import json
import time
import argparse
import pprint
from datetime import datetime
from kafka import KafkaProducer
from kafka import KafkaConsumer

# 터미널 출력용
def topic_to_tm(consumer):
    print('터미널 출력')

    # Read data from kafka
    try :
        for message in consumer:
            print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                message.offset, message.key,
                                                message.value))
    except KeyboardInterrupt :
        print('\r\n Output to Terminal - interrupted!')
        return

# Kafka Topic로부터 데이터 취득
def get_kafka_topic():
    # Initialize consumer variable and set property for JSON decode
    consumer = KafkaConsumer ('topic-11',
                        bootstrap_servers = ['broker:29092'],
                        value_deserializer=lambda m: json.loads(m.decode('utf-8')))

    print(consumer)
    return consumer


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Kafka에서IoT기기등 Stream데이터 취득')
    parser.add_argument('--mode', type=str, default='tm', help='tm(터미널 출력)')
    args = parser.parse_args()

    start = time.time()

    consumer = get_kafka_topic()
    topic_to_tm(consumer)

    making_time = time.time() - start

    print("")
    print("Stream데이터취득 대기시간:{0}".format(making_time) + " [sec]")
    print("")