# gRPC Messaging Proxy Server

A lightweight gRPC server that acts as a proxy between RabbitMQ message queues and the Typechecking microservice, providing real-time message streaming and configuration management for the ETL Design system.

## Overview

The Messaging Connection service serves as a critical middleware component in the ETL Design architecture, enabling seamless communication between the API layer and the Typechecking service through RabbitMQ message broker. This service abstracts the complexity of direct RabbitMQ interaction while providing a standardized gRPC interface for message consumption and configuration management.

### Architecture Role

```text
API Service → RabbitMQ → Messaging Server (this) → Typechecking Service
     ↓                                                      ↑
  Publishes directly                            Consumes via gRPC streaming
```

The API service publishes messages directly to RabbitMQ without using this proxy, but consults this server only to obtain RabbitMQ connection credentials. The Typechecking service, however, relies entirely on this server for consuming messages through gRPC streaming interfaces.

### Core Functionality

- **Connection Parameter Distribution**: Provides RabbitMQ connection credentials to other services
- **Real-time Message Streaming**: Streams schema and validation messages from RabbitMQ queues to gRPC clients
- **Routing Key Management**: Manages message routing configuration for different queue types
- **Service Abstraction**: Hides RabbitMQ complexity behind a clean gRPC interface

## Service Architecture

### Components

The service is organized into several key components:

- **gRPC Server** (`src/server.py`): Main server implementation with streaming endpoints
- **Configuration Management** (`src/core/`): Settings and connection parameter management
- **Service Handlers** (`src/handlers/`): Business logic for request processing
- **Parameter Services** (`src/services/`): Connection and routing key configuration
- **Utilities** (`src/utils/`): Logging and common utilities

### gRPC Interface

The service implements the `MessagingService` protocol buffer interface with the following endpoints:

#### Configuration Endpoints

- `GetMessagingParams`: Retrieves RabbitMQ connection parameters
- `GetRoutingKeySchemas`: Gets routing keys for schema message queues
- `GetRoutingKeyValidations`: Gets routing keys for validation message queues

#### Streaming Endpoints

- `StreamSchemaMessages`: Continuous streaming of schema update messages
- `StreamValidationMessages`: Continuous streaming of validation request messages

## Message Types

The system handles two primary message categories:

### Schema Messages

- **Purpose**: Manage database schema updates and validation
- **Queue**: `typechecking.schemas.queue`
- **Routing Key**: `schemas.*`
- **Content**: JSON schema definitions, import names, and metadata

### Validation Messages

- **Purpose**: Handle file validation requests and results
- **Queue**: `typechecking.validations.queue`
- **Routing Key**: `validation.*`
- **Content**: File data, validation tasks, and processing metadata

## Configuration

### Environment Variables

The service requires the following environment configuration:

#### RabbitMQ Connection

```bash
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_VHOST=/
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=admin
```

#### Exchange and Queue Configuration

```bash
RABBITMQ_EXCHANGE=typechecking.exchange
RABBITMQ_EXCHANGE_TYPE=topic
RABBITMQ_QUEUE_SCHEMAS=typechecking.schemas.queue
RABBITMQ_QUEUE_VALIDATIONS=typechecking.validations.queue
RABBITMQ_QUEUE_RESULTS_SCHEMAS=typechecking.schemas.results.queue
RABBITMQ_QUEUE_RESULTS_VALIDATIONS=typechecking.validation.results.queue
```

#### Routing Keys

```bash
RABBITMQ_ROUTING_KEY_SCHEMAS=schemas.*
RABBITMQ_ROUTING_KEY_VALIDATIONS=validation.*
RABBITMQ_ROUTING_KEY_RESULTS_SCHEMAS=schemas.result.*
RABBITMQ_ROUTING_KEY_RESULTS_VALIDATIONS=validation.result.*
```

#### Server Configuration

```bash
MESSAGING_CONNECTION_HOST=localhost
MESSAGING_CONNECTION_PORT=50055
MESSAGING_CONNECTION_DEBUG=True
```

### Configuration Files

- **Environment**: `.env` file for local development settings
- **Project**: `pyproject.toml` for Python dependencies and tool configuration
- **Moon**: `moon.yml` for build system and task definitions

See `.env.example` for a complete configuration template.

## Running the Service

### Prerequisites

- Python 3.12.10 or higher
- UV package manager
- Running RabbitMQ instance
- Required dependencies (automatically managed by UV)

### Development Setup

1. **Clone and navigate to the service directory**:

   ```bash
   cd apps/connections/messaging
   ```

2. **Set up environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

3. **Install dependencies**:

   ```bash
   uv sync
   ```

4. **Start the server**:

   ```bash
   uv run python -m src.server
   ```

   Or using Moon build system:

   ```bash
   moon run messaging:run
   ```

### Production Deployment

For production deployment, ensure:

- RabbitMQ is properly configured and accessible
- Environment variables are securely managed
- Appropriate logging levels are set
- Network security is configured for gRPC port

## Usage Examples

### Client Connection

The service provides a test client (`test_client.py`) that demonstrates how to interact with the server:

```bash
# Run the test client
uv run python test_client.py

# With custom host/port
uv run python test_client.py --host localhost --port 50055
```

### Integration with Other Services

#### API Service Usage

The API service connects to retrieve RabbitMQ credentials:

