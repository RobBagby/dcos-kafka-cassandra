"""Module for CassandraClient"""
import datetime
import os
from cassandra.cluster import Cluster
from log import Log

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
        if self._table_exists(session, keyspace, 'temperature_by_day'):
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

    def createLastAlertPerSensorTable(self, session, keyspace):
        if self._table_exists(session, keyspace, 'last_alert_per_sensor'):
            LOGGER.info('Table last_alert_per_sensor exists')
        else:
            LOGGER.info('Creating table last_alert_per_sensor')
            try:
                session.execute("""
                    CREATE TABLE IF NOT EXISTS %s.last_alert_per_sensor (
                        sensor_id text,
                        event_date text,
                        event_time timestamp,
                        temperature int,
                        PRIMARY KEY (sensor_id)
                    );
                    """ % keyspace)
            except Exception as e:
                LOGGER.error("Unable to create table last_alert_per_sensor")
                LOGGER.error(e)

    def create_latest_lag(self, session, keyspace):
        if self._table_exists(session, keyspace, 'latest_lag'):
            LOGGER.info('Table latest_lag exists')
        else:
            LOGGER.info('Creating table latest_lag')
            try:
                session.execute("""
                    CREATE TABLE IF NOT EXISTS %s.latest_lag (
                        lagid text,
                        lag float,
                        event_time timestamp,
                        PRIMARY KEY (lagid)
                    );
                    """ % keyspace)
            except Exception as e:
                LOGGER.error("Unable to create table latest_lag")
                LOGGER.error(e)

    def _table_exists(self, session, keyspace, tablename):
        query = """SELECT table_name FROM system_schema.tables WHERE keyspace_name='%s' AND table_name='%s';""" % (keyspace, tablename)
        LOGGER.debug('Running the following query ' + query)

        try:
            rows = session.execute(query)
            if not rows:
                return False
            return True
        except Exception as e:
            LOGGER.error('Error seraching for ' + tablename + ' table')
            LOGGER.error(e)

    def add_sensor_rating(self, session, keyspace, sensorId, eventDatetime, temperature):
        eventdate = eventDatetime.strftime("%Y%m%d")
        eventTimestamp = eventDatetime.strftime("%Y-%m-%d %H:%M:%S")

        query = """INSERT INTO %s.temperature_by_day(sensor_id, event_date, event_time, temperature) VALUES('%s', '%s', '%s', %s);""" % (keyspace, sensorId, eventdate, eventTimestamp, temperature)

        try:
            session.execute(query)
        except Exception as exc:
            LOGGER.error("Unable to insert into table temperature_by_day")
            LOGGER.error(exc)


    def update_latest_lag(self, session, keyspace, lag, eventDatetime):
        eventTimestamp = eventDatetime.strftime("%Y-%m-%d %H:%M:%S")

        query = """UPDATE %s.latest_lag SET lag = %s, event_time = '%s' WHERE lagid = 'sensors';""" % (keyspace, lag, eventTimestamp)

        try:
            session.execute(query)
        except Exception as exc:
            LOGGER.error("Unable to insert into table temperature_by_day")
            LOGGER.error(exc)

    def add_last_alert_per_sensor(self, session, keyspace, sensor_id, eventDatetime, temperature):
        existing_rows = self._get_last_alert_for_sensor(session, keyspace, sensor_id)
        if existing_rows:
            if existing_rows[0].event_time > eventDatetime:
                return

        eventdate = eventDatetime.strftime("%Y%m%d")
        eventTimestamp = eventDatetime.strftime("%Y-%m-%d %H:%M:%S")

        query = """INSERT INTO %s.last_alert_per_sensor(sensor_id, event_date, event_time, temperature) VALUES('%s', '%s', '%s', %s);""" % (keyspace, sensor_id, eventdate, eventTimestamp, temperature)

        try:
            session.execute(query)
        except Exception as exc:
            LOGGER.error("Unable to insert into table last_alert_per_sensor")
            LOGGER.error(exc)

    def _get_last_alert_for_sensor(self, session, keyspace, sensor_id):
        query = """SELECT sensor_id, event_date, event_time, temperature FROM %s.last_alert_per_sensor where sensor_id = '%s';""" % (keyspace, sensor_id)

        try:
            rows = session.execute(query)
            return rows
        except Exception as exc:
            LOGGER.error("Error selecting from last_alert_per_sensor")
            LOGGER.error(exc)

    def get_last_alerts(self, session, keyspace):
        query = """SELECT sensor_id, event_date, event_time, temperature FROM %s.last_alert_per_sensor LIMIT 10;""" % (keyspace)

        try:
            rows = session.execute(query)
            return rows
        except Exception as exc:
            LOGGER.error("Error returning get_last_alerts")
            LOGGER.error(exc)

    def get_latest_lag(self, session, keyspace):
        query = """SELECT lag, event_time FROM %s.latest_lag WHERE lagid = 'sensors';""" % (keyspace)

        try:
            rows = session.execute(query)
            return rows
        except Exception as exc:
            LOGGER.error("Error returning latest_lag")
            LOGGER.error(exc)

    def getLastTenSensorReadings(self, session, keyspace):
        query = """SELECT sensor_id, event_date, event_time, temperature FROM %s.temperature_by_day LIMIT 10;""" % keyspace

        try:
            rows = session.execute(query)
            return rows
        except Exception as e:
            LOGGER.error("Error returning last 10 records from table temperature_by_day")
            LOGGER.error(e)


