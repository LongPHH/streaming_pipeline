from kafka import KafkaConsumer, KafkaAdminClient
import json
import argparse
import os

# Get bootstrap servers from environment variable or use default
BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:29092').split(',')

def get_topics():
    """Gets list of topics from Kafka broker"""
    admin = KafkaAdminClient(bootstrap_servers=BOOTSTRAP_SERVERS)
    return admin.list_topics()

def create_consumer(topic):
    """Creates consumer for a single topic with standard config"""
    return KafkaConsumer(
        topic,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest', 
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

def view_messages(selected_topics=None):
    """
    Main viewing function
    Args:
        selected_topics (list): List of topic names to monitor
    """
    try:
        # Get all topics or filter to selected ones
        topics = get_topics()
        if selected_topics:
            topics = [t for t in topics if t in selected_topics]
        
        if not topics:
            print("No matching topics found!")
            return
        
        print(f"Monitoring topics: {topics}")
        print("Press Ctrl+C to exit")
        
        # Create consumers for each topic
        consumers = {topic: create_consumer(topic) for topic in topics}
        
        # Monitor messages
        while True:
            for topic, consumer in consumers.items():
                for message in consumer:
                    print(f"\n{topic}:", json.dumps(message.value, indent=2))

    except KeyboardInterrupt:
        print("\nShutting down consumers viewer...")
        for consumer in consumers.values():
            consumer.close()
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Kafka topic message viewer')
    parser.add_argument('--list', action='store_true', help='List all available topics')
    parser.add_argument('--topics', nargs='*', help='Topics to monitor (space-separated)')
    
    args = parser.parse_args()
    
    if args.list:
        topics = get_topics()
        print("\nAvailable topics:")
        for topic in sorted(topics):
            print(f"- {topic}")
        return

    if args.topics:
        view_messages(args.topics)
    else:
        view_messages()

if __name__ == "__main__":
    main()