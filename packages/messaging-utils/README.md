# Messaging Utilities

This directory contains Python utilities for message publishing and communication with RabbitMQ in the ETL Design platform. These utilities provide a standardized interface for sending messages between microservices.

## 📋 Overview

The messaging-utils package provides high-level abstractions for RabbitMQ operations, including message publishers, connection management, and schema definitions for asynchronous communication between services.

## 🗂️ Directory Structure

```text
messaging-utils/
└── messaging-utils-py/          # Python messaging utilities
    ├── src/
    │   └── messaging_utils/
    │       ├── core/            # Core connection and configuration
    │       ├── messaging/       # Publishers and connection factory
    │       └── schemas/         # Message schema definitions
    ├── tests/                   # Unit tests
    ├── pyproject.toml          # Python package configuration
    └── uv.lock                 # Dependency lock file
```

## 📦 Package

**Package Name**: `messaging-utils`

**Features**:

- RabbitMQ connection factory with connection pooling
- Type-safe message publishers for validation and schema operations
- Standardized message formatting and routing
- Integration with Protocol Buffer message types
- Asynchronous and synchronous publishing support

**Dependencies**:

- `proto-utils`: Protocol Buffer utilities and generated types
- `pika`: Synchronous RabbitMQ client
- `aio-pika`: Asynchronous RabbitMQ client
- `pydantic-settings`: Configuration management

**Requirements**:

- Python 3.12+
- Compatible with backend services that use RabbitMQ messaging

## 🚀 Core Components

### Connection Factory

Provides managed RabbitMQ connections with thread-safe operation:

```python
from messaging_utils.messaging.connection_factory import RabbitMQConnectionFactory

# Configure the factory (usually done at application startup)
RabbitMQConnectionFactory.configure()

# Use context manager for channel operations
with RabbitMQConnectionFactory.get_channel() as channel:
    # Channel is ready with infrastructure set up
    channel.basic_publish(
        exchange='typechecking.exchange',
        routing_key='validation.request',
        body='message'
    )
```

### Message Publishers

Type-safe publishers for different message types:

#### Validation Messages

```python
from messaging_utils.messaging.publishers import Publisher
from messaging_utils.schemas.validation import Metadata

publisher = Publisher()

# Publish validation request
task_id = publisher.publish_validation_request(
    routing_key="validation.request",
    file_data=file_content,
    import_name="user_schema_v1",
    metadata=Metadata(
        filename="data.csv",
        content_type="text/csv",
        size=24
    ),
    task="sample_validation"
)
```

#### Schema Messages

```python
from messaging_utils.messaging.publishers import Publisher

publisher = Publisher()

# Publish schema update
task_id = publisher.publish_schema_update(
    routing_key="schema.update",
    import_name="user_schema_v1",
    task="upload_schema",
    schema_data=json_schema_dict
)
```

## 🔧 Message Types

The package supports standardized message types for:

### Validation Operations

- **Validation Tasks**: File validation requests with schema references
- **Validation Results**: Processing results and error reports
- **Progress Updates**: Status updates for long-running validations

### Schema Operations

- **Schema Updates**: Create, update, or delete JSON schemas
- **Schema Validation**: Validate schema definitions
- **Version Management**: Schema versioning and migration

## 🏗️ Integration

This package is used by:

- **API Service**: [`apps/backend/api/`](../../apps/backend/api/) - Publishing validation requests
- **Typechecking Service**: [`apps/backend/typechecking/`](../../apps/backend/typechecking/) - Consuming messages
- **Database Service**: [`apps/connections/`](../../apps/connections/) - Schema management

## 📊 Message Flow

```text
API Service → RabbitMQ → Typechecking Workers → Database Service
     ↓           ↓              ↓                    ↓
  Publisher    Queue         Consumer            Storage
```

## ⚙️ Configuration

The package uses environment-based configuration loaded automatically:

```env
# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_VHOST=/
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=admin

# Exchange and Queue Configuration
RABBITMQ_EXCHANGE=typechecking.exchange
RABBITMQ_EXCHANGE_TYPE=topic

# Queues for different message types
RABBITMQ_QUEUE_SCHEMAS=typechecking.schemas.queue
RABBITMQ_QUEUE_VALIDATIONS=typechecking.validations.queue
RABBITMQ_QUEUE_RESULTS_SCHEMAS=typechecking.schemas.results.queue
RABBITMQ_QUEUE_RESULTS_VALIDATIONS=typechecking.validation.results.queue

# Routing Keys (used for binding queues to the exchange)
RABBITMQ_ROUTING_KEY_SCHEMAS=schemas.*
RABBITMQ_ROUTING_KEY_VALIDATIONS=validation.*
RABBITMQ_ROUTING_KEY_RESULTS_SCHEMAS=schemas.result.*
RABBITMQ_ROUTING_KEY_RESULTS_VALIDATIONS=validation.results.*

# Routing Keys for Publishing (used by producers to send messages)
RABBITMQ_PUBLISHERS_ROUTING_KEY_SCHEMAS=schemas.update
RABBITMQ_PUBLISHERS_ROUTING_KEY_VALIDATIONS=validation.request
RABBITMQ_PUBLISHERS_ROUTING_KEY_RESULTS_SCHEMAS=schemas.results.publish
RABBITMQ_PUBLISHERS_ROUTING_KEY_RESULTS_VALIDATIONS=validation.results.publish
```

The configuration is managed through the `messaging_params` module and automatically applied when creating publishers.

## 🔧 Development

### Installation

```bash
cd messaging-utils-py/
uv sync
```

### Testing

```bash
uv run pytest
uv run pytest --cov=messaging_utils
```

### Building

```bash
uv run python -m build
```

## 🧪 Testing

The package includes comprehensive tests:

- **Unit Tests**: Testing individual publisher components
- **Integration Tests**: Testing RabbitMQ communication
- **Mock Tests**: Testing without external dependencies

## 📈 Features

### Connection Management

- Automatic connection pooling and reuse
- Graceful reconnection on connection failures
- Connection health monitoring

### Message Reliability

- Unique message ID generation
- Message persistence configuration
- Delivery confirmation support
- Dead letter queue handling

### Type Safety

- Protocol Buffer integration for type-safe messages
- Pydantic models for configuration validation
- Comprehensive type hints throughout

---

> **Note**: This package provides a high-level interface for RabbitMQ operations. For low-level messaging operations, use the underlying `pika` or `aio-pika` libraries directly.
