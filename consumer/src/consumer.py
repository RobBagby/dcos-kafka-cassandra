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

CONSUMER_READ_DELAY_IN_SECONDS = float(os.getenv('CONSUMER_READ_DELAY_IN_SECONDS'))
CONSUMER_NUM_MESSAGES_TO_WRITE_LAG = int(os.getenv('CONSUMER_NUM_MESSAGES_TO_WRITE_LAG'))
CONSUMER_NUM_SECONDS_TO_WRITE_LAG = float(os.getenv('CONSUMER_NUM_SECONDS_TO_WRITE_LAG'))

CASSANDRA_ADDRESS = os.getenv('CASSANDRA_ADDRESS')
CASSANDRA_PORT = os.getenv('CASSANDRA_PORT')
CASSANDRA_KEYSPACE = 'sensors'

# session = getConnection('localcassandra', 9042)




# createKeySpace('mykeyspace');
# rows = getLastTenSensorReadings(session, 'test1')
# for row in rows:
#     print(row.sensor_id, row.event_date, row.event_time, row.temperature)
APPLICATION_LOGGING_LEVEL = os.getenv('APPLICATION_LOGGING_LEVEL')
LOGGER = Log()

def initialize(session):
    cassandraclient = CassandraClient()
    cassandraclient.createKeySpace(session, CASSANDRA_KEYSPACE)
    cassandraclient.createTemperatureByDayTable(session, CASSANDRA_KEYSPACE)

def consume():
    """Consumes events from sensortemp topic"""
    LOGGER.setLevel(APPLICATION_LOGGING_LEVEL)
    LOGGER.debug("Starting consumer")
    LOGGER.debug('Set Logging Level to ' + APPLICATION_LOGGING_LEVEL)
    LOGGER.debug('Listening on Kafka at: ' + KAFKA_URI)

    cassandraclient = CassandraClient()
    session = cassandraclient.getConnection(CASSANDRA_ADDRESS, CASSANDRA_PORT)
    initialize(session)
    print('I got here')
    consumer = KafkaConsumer(group_id='sensortempgroup', bootstrap_servers=KAFKA_URI)
    producer = KafkaProducer(bootstrap_servers=KAFKA_URI)

    consumer.subscribe(topics=['sensortemp'])
    last_readtime = datetime.datetime.now()
    counter = 0

    for msg in consumer:
        tp = TopicPartition(msg.topic, msg.partition)
        highwater = consumer.highwater(tp)

        
        machinetemp = MachineTemperature.from_json(msg.value)
        LOGGER.debug('Inserting record for machineid: ' + machinetemp.machineid)
        cassandraclient.addSensorReading(session, CASSANDRA_KEYSPACE, machinetemp.machineid, machinetemp.eventdate, machinetemp.temperature)
        # LOGGER.debug("Message Value")
        # LOGGER.debug(msg.value)
        # machinetemp = MachineTemperature.from_json(msg.value)

        # LOGGER.debug('Machine id: ' + machinetemp.machineid + '; temperature: ' + str(machinetemp.temperature))
        
        # # cassandraclient.addSensorReading(session, CASSANDRA_KEYSPACE, 'sensor1', datetime.datetime.now(), '72F')

        # print("date: " + str(msg) + " partition: " + str(msg.partition)  + "; highwater: " + str(highwater) + " lag: " + str(lag) + "; offset: " + str(msg.offset))
        
        if highwater is None:
            LOGGER.debug('Highwater was none, resubscribing to topic')
            consumer.unsubscribe()
            consumer.subscribe(topics=['sensortemp'])

        delta = datetime.datetime.now() - last_readtime
        if (delta.seconds >= CONSUMER_NUM_SECONDS_TO_WRITE_LAG \
            or counter >= CONSUMER_NUM_MESSAGES_TO_WRITE_LAG) \
            and highwater is not None:

            LOGGER.debug("delta.seconds: " + str(delta.seconds) \
                + "CONSUMER_NUM_SECONDS_TO_WRITE_LAG: " + str(CONSUMER_NUM_SECONDS_TO_WRITE_LAG) \
                + " counter: " + str(counter) \
                + "CONSUMER_NUM_MESSAGES_TO_WRITE_LAG" + str(CONSUMER_NUM_MESSAGES_TO_WRITE_LAG))

            lag = (highwater - 1) - msg.offset
            partitionlag = PartitionLag(msg.partition, lag)
            LOGGER.debug('Sending partition lag event.  Lag: ' + str(partitionlag.lag) \
                + ' partition: ' + str(partitionlag.partition))
            producer.send('partitionlag', str.encode(partitionlag.to_json()))

            counter = 0
            last_readtime = datetime.datetime.now()

        time.sleep(CONSUMER_READ_DELAY_IN_SECONDS)
        counter = counter + 1


if __name__ == "__main__":
    try:
        consume()
    except:
        e = sys.exc_info()[0]
        LOGGER.error("Unable to consume events", exc_info=True)
