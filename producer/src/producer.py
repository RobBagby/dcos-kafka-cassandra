"""Module for event producer"""
import os
import time
import random
import datetime
import sys
from kafka import KafkaProducer
from machinetemperature import MachineTemperature
from log import Log

ADVERTISED_HOST = os.getenv('ADVERTISED_HOST')
ADVERTISED_PORT = os.getenv('ADVERTISED_PORT')
KAFKA_URI = ADVERTISED_HOST + ':' + ADVERTISED_PORT

SENSOR_TEMPERATURE_TOPIC = os.getenv('SENSOR_TEMPERATURE_TOPIC')

PUBLISH_DELAY_IN_SECONDS = float(os.getenv('PUBLISH_DELAY_IN_SECONDS'))
PUBLISH_NUMBER_OF_SENSORS = int(os.getenv('PUBLISH_NUMBER_OF_SENSORS'))

APPLICATION_LOGGING_LEVEL = os.getenv('APPLICATION_LOGGING_LEVEL')
LOGGER = Log()

def simulate():
    """simulate temperature events for machines"""

    LOGGER.setLevel(APPLICATION_LOGGING_LEVEL)
    LOGGER.debug("Starting producer")
    LOGGER.debug('Set Logging Level to ' + APPLICATION_LOGGING_LEVEL)
    LOGGER.debug('Writing to Kafka listening at: ' + KAFKA_URI)

    producer = KafkaProducer(bootstrap_servers=KAFKA_URI)

    last_temperatures = {}

    while True:
        for i in range(PUBLISH_NUMBER_OF_SENSORS):
            sensor = 'sensor' + str(i)
            temperature = _get_temperature(sensor, last_temperatures)
            message = MachineTemperature(sensor, temperature, datetime.datetime.utcnow()).to_json()

            producer.send(SENSOR_TEMPERATURE_TOPIC, str.encode(message), key=sensor.encode())

        LOGGER.debug(str(PUBLISH_NUMBER_OF_SENSORS) + " messages published")
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
    try:
        simulate()
    except:
        e = sys.exc_info()[0]
        LOGGER.error("Unable to simulate logging", exc_info=True)
