import os
import time
import datetime
from kafka import KafkaConsumer
from kafka.structs import TopicPartition
from partitionlag import PartitionLag
from partitionlagdict import PartitionLagDict

print('Starting lagreader')
ADVERTISED_HOST = os.getenv('ADVERTISED_HOST')
ADVERTISED_PORT = os.getenv('ADVERTISED_PORT')
KAFKA_URI = ADVERTISED_HOST + ':' + ADVERTISED_PORT
print('KAFKA_URI', KAFKA_URI)

consumer = KafkaConsumer(group_id='lagConsumerGroup', bootstrap_servers=KAFKA_URI)
consumer.subscribe(topics=['partitionlag'])
starttime = datetime.datetime.now()
partitionLagDict = PartitionLagDict()
# partitionLags = {}

for msg in consumer:
    jsonString = msg.value
    pl = PartitionLag.from_json(jsonString)
    partitionLagDict.addPartitionLag(pl)
    print("partition: ", pl.partition, " lag: ", str(pl.lag))
    print(partitionLagDict.toString())