from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
import json
import logging

class KafkaClient:
    """
     Handles Kafka connections and topic management.
     Creates required topics and provides methods for message production/consumption.
    """
    def __init__(self, config):
        self.config = config
        self.bootstrap_servers = config['kafka']['bootstrap_servers']
        self.create_topics()
        self.consumer = self._create_consumer()
        self.producer = self._create_producer()

    def create_topics(self):
        print(self.bootstrap_servers)
        admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)

        topics = [
            NewTopic(name=topic, num_partitions=1, replication_factor=1)
            for topic in self.config['kafka']['topics'].values()
        ]
        
        try:
            admin_client.create_topics(topics)
        except Exception as e:
            logging.info(f"Topics might exist: {e}")

    def _create_consumer(self):
        return KafkaConsumer(
            self.config['kafka']['topics']['input'],
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.config['kafka']['consumer']['group_id'],
            auto_offset_reset=self.config['kafka']['consumer']['auto_offset_reset'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

    def _create_producer(self):
        return KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )

    def send_message(self, topic, message):
        self.producer.send(topic, message)
        self.producer.flush()