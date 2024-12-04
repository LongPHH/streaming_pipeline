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

## Design Documentation
For detailed design decisions and implementation notes, see [Design Documentation](DesignDoc.md)

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