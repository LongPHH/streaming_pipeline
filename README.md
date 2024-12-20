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
docker-compose exec kafka-consumer python -m tools.view_consumer --list

# View raw login events
docker-compose exec kafka-consumer python -m tools.view_consumer --topics user-login

# View processed login events
docker-compose exec kafka-consumer python -m tools.view_consumer --topics processed-logins

# View error messages
docker-compose exec kafka-consumer python -m tools.view_consumer --topics error-logins

# View analytics topics
docker-compose exec kafka-consumer python -m tools.view_consumer --topics <desired_topic>
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