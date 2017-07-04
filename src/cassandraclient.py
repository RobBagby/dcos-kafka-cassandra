"""Module for CassandraClient"""
import datetime
import os
from cassandra.cluster import Cluster
from log import Log

# log = logging.getLogger()
# log.setLevel('INFO')
# handler = logging.StreamHandler()
# handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
# log.addHandler(handler)

# from cassandra import ConsistencyLevel

# from cassandra.query import SimpleStatement

# cluster = Cluster(contact_points=['localcassandra'],port=9042)
# session = cluster.connect()

APPLICATION_LOGGING_LEVEL = os.getenv('APPLICATION_LOGGING_LEVEL')
LOGGER = Log()

class CassandraClient:
    def getConnection(self, ip, port):
        cluster = Cluster(contact_points=[ip], port=port)
        session = cluster.connect()
        return session
        
    def createKeySpace(self, session, keyspace):
        LOGGER.info("Creating keyspace...")
        try:
            session.execute("""
                CREATE KEYSPACE IF NOT EXISTS %s
                WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '2' }
                """ % keyspace)
    
            LOGGER.info('created keyspace ' + keyspace)

        except Exception as e:
            LOGGER.error("Unable to create keyspace")
            LOGGER.error(e)

    def createTemperatureByDayTable(self, session, keyspace):
        if self._temperatureByDayTableExists(session, keyspace):
            LOGGER.info('Table temperature_by_day exists')
        else:
            LOGGER.info('Creating table temperature_by_day')
            try:
                session.execute("""
                    CREATE TABLE IF NOT EXISTS %s.temperature_by_day (
                        sensor_id text,
                        event_date text,
                        event_time timestamp,
                        temperature int,
                        PRIMARY KEY ((sensor_id, event_date), event_time)
                    ) WITH CLUSTERING ORDER BY (event_time DESC)
                    """ % keyspace)
            except Exception as e:
                LOGGER.error("Unable to create table temperature_by_day")
                LOGGER.error(e)
    def _temperatureByDayTableExists(self, session, keyspace):
        query = """SELECT table_name FROM system_schema.tables WHERE keyspace_name='%s';""" % (keyspace)
        LOGGER.debug('Running the following query ' + query)

        try:
            rows = session.execute(query)
            if not rows:
                return False
            return True
        except Exception as e:
            LOGGER.error("Error seraching for temperature_by_day table")
            LOGGER.error(e)

    def addSensorReading(self, session, keyspace, sensorId, eventDatetime, temperature):
        eventDate = eventDatetime.strftime("%Y%m%d")
        eventTimestamp = eventDatetime.strftime("%Y-%m-%d %H:%M:%S")

        query = """INSERT INTO %s.temperature_by_day(sensor_id, event_date, event_time, temperature) VALUES('%s', '%s', '%s', %s);""" % (keyspace, sensorId, eventDate, eventTimestamp, temperature)

        try:
            session.execute(query)
        except Exception as e:
            LOGGER.error("Unable to insert into table temperature_by_day")
            LOGGER.error(e)

    def getLastTenSensorReadings(self, session, keyspace):
        query = """SELECT sensor_id, event_date, event_time, temperature FROM %s.temperature_by_day;""" % keyspace

        try:
            rows = session.execute(query)
            return rows
        except Exception as e:
            LOGGER.error("Error returning last 10 records from table temperature_by_day")
            LOGGER.error(e)