```python
# API service connects only to get RabbitMQ connection parameters
response = await stub.GetMessagingParams(request)
# Then uses these parameters to publish directly to RabbitMQ
```

#### Typechecking Service Usage

The Typechecking service streams messages continuously:

```python
# Typechecking service streams messages for processing
async for message in stub.StreamSchemaMessages(request):
    # Process each schema message as it arrives
```

## Testing

The service includes comprehensive test coverage with both unit and integration tests.

### Running Tests

```bash
# Run all tests
uv run pytest -v

# Run only unit tests (fast, no external dependencies)
uv run pytest -m "not integration" -v

# Run only integration tests (requires running RabbitMQ and gRPC server)
uv run pytest -m integration -v

# Run tests with coverage
uv run pytest -v --cov=src --cov-report=html
```

### Test Categories

- **Unit Tests**: Mock-based testing of individual components without external dependencies
- **Integration Tests**: End-to-end testing with real RabbitMQ and gRPC connections
- **Service Tests**: Parameter service functionality and routing key management

### Test Requirements

- Unit tests: No external dependencies (all mocked)
- Integration tests: Requires running RabbitMQ instance and gRPC server

## Logging and Monitoring

### Logging Configuration

The service implements structured logging with contextual information:

- **Stream IDs**: Unique identifiers for tracking client connections
- **Message Counts**: Processing metrics and queue information
- **Connection Lifecycle**: Detailed connection and cleanup logging
- **Error Handling**: Comprehensive error logging with context

### Log Files

- `logs/messaging_server.log`: General application logs
- `logs/messaging_server_errors.log`: Error-specific logs
- `logs/messaging_server_daily.log`: Daily rotating logs

### Monitoring Endpoints

The service logs performance metrics including:

- Queue sizes and processing times
- Connection counts and client information
- Message throughput and error rates

## Development Guidelines

### Code Organization

The codebase follows Python best practices with clear separation of concerns:

- **Protocol Definitions**: Shared protocol buffer definitions in `packages/proto-utils`
- **Messaging Utilities**: Common RabbitMQ functionality in `packages/messaging-utils`
- **Service Logic**: Core business logic in `src/` directory
- **Configuration**: Environment-based configuration management
- **Testing**: Comprehensive test suite with proper isolation

### Adding New Features

When extending the service:

1. **Protocol Changes**: Update protocol buffer definitions first
2. **Service Implementation**: Add business logic in appropriate service classes
3. **Handler Integration**: Connect new logic through handler classes
4. **Testing**: Include both unit and integration tests
5. **Documentation**: Update relevant documentation sections

### Performance Considerations

- **Connection Pooling**: RabbitMQ connections are managed per-thread
- **Async Streaming**: Non-blocking message streaming for multiple clients
- **Memory Management**: Efficient message processing with proper cleanup
- **Error Recovery**: Graceful handling of connection failures and timeouts

## Dependencies

### Core Dependencies

- **grpcio**: gRPC Python implementation for server functionality
- **pika**: RabbitMQ client library for message broker interaction
- **pydantic**: Configuration management and data validation
- **proto-utils**: Internal package for protocol buffer utilities
- **messaging-utils**: Internal package for RabbitMQ connection management

### Development Dependencies

- **pytest**: Testing framework with async support
- **pytest-cov**: Code coverage reporting
- **pytest-asyncio**: Async test support
- **ruff**: Code formatting and linting

### Internal Packages

The service depends on internal packages within the ETL Design monorepo:

- `packages/proto-utils/proto-utils-py`: Protocol buffer definitions and utilities
- `packages/messaging-utils/messaging-utils-py`: RabbitMQ connection and publishing utilities

## Troubleshooting

### Common Issues

#### Connection Failures

- **Symptom**: gRPC connection errors or timeouts
- **Solution**: Verify RabbitMQ is running and accessible with correct credentials

#### Message Streaming Issues

- **Symptom**: Messages not arriving or streaming stops
- **Solution**: Check RabbitMQ queue status and message publisher functionality

#### Configuration Problems

- **Symptom**: Service fails to start or connect
- **Solution**: Verify environment variables and configuration file completeness

### Debug Mode

Enable debug mode for detailed logging:

```bash
MESSAGING_CONNECTION_DEBUG=True
```

### Health Checks

Monitor service health through:

- Log file analysis for error patterns
- Connection status in RabbitMQ management interface
- gRPC client connectivity tests

## Security Considerations

### Network Security

- Configure firewall rules for gRPC port (default: 50055)
- Use secure RabbitMQ connections in production
- Implement proper authentication for gRPC clients

### Credential Management

- Store RabbitMQ credentials securely (environment variables, secrets management)
- Rotate credentials regularly
- Use principle of least privilege for RabbitMQ user permissions

### Data Privacy

- Message content is streamed in real-time without persistent storage
- Ensure sensitive data in messages is properly encrypted
- Implement audit logging for compliance requirements

## Related Services

This service is part of the larger ETL Design ecosystem:

- **API Service** (`apps/backend/api/`): Publishes messages to RabbitMQ and consults this service for credentials
- **Typechecking Service** (`apps/backend/typechecking/`): Consumes messages through this service's gRPC interface
- **Database Connection** (`apps/connections/database/`): Parallel service for database connection management

For more information about the overall system architecture, see the [main project README](../../../README.md).
