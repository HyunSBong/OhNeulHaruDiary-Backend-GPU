from kafka import KafkaConsumer
from kafka import KafkaProducer
from json import dumps
from json import loads
import json

brokers = ["localhost:9091"] # "docker internal => kafka1:19091"
class KafkaConnector:
    def Kafka_Producer(self, topic, data):
        # producer = KafkaProducer(acks = 0, 
        #                          bootstrap_servers = brokers,
        #                          compression_type='gzip',
        #                          value_serializer = lambda x: dumps(x, ensure_ascii=False).encode('utf-8'),
        #                          api_version=(0,10,2))

        producer = KafkaProducer(
            acks = 0,
            compression_type = 'gzip',
            bootstrap_servers = brokers,
            value_serializer = lambda x: dumps(x).encode('utf-8')
        )
        producer.send(topic, value = data)
        producer.flush()

    def kafka_Consumer(self, topic):
        # consumer = KafkaConsumer(
        #     topic,
        #     group_id = None,
        #     bootstrap_servers = brokers,
        #     enable_auto_commit = True,
        #     auto_offset_reset = 'latest',
        #     value_deserializer = lambda m: loads(m),
        #     api_version=(0,10,2))

        consumer = KafkaConsumer(
            topic,
            bootstrap_servers = brokers,
            auto_offset_reset = 'earliest',
            enable_auto_commit = True,
            group_id = 'my-group',
            value_deserializer = lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms = 10000
        )

        return consumer
