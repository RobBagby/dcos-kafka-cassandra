"""Module for lagreader"""
import os
import datetime
import requests
from kafka import KafkaConsumer
from log import Log
from partitionlag import PartitionLag
from partitionlagdict import PartitionLagDict
from lagevent import LagEvent
from cassandraclient import CassandraClient

ADVERTISED_HOST = os.getenv('ADVERTISED_HOST')
ADVERTISED_PORT = os.getenv('ADVERTISED_PORT')
KAFKA_URI = ADVERTISED_HOST + ':' + ADVERTISED_PORT

CASSANDRA_ADDRESS = os.getenv('CASSANDRA_ADDRESS')
CASSANDRA_PORT = os.getenv('CASSANDRA_PORT')
CASSANDRA_KEYSPACE = 'sensors'

APPLICATION_LOGGING_LEVEL = os.getenv('APPLICATION_LOGGING_LEVEL')

LAG_DELAY_IN_SECONDS = int(os.getenv('LAG_DELAY_IN_SECONDS'))

LOGGER = Log()

def initialize(session):
    cassandraclient = CassandraClient()
    cassandraclient.createKeySpace(session, CASSANDRA_KEYSPACE)
    cassandraclient.create_latest_lag(session, CASSANDRA_KEYSPACE)

def consume():
    """Consumes events from partitionlag topic"""
    LOGGER.setLevel(APPLICATION_LOGGING_LEVEL)
    LOGGER.info("Starting lagreader")
    LOGGER.debug('Set Logging Level to ' + APPLICATION_LOGGING_LEVEL)
    LOGGER.debug('Listening on Kafka at: ' + KAFKA_URI)
    LOGGER.debug('Writing to Cassandra at: ' + CASSANDRA_ADDRESS + ":" + CASSANDRA_PORT)

    cassandraclient = CassandraClient()
    session = cassandraclient.getConnection(CASSANDRA_ADDRESS, CASSANDRA_PORT)
    initialize(session)

    consumer = KafkaConsumer(group_id='lagConsumerGroup', bootstrap_servers=KAFKA_URI)
    consumer.subscribe(topics=['partitionlag'])
    partition_lag_dict = PartitionLagDict()

    last_writetime = datetime.datetime.now()

    for msg in consumer:
        jsonstring = msg.value
        partitionlag = PartitionLag.from_json(jsonstring)
        partition_lag_dict.addPartitionLag(partitionlag)
        LOGGER.debug(str(partitionlag.eventdate) + "  Received partitionlag event: " \
            + "partition: " + str(partitionlag.partition) \
            + " lag: " + str(partitionlag.lag))
        LOGGER.debug(str(datetime.datetime.now()) + ' Received partitionlag: ' \
            + partition_lag_dict.toString())

        last_writetime = _notifylag_conditionally(session, partition_lag_dict, last_writetime)

def _notifylag_conditionally(session, partition_lag_dict, last_writetime):
    currtime = datetime.datetime.now()
    delta = currtime - last_writetime

    if delta.seconds >= LAG_DELAY_IN_SECONDS:
        _notifylag(session, partition_lag_dict)
        return currtime

    return last_writetime

def _notifylag(session, partition_lag_dict):
    LOGGER.info(str(datetime.datetime.now()) + 'Notifying Lag:' + partition_lag_dict.toString())
    vamp_uri = os.getenv('VAMP_URI')
    notify_vamp = _str2bool(os.getenv('NOTIFY_VAMP'))
    average_of_last_x = int(os.getenv('LAG_AVERAGE_OF_LAST_X'))

    average_lag = partition_lag_dict.getAverageLag(average_of_last_x)

    cassandraclient = CassandraClient()
    cassandraclient.update_latest_lag(session, CASSANDRA_KEYSPACE, average_lag, \
            datetime.datetime.now())

    if notify_vamp:
        headers = {'Content-Type':'application/json'}

        lag_event = LagEvent(average_lag)
        response = requests.post(vamp_uri, headers=headers, data=lag_event.to_json())
        LOGGER.info(str(datetime.datetime.now()) + 'wrote lag event ' + response.text)


def _str2bool(v):
      return v.lower() in ("yes", "true", "t", "1")

if __name__ == "__main__":
    try:
        consume()
    except:
        e = sys.exc_info()[0]
        LOGGER.error("Unable to consume events", exc_info=True)