import os
import sys
import time
import datetime
from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.structs import TopicPartition
from partitionlag import PartitionLag
# sys.path.append(os.path.expanduser('../../libs'))
# from partitions.partitionlag import PartitionLag

print('Starting simpleconsumer')
ADVERTISED_HOST = os.getenv('ADVERTISED_HOST')
ADVERTISED_PORT = os.getenv('ADVERTISED_PORT')
KAFKA_URI = ADVERTISED_HOST + ':' + ADVERTISED_PORT
print('KAFKA_URI', KAFKA_URI)

CONSUMER_READ_DELAY_IN_SECONDS = float(os.getenv('CONSUMER_READ_DELAY_IN_SECONDS'))
CONSUMER_NUM_MESSAGES_TO_WRITE_LAG = int(os.getenv('CONSUMER_NUM_MESSAGES_TO_WRITE_LAG'))
CONSUMER_NUM_SECONDS_TO_WRITE_LAG = float(os.getenv('CONSUMER_NUM_SECONDS_TO_WRITE_LAG'))

consumer = KafkaConsumer(group_id='sensortempgroup', bootstrap_servers=KAFKA_URI)
producer = KafkaProducer(bootstrap_servers=KAFKA_URI)

consumer.subscribe(topics=['sensortemp'])
last_readtime = datetime.datetime.now()
counter = 0

for msg in consumer:
    tp = TopicPartition(msg.topic, msg.partition)
    highwater = consumer.highwater(tp)

    # print("date: " + str(msg) + " partition: " + str(msg.partition)  + "; highwater: " + str(highwater) + " lag: " + str(lag) + "; offset: " + str(msg.offset))
    
    if highwater is None:
        print("None: partition: ", msg.partition, " value: ", msg.value)
        consumer.unsubscribe()
        consumer.subscribe(topics=['sensortemp'])
    delta = datetime.datetime.now() - last_readtime
    if (delta.seconds >= CONSUMER_NUM_SECONDS_TO_WRITE_LAG or counter >= CONSUMER_NUM_MESSAGES_TO_WRITE_LAG) and highwater is not None:
        print("delta.seconds: ", str(delta.seconds), "CONSUMER_NUM_SECONDS_TO_WRITE_LAG: ", str(CONSUMER_NUM_SECONDS_TO_WRITE_LAG), " counter: ", str(counter), "CONSUMER_NUM_MESSAGES_TO_WRITE_LAG", str(CONSUMER_NUM_MESSAGES_TO_WRITE_LAG))
        # print('fred')
        if highwater is None:
            print('highwater none')

        lag = (highwater - 1) - msg.offset
        pl = PartitionLag(msg.partition, lag)
        print("lag: ", pl.lag, " partition: ", pl.partition)
        producer.send('partitionlag', str.encode(pl.to_json()))
        counter = 0
        last_readtime = datetime.datetime.now()
        
    print('pre')
    time.sleep(CONSUMER_READ_DELAY_IN_SECONDS)
    print('post')
    counter = counter + 1

print('No messages')
