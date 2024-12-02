# Kafka Login Event Processor

A real-time streaming data pipeline using Kafka and Docker that processes login events.

## Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repository)

## Quick Start

1. Clone the repository:
```bash
git clone git@github.com:LongPHH/streaming_pipeline.git
```

2. Start the application:
```bash
docker-compose up --build
```

3. View the processed messages using the view_consumer tool:
```bash
# List all topics
python tools/view_consumer.py --list

# View processed login events
python tools/view_consumer.py --topics processed-logins

# View error messages
python tools/view_consumer.py --topics error-logins

# View analytics
python tools/view_consumer.py --topics login-analytics
```

4. To stop the application:
```bash
docker-compose down
```

## Project Structure
```
streaming_pipeline/
├── src/
│   ├── analytics/
│   │   └── metrics.py                  # Analytics and metrics collection
│   ├── transformer/
│   │   └── message_transformer.py      # Message transformation logic
│   ├── validator/
│   │   └── message_validator.py        # Message validation
│   ├── kafka_client.py                 # Kafka interaction handling
│   └── processor.py                    # Main processing logic
├── tools/
│   └── view_consumer.py                # Utility to view Kafka messages
├── config.yaml                         # Configuration file
├── docker-compose.yaml                 # Docker services configuration
├── Dockerfile                          # Application container configuration
└── requirements.txt                    # Python dependencies
```

## Data Flow
1. Login events are produced to the `user-login` topic
2. Events are validated and transformed
3. Valid events go to `processed-logins` topic
4. Invalid events go to `error-logins` topic
5. Analytics are published to `login-analytics` topic

## Troubleshooting

If you encounter any issues:

1. Ensure all required ports (9092, 29092) are available
2. Check Docker and Docker Compose are installed correctly
3. Verify all containers are running:
```bash
docker-compose ps
```
4. Check container logs:
```bash
docker-compose logs -f login-processor
```

## License

This project is licensed under the MIT License