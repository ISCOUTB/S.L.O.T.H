# Connection Services

A collection of centralized gRPC microservices that solve architectural challenges in shared resource management for microservices. These services provide unified access to databases and messaging systems while maintaining microservices architecture principles.

## Architecture Problem & Solution

### The Challenge

In a traditional microservices architecture, each service should maintain its own isolated databases. However, our ETL Design system requires the [API](../backend/api/) and [Typechecking](../backend/typechecking/) services to share:

- **Redis**: Fast task state tracking and response caching
- **MongoDB**: Persistent storage for JSON schemas and task history  
- **RabbitMQ**: Pub/Sub messaging for asynchronous task processing

Direct database sharing between microservices violates microservices principles and creates tight coupling between services.

### The Solution

We've implemented dedicated connection services that act as centralized proxies, providing gRPC interfaces to shared resources:

```text
┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
│ API Service │────│ Database Service│────│ Redis/Mongo │
└─────────────┘    └─────────────────┘    └─────────────┘
       │                                  ┌─────────────┐
       │                              ┌───│  RabbitMQ   │
       │            ┌─────────────────┐   └─────────────┘
       └─(creds)────│Messaging Service│
                    └─────────────────┘
                           │
┌─────────────┐            │
│Typechecking │────────────┘
│   Service   │
└─────────────┘
```

This approach:

- ✅ Maintains microservices independence
- ✅ Enables multi-language support
- ✅ Centralizes connection management
- ✅ Provides standardized interfaces
- ✅ Eliminates direct database coupling

## Services Overview

### [Database Connections](./database/)

**Purpose**: Centralized database operations for MongoDB and Redis

**Key Features**:

- **Dual Storage Strategy**: Intelligent Redis caching with MongoDB persistence
- **Task Management**: Real-time task state tracking with automatic synchronization
- **Schema Versioning**: JSON schema management with release history
- **Intelligent TTL**: Context-aware expiration policies
- **Automatic Fallback**: Seamless recovery between storage systems

**Technology Stack**: Python 3.12, gRPC, Redis 6.4+, MongoDB 4.15+

**Usage Pattern**:

- API Service: Task status queries, response caching, schema operations
- Typechecking Service: Task state updates, schema retrieval and management

### [Messaging Connections](./messaging/)

**Purpose**: gRPC proxy for RabbitMQ message streaming and configuration

**Key Features**:

- **Real-time Streaming**: Continuous message delivery via gRPC streams
- **Connection Management**: RabbitMQ credential distribution and configuration
- **Routing Intelligence**: Message routing key management for different queue types
- **Service Abstraction**: Clean gRPC interface hiding RabbitMQ complexity

**Technology Stack**: Python 3.12, gRPC, RabbitMQ, Pika

**Usage Pattern**:

- API Service: Retrieves RabbitMQ credentials for direct publishing
- Typechecking Service: Consumes messages through gRPC streaming interfaces

## Communication Patterns

### Database Access Pattern

```text
API/Typechecking → gRPC → Database Service → Redis/MongoDB
```

Both services communicate with databases exclusively through the Database Service:

- **Fast Operations**: Redis for caching and real-time task state
- **Persistent Operations**: MongoDB for schema storage and task history
- **Automatic Sync**: Transparent synchronization between both systems

### Messaging Pattern

```text
API Service → Direct RabbitMQ Publishing
Typechecking Service → gRPC Streaming ← Messaging Service ← RabbitMQ
```

Asymmetric messaging pattern:

- **Publishing**: API publishes directly to RabbitMQ (after getting credentials)
- **Consuming**: Typechecking consumes via gRPC streams from Messaging Service

## Message Types & Queues

### Schema Messages

- **Queue**: `typechecking.schemas.queue`
- **Purpose**: Database schema updates and validation
- **Routing**: `schemas.*`
- **Content**: JSON schema definitions, import names, metadata

### Validation Messages  

- **Queue**: `typechecking.validations.queue`
- **Purpose**: File validation requests and results
- **Routing**: `validation.*`
- **Content**: File data, validation tasks, processing metadata

## Shared Infrastructure

### Protocol Buffers

All services use shared `.proto` definitions located in [`packages/proto/`](../../packages/proto/):

- `database/`: Database operation interfaces
- `messaging/`: Messaging and streaming interfaces

### Utility Packages

- [`proto-utils`](../../packages/proto-utils/): Protocol buffer utilities and serialization
- [`messaging-utils`](../../packages/messaging-utils/): RabbitMQ connection and publishing utilities

## Configuration Management

### Environment-Based Configuration

Both services use environment variables for configuration:

- Database credentials and connection settings
- TTL policies and cache configuration  
- gRPC server settings and debug options
- Queue names and routing key patterns

### Service Discovery

Services communicate through configured gRPC endpoints:

- **Database Service**: Default port 50050
- **Messaging Service**: Default port 50055

## Development & Operations

### Development Commands

```bash
# Database Service
moon run database:run      # Start database service
moon run database:test     # Run database tests  
moon run database:format   # Format database code

# Messaging Service  
moon run messaging:run     # Start messaging service
moon run messaging:test    # Run messaging tests
moon run messaging:format  # Format messaging code
```

### Docker Support

Both services include Docker support for containerized deployment:

```bash
# Build services
moon run database:docker-build
moon run messaging:docker-build

# Deploy with proper networking for inter-service communication
```

### Testing Strategy

Comprehensive testing across both services:

- **Unit Tests**: Mock-based testing without external dependencies
- **Integration Tests**: Full end-to-end testing with real infrastructure
- **Service Tests**: gRPC interface and business logic validation

## Benefits of This Architecture

### Microservices Compliance

- Each service maintains its own concerns and responsibilities
- No direct database coupling between business logic services
- Clean separation between connection management and business logic

### Scalability & Performance

- Connection pooling and resource optimization at the proxy level
- Intelligent caching strategies with automatic fallback
- Efficient message streaming without polling overhead

### Technology Flexibility

- Services can be implemented in different programming languages
- Database technologies can be changed without affecting business services
- Messaging systems can be swapped (RabbitMQ → Kafka) with minimal impact

### Operational Excellence

- Centralized monitoring and logging of database/messaging operations
- Standardized error handling and retry logic
- Simplified configuration management and deployment

## Related Documentation

- [Database Service README](./database/README.md): Detailed database service documentation
- [Messaging Service README](./messaging/README.md): Comprehensive messaging service guide
- [Protocol Definitions](../../packages/proto/): Shared interface specifications

For information about client services that use these connections, see:

- [API Service](../backend/api/): REST API and authentication layer
- [Typechecking Service](../backend/typechecking/): File validation and schema management
