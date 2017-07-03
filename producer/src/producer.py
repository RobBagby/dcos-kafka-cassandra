import os
import time
import random
import datetime
import sys
from kafka import KafkaProducer
from machinetemperature import MachineTemperature

ADVERTISED_HOST = os.getenv('ADVERTISED_HOST')
ADVERTISED_PORT = os.getenv('ADVERTISED_PORT')
KAFKA_URI = ADVERTISED_HOST + ':' + ADVERTISED_PORT

PUBLISH_DELAY_IN_SECONDS = float(os.getenv('PUBLISH_DELAY_IN_SECONDS'))
PUBLISH_NUMBER_OF_SENSORS = int(os.getenv('PUBLISH_NUMBER_OF_SENSORS'))

def simulate():
    """simulate temperature events for machines"""
    print('Starting producer')
    print('Writing to Kafka listening at: ', KAFKA_URI)

    producer = KafkaProducer(bootstrap_servers=KAFKA_URI)

    last_temperatures = {}

    while True:
        for i in range(PUBLISH_NUMBER_OF_SENSORS):
            sensor = 'sensor' + str(i)
            temperature = _get_temperature(sensor, last_temperatures)
            message = MachineTemperature(sensor, temperature, datetime.datetime.utcnow()).to_json()
            # message = 'Message: ' + time.ctime()
            # print('sending message', message, ", key: ", i)
            producer.send('sensortemp', str.encode(message), key=sensor.encode())

        print(str(PUBLISH_NUMBER_OF_SENSORS) + " messages published")
        time.sleep(PUBLISH_DELAY_IN_SECONDS)

def _get_temperature(sensorid, last_temperatures):
    """
    Gets the last value for a temperature, changes it by 1,
    stores the value and returns the new temp
    """
    temperature = 70
    if sensorid in last_temperatures:
        temperature = last_temperatures[sensorid]

    change = random.randint(-1, 1)
    temperature += change

    last_temperatures[sensorid] = temperature

    return temperature

if __name__ == "__main__":
    # log = Log()
    # log.debug("Started to simulate logs")
    try:
        simulate()
    except:
        print("error")
        e = sys.exc_info()[0]
        print(e)
    #   hostname = socket.gethostname()
    #   log.error("Unable to simulate logging", exc_info=True)
    #   notify.error(hostname + ": ACS Logging simulation failed")
    #   mailhandler.send(hostname + ": ACS Logging simulation failed", "Check logs on " + hostname + " for details")