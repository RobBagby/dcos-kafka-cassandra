"""Module for event consumer"""
import os
import sys
import time
import datetime
from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.structs import TopicPartition
from partitionlag import PartitionLag
from log import Log
from cassandraclient import CassandraClient
from machinetemperature import MachineTemperature

print('Starting simpleconsumer')
ADVERTISED_HOST = os.getenv('ADVERTISED_HOST')
ADVERTISED_PORT = os.getenv('ADVERTISED_PORT')
KAFKA_URI = ADVERTISED_HOST + ':' + ADVERTISED_PORT
print('KAFKA_URI', KAFKA_URI)

SENSOR_TEMPERATURE_TOPIC = os.getenv('SENSOR_TEMPERATURE_TOPIC')

CONSUMER_READ_DELAY_FACTOR = float(os.getenv('CONSUMER_READ_DELAY_FACTOR'))
CONSUMER_NUM_MESSAGES_TO_WRITE_LAG = int(os.getenv('CONSUMER_NUM_MESSAGES_TO_WRITE_LAG'))
CONSUMER_NUM_SECONDS_TO_WRITE_LAG = float(os.getenv('CONSUMER_NUM_SECONDS_TO_WRITE_LAG'))

CASSANDRA_ADDRESS = os.getenv('CASSANDRA_ADDRESS')
CASSANDRA_PORT = os.getenv('CASSANDRA_PORT')
CASSANDRA_KEYSPACE = 'sensors'

PUBLISH_NUMBER_OF_SENSORS = int(os.getenv('PUBLISH_NUMBER_OF_SENSORS'))
PUBLISH_DELAY_IN_SECONDS = int(os.getenv('PUBLISH_DELAY_IN_SECONDS'))

APPLICATION_LOGGING_LEVEL = os.getenv('APPLICATION_LOGGING_LEVEL')
LOGGER = Log()

def initialize(session):
    cassandraclient = CassandraClient()
    cassandraclient.createKeySpace(session, CASSANDRA_KEYSPACE)
    cassandraclient.createTemperatureByDayTable(session, CASSANDRA_KEYSPACE)

def consume():
    """Consumes events from SENSOR_TEMPERATURE_TOPIC topic"""
    LOGGER.setLevel(APPLICATION_LOGGING_LEVEL)
    LOGGER.info("Starting consumer")
    LOGGER.debug('Set Logging Level to ' + APPLICATION_LOGGING_LEVEL)
    LOGGER.debug('Listening on Kafka at: ' + KAFKA_URI)
    LOGGER.debug('Writing to Cassandra at: ' + CASSANDRA_ADDRESS + ":" + CASSANDRA_PORT)

    cassandraclient = CassandraClient()
    session = cassandraclient.getConnection(CASSANDRA_ADDRESS, CASSANDRA_PORT)
    initialize(session)

    consumer = KafkaConsumer(group_id='sensortempgroup', bootstrap_servers=KAFKA_URI)
    producer = KafkaProducer(bootstrap_servers=KAFKA_URI)

    consumer.subscribe(topics=[SENSOR_TEMPERATURE_TOPIC])
    last_readtime = datetime.datetime.now()
    lagcounter = 0

    published_items_per_sec = float(PUBLISH_NUMBER_OF_SENSORS) / float(PUBLISH_DELAY_IN_SECONDS)
    consumed_items_per_sec = published_items_per_sec / float(CONSUMER_READ_DELAY_FACTOR)
    consumer_delay = 1 / consumed_items_per_sec

    for msg in consumer:
        tp = TopicPartition(msg.topic, msg.partition)
        highwater = consumer.highwater(tp)

        machinetemp = MachineTemperature.from_json(msg.value)
        LOGGER.debug('Inserting record for machineid: ' + machinetemp.machineid \
            + '; temperature: ' + str(machinetemp.temperature) \
            + '; datetime: ' + str(machinetemp.eventdate))
        cassandraclient.addSensorReading(session, CASSANDRA_KEYSPACE, machinetemp.machineid, \
            machinetemp.eventdate, machinetemp.temperature)

        if highwater is None:
            LOGGER.warning('Highwater was none, resubscribing to topic')
            consumer.unsubscribe()
            consumer.subscribe(topics=[SENSOR_TEMPERATURE_TOPIC])

        delta = datetime.datetime.now() - last_readtime
        if (delta.seconds >= CONSUMER_NUM_SECONDS_TO_WRITE_LAG \
            or lagcounter >= CONSUMER_NUM_MESSAGES_TO_WRITE_LAG) \
            and highwater is not None:

            LOGGER.debug("delta.seconds: " + str(delta.seconds) \
                + "CONSUMER_NUM_SECONDS_TO_WRITE_LAG: " + str(CONSUMER_NUM_SECONDS_TO_WRITE_LAG) \
                + " lagcounter: " + str(lagcounter) \
                + "CONSUMER_NUM_MESSAGES_TO_WRITE_LAG" + str(CONSUMER_NUM_MESSAGES_TO_WRITE_LAG) \
                + "\n")


            lag = (highwater - 1) - msg.offset
            partitionlag = PartitionLag(msg.partition, lag)
            LOGGER.info('Sending partition lag event.  Lag: ' + str(partitionlag.lag) \
                + ' partition: ' + str(partitionlag.partition) + '\n')
            producer.send('partitionlag', str.encode(partitionlag.to_json()))

            lagcounter = 0
            last_readtime = datetime.datetime.now()

        time.sleep(consumer_delay)

        lagcounter = lagcounter + 1

if __name__ == "__main__":
    try:
        consume()
    except:
        e = sys.exc_info()[0]
        LOGGER.error("Unable to consume events", exc_info=True)
