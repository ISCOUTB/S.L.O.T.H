# Database Connections Service

A centralized gRPC microservice for database connection management and operations, providing a unified abstraction layer for MongoDB and Redis. This service was designed to solve architectural problems that arise when multiple microservices need to share the same databases, while maintaining microservices architecture principles.

## Purpose and Architecture

### Problem Solved

In a microservices architecture, traditionally each service should have its own database. However, in this project, the [API](../../backend/api/) and [Typechecking](../../backend/typechecking/) services needed to share:

- **Redis**: For fast task state tracking and response caching
- **MongoDB**: For JSON schema persistence and task history

This service centralizes access to these databases through gRPC, eliminating direct coupling and maintaining microservices philosophy.

### Dual Storage Strategy

The service implements an intelligent dual storage strategy:

- **Redis**: Fast cache for immediate access and real-time task state management
- **MongoDB**: Persistent storage for JSON schemas and task backup

With automatic synchronization and fallback mechanisms between both systems.

## Main Features

### Task Management

- **State Tracking**: Real-time monitoring of asynchronous task states
- **Automatic Persistence**: Transparent synchronization between Redis and MongoDB
- **Intelligent TTL**: Differentiated expiration policies based on task state
- **Automatic Fallback**: Recovery from MongoDB when Redis is unavailable

### JSON Schema Management

- **Schema Versioning**: Automatic version control with release history
- **Intelligent Comparison**: Change detection and redundant update prevention
- **CRUD Operations**: Create, read, update, and delete schemas with validation
- **Release Management**: Reversion to previous versions when active schema is deleted

### Cache Operations

- **General Cache**: Basic get/set operations with configurable TTL
- **Key Management**: Pattern-based search and bulk operations
- **Cache Cleanup**: Selective and complete cleanup operations
- **Monitoring**: Connectivity verification and service status

## Technologies Used

- **Python 3.12**: Main service language
- **gRPC**: High-performance communication protocol
- **Redis 6.4+**: In-memory database for cache and task state
- **MongoDB 4.15+**: NoSQL database for persistence
- **Protocol Buffers**: Efficient data serialization
- **Docker**: Service containerization

## Configuration

### Environment Variables

The service is configured through environment variables. Copy `.env.example` to `.env` and adjust the values:

```bash
cp .env.example .env
```

Main configurations include:

- **MongoDB**: Connection, authentication, and collection names
- **Redis**: Connection, authentication, and TTL configuration
- **gRPC**: Host, port, and debug settings
- **TTL by State**: Differentiated expiration times by task type

### Intelligent TTL

The service implements differentiated TTL policies based on context:

- **Pending Tasks**: 30 minutes
- **Processing Tasks**: 1 hour  
- **Completed Tasks**: 24 hours
- **Failed Tasks**: 12 hours
- **User Cache**: 15 minutes
- **Schema Cache**: 6 hours

## Service Usage

### gRPC Server

The service exposes its functionalities through a gRPC server that implements the following interfaces:

- **Redis Operations**: Basic cache operations and task management
- **MongoDB Operations**: JSON schema CRUD with versioning
- **Task Management**: Comprehensive task management with dual storage

### Service Clients

Client microservices communicate with this service using gRPC stubs generated from `.proto` files located in [`packages/proto/database/`](../../../packages/proto/database/).

## Project Structure

```text
src/
├── server.py              # Main gRPC server
├── core/                  # Configuration and base connections
│   ├── config.py          # Service configuration
│   ├── database_mongo.py  # MongoDB client
│   └── database_redis.py  # Redis client
├── handlers/              # gRPC handlers
│   ├── mongo.py           # MongoDB operations
│   ├── redis.py           # Redis operations
│   └── tasks.py           # Task management
├── services/              # Business logic
│   ├── mongo.py           # Schema services
│   ├── redis.py           # Cache services
│   └── tasks.py           # Task services
└── utils/
    └── logger.py          # Logging configuration
```

## Available Commands

### Development

```bash
# Run the server
moon run database:run

# Run tests with coverage
moon run database:test

# Format code
moon run database:format
```

### Docker

```bash
# Build image
moon run database:docker-build

# Run container
docker run -p 50050:50050 --env-file .env database:1.0
```

## Testing

The service includes a comprehensive unit test suite that covers:

- **Redis Operations**: Cache, tasks, and connectivity tests
- **MongoDB Operations**: Schema, versioning, and CRUD tests
- **Task Management**: Dual storage and synchronization tests
- **Integration**: End-to-end gRPC server tests

Tests are located in the `tests/` directory and can be executed with the `moon run database:test` command.

## Dependencies

For more details about project dependencies, refer to the [`pyproject.toml`](./pyproject.toml) file.

Main dependencies include:

- **proto-utils**: Protocol Buffers utilities (internal package)
- **pymongo**: Official MongoDB client
- **redis**: Official Redis client  
- **pydantic-settings**: Type-safe configuration management
