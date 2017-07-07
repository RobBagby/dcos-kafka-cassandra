"""Module for lagreader"""
import os
from kafka import KafkaConsumer
from log import Log
from partitionlag import PartitionLag
from partitionlagdict import PartitionLagDict

ADVERTISED_HOST = os.getenv('ADVERTISED_HOST')
ADVERTISED_PORT = os.getenv('ADVERTISED_PORT')
KAFKA_URI = ADVERTISED_HOST + ':' + ADVERTISED_PORT

APPLICATION_LOGGING_LEVEL = os.getenv('APPLICATION_LOGGING_LEVEL')
LOGGER = Log()

def consume():
    """Consumes events from partitionlag topic"""
    LOGGER.setLevel(APPLICATION_LOGGING_LEVEL)
    LOGGER.info("Starting lagreader")
    LOGGER.debug('Set Logging Level to ' + APPLICATION_LOGGING_LEVEL)
    LOGGER.debug('Listening on Kafka at: ' + KAFKA_URI)

    consumer = KafkaConsumer(group_id='lagConsumerGroup', bootstrap_servers=KAFKA_URI)
    consumer.subscribe(topics=['partitionlag'])
    partition_lag_dict = PartitionLagDict()

    for msg in consumer:
        jsonstring = msg.value
        partitionlag = PartitionLag.from_json(jsonstring)
        partition_lag_dict.addPartitionLag(partitionlag)
        LOGGER.info(str(partitionlag.eventdate) + "  Received partitionlag event: " \
            + "partition: " + str(partitionlag.partition) \
            + " lag: " + str(partitionlag.lag))
        LOGGER.info(partition_lag_dict.toString())

if __name__ == "__main__":
    try:
        consume()
    except:
        e = sys.exc_info()[0]
        LOGGER.error("Unable to consume events", exc_info=True)