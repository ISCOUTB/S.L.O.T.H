# Connection Services

A centralized gRPC microservice that solves architectural challenges in shared database resource management for microservices. This service provides unified access to databases while maintaining microservices architecture principles.

## Architecture Problem & Solution

### The Challenge

In a traditional microservices architecture, each service should maintain its own isolated databases. However, our ETL Design system requires the [API](../backend/api/) and [Typechecking](../backend/typechecking/) services to share:

- **Redis**: Fast task state tracking and response caching
- **MongoDB**: Persistent storage for JSON schemas and task history  

Direct database sharing between microservices violates microservices principles and creates tight coupling between services.

For messaging, both services connect directly to **RabbitMQ**: the API service publishes messages and the Typechecking service consumes them.

### The Solution

We've implemented a dedicated database service that acts as a centralized proxy, providing gRPC interfaces to shared database resources:

```text
┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
│ API Service │────│ Database Service│────│ Redis/Mongo │
└─────────────┘    └─────────────────┘    └─────────────┘
       │                                  
       │            ┌─────────────┐
       └────────────│  RabbitMQ   │───────┐
                    └─────────────┘       │
                                          │
┌─────────────┐                           │
│Typechecking │───────────────────────────┘
│   Service   │
└─────────────┘
```

This approach:

- ✅ Maintains microservices independence for database access
- ✅ Enables direct messaging communication
- ✅ Centralizes database connection management
- ✅ Provides standardized database interfaces
- ✅ Eliminates unnecessary messaging proxies

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

## Messaging Architecture

Both the API and Typechecking services connect directly to RabbitMQ without any intermediary proxy:

- **API Service**: Publishes messages directly to RabbitMQ queues
- **Typechecking Service**: Consumes messages directly from RabbitMQ queues

This direct connection approach eliminates unnecessary complexity and potential points of failure that would be introduced by a messaging proxy service.

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
Typechecking Service → Direct RabbitMQ Consuming
```

Direct messaging pattern:

- **Publishing**: API service publishes directly to RabbitMQ queues
- **Consuming**: Typechecking service consumes directly from RabbitMQ queues

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

The Database service uses shared `.proto` definitions located in [`packages/proto/`](../../packages/proto/):

- `database/`: Database operation interfaces

### Utility Packages

- [`proto-utils`](../../packages/proto-utils/): Protocol buffer utilities and serialization
- [`messaging-utils`](../../packages/messaging-utils/): RabbitMQ connection and publishing utilities

## Configuration Management

### Environment-Based Configuration

The Database service uses environment variables for configuration:

- Database credentials and connection settings
- TTL policies and cache configuration  
- gRPC server settings and debug options

Both API and Typechecking services manage their own RabbitMQ connection configuration:

- Queue names and routing key patterns
- RabbitMQ connection credentials
- Message processing settings

### Service Discovery

Services communicate through configured endpoints:

- **Database Service**: Default port 50050
- **RabbitMQ**: Direct connection to configured RabbitMQ instance

## Development & Operations

### Development Commands

```bash
# Database Service
moon run database:run      # Start database service
moon run database:test     # Run database tests  
moon run database:format   # Format database code
```

### Docker Support

The Database service includes Docker support for containerized deployment:

```bash
# Build service
moon run database:docker-build

# Deploy with proper networking for inter-service communication
```

### Testing Strategy

Comprehensive testing for the Database service:

- **Unit Tests**: Mock-based testing without external dependencies
- **Integration Tests**: Full end-to-end testing with real infrastructure
- **Service Tests**: gRPC interface and business logic validation

## Benefits of This Architecture

### Microservices Compliance

- Database service maintains clear separation of concerns and responsibilities
- No direct database coupling between business logic services
- Clean separation between database connection management and business logic
- Direct messaging eliminates unnecessary complexity

### Scalability & Performance

- Database connection pooling and resource optimization at the proxy level
- Intelligent caching strategies with automatic fallback
- Direct RabbitMQ communication reduces latency and improves throughput

### Technology Flexibility

- Services can be implemented in different programming languages
- Database technologies can be changed without affecting business services
- Direct messaging allows each service to optimize its RabbitMQ usage patterns

### Operational Excellence

- Centralized monitoring and logging of database operations
- Standardized error handling and retry logic for database access
- Simplified configuration management and deployment
- Reduced points of failure by eliminating unnecessary messaging proxies

## Related Documentation

- [Database Service README](./database/README.md): Detailed database service documentation
- [Protocol Definitions](../../packages/proto/): Shared interface specifications

For information about client services that use these connections, see:

- [API Service](../backend/api/): REST API and authentication layer
- [Typechecking Service](../backend/typechecking/): File validation and schema management
