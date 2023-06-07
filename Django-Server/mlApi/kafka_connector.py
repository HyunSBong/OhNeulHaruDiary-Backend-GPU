from kafka import KafkaConsumer
from kafka import KafkaProducer
from json import dumps
from json import loads
import json

brokers = ["localhost:9091"] # "docker internal => kafka1:19091"
class KafkaConnector:
    def Kafka_Producer(self, topic, data):
        producer = KafkaProducer(
            acks = 0,
            compression_type='gzip',
            bootstrap_servers = brokers,
            value_serializer=lambda x: dumps(x, ensure_ascii=False).encode('utf-8'),
            api_version=(0,11,5)
        )
        producer.send(topic, value = data)
        producer.flush()

    def kafka_Consumer(self, topic):

        consumer = KafkaConsumer(
            topic,
            group_id = None,
            bootstrap_servers = brokers,
            auto_offset_reset = 'earliest',
            enable_auto_commit = True,
            value_deserializer = lambda x: json.loads(x.decode('utf-8')),
            api_version=(0,11,5)
        )

        return consumer
