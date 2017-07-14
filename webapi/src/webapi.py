import os
import json
from flask import Flask, render_template
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api
from cassandraclient import CassandraClient
from alert import Alert, Alerts, WebViewData, CustomJsonEncoder
from log import Log
import time

app = Flask(__name__)
CORS(app)
api = Api(app)

CASSANDRA_ADDRESS = os.getenv('CASSANDRA_ADDRESS')
CASSANDRA_PORT = os.getenv('CASSANDRA_PORT')
CASSANDRA_KEYSPACE = 'sensors'

APPLICATION_LOGGING_LEVEL = os.getenv('APPLICATION_LOGGING_LEVEL')
LOGGER = Log()
LOGGER.setLevel(APPLICATION_LOGGING_LEVEL)
LOGGER.info("Starting consumer")
LOGGER.info('Writing to Cassandra at: ' + CASSANDRA_ADDRESS + ":" + CASSANDRA_PORT)

class QueueAPI(Resource):

    # @app.route("/")
    # def hello():
    #     return render_template('index.html')

    def get(self, queue_id):
        """Get details of a queue. 
        """

        cassandraclient = CassandraClient()
        session = cassandraclient.getConnection(CASSANDRA_ADDRESS, CASSANDRA_PORT)
        self._initialize(session)
        
        wvd = WebViewData()

        alerts = self.get_last_alerts(session)
        wvd.last_alerts = alerts
        # if not queue_id:
        #     queue_id = config.AZURE_STORAGE_QUEUE_NAME

        # queue = self.getMessageQueue(queue_id)
        # length = self.queue.getLength()
        # duration = self.getTableService().getLastProcessingTime()
        
        # resp = {
        #     'queue_name': queue_id,
        #     'queue_length': length,
        #     'last_duration': duration,
        #     'time': time.strftime("%H:%M")
        #     }
        resp = json.dumps(wvd, cls=CustomJsonEncoder)
        # print('resp', alerts.to_json())
        # resp = {'test': 'fred'}
        return resp
    
    def get_last_alerts(self, session):
        cassandraclient = CassandraClient()
        rows = cassandraclient.get_last_alerts(session, CASSANDRA_KEYSPACE)
        alerts = Alerts()
        for row in rows:
            print(row.sensor_id, ' ', row.temperature)
            alerts.append(Alert(row.sensor_id, row.event_date, row.event_time, row.temperature))

        return alerts
    # def getTableService(self):
    #     return SummaryTable(config.AZURE_STORAGE_ACCOUNT_NAME, config.AZURE_STORAGE_ACCOUNT_KEY, config.AZURE_STORAGE_SUMMARY_TABLE_NAME)
    
    # def getMessageQueue(self, queue_id):
    #     self.queue = Queue(account_name = config.AZURE_STORAGE_ACCOUNT_NAME, account_key=config.AZURE_STORAGE_ACCOUNT_KEY, queue_name=queue_id)

    def _initialize(self, session):
        cassandraclient = CassandraClient()
        cassandraclient.createKeySpace(session, CASSANDRA_KEYSPACE)
        cassandraclient.createTemperatureByDayTable(session, CASSANDRA_KEYSPACE)
        cassandraclient.createLastAlertPerSensorTable(session, CASSANDRA_KEYSPACE)

api.add_resource(QueueAPI, '/queue',
                 '/queue/<string:queue_id>')

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
