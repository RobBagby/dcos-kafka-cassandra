"""Module for event consumer"""
import os
import sys
import time
import datetime
from log import Log
from cassandraclient import CassandraClient
import cassandra

CASSANDRA_ADDRESS = os.getenv('CASSANDRA_ADDRESS')
CASSANDRA_PORT = os.getenv('CASSANDRA_PORT')
CASSANDRA_KEYSPACE = 'test'

LOGGER = Log()

def initialize(session):
    """creates keyspace and creates table"""
    cassandraclient = CassandraClient()
    cassandraclient.createKeySpace(session, CASSANDRA_KEYSPACE)
    cassandraclient.createTemperatureByDayTable(session, CASSANDRA_KEYSPACE)
    cassandraclient.createLastAlertPerSensorTable(session, CASSANDRA_KEYSPACE)

def readwritetest():
    """Consumes events from SENSOR_TEMPERATURE_TOPIC topic"""
    LOGGER.setLevel('INFO')
    LOGGER.debug('Starting cassandratester')
    LOGGER.debug('Set Logging Level to ' + 'INFO')
    LOGGER.debug('Writing to Cassandra at: ' + CASSANDRA_ADDRESS + ":" + CASSANDRA_PORT)
    try:
        cassandraclient = CassandraClient()
        session = cassandraclient.getConnection(CASSANDRA_ADDRESS, CASSANDRA_PORT)
        initialize(session)

        while True:
            cassandraclient.add_sensor_rating(session, CASSANDRA_KEYSPACE, \
                'sensor1', datetime.datetime.now(), 72)

            rows = cassandraclient.getLastTenSensorReadings(session, CASSANDRA_KEYSPACE)
            LOGGER.info('Writing last 10 records')
            for row in rows:
                LOGGER.info('time: ' + str(row.event_time) \
                    + '   sensorid: ' + row.sensor_id + '  temperature' + str(row.temperature))
            LOGGER.info('\n')

            time.sleep(3)
    except cassandra.cluster.NoHostAvailable:
        LOGGER.info('Could not reach Cassandra Server retrying...')
        time.sleep(3)
        readwritetest()

if __name__ == "__main__":
    try:
        readwritetest()
    except:
        e = sys.exc_info()[0]
        LOGGER.info('exception type: ' + str(type(e)))
        e = sys.exc_info()[0]
        LOGGER.error('Unable to consume events', exc_info=True)
