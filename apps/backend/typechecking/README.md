# Typechecking Service

A high-performance background processing service that validates spreadsheet files (CSV, XLSX, XLS) against JSON schemas using parallel processing with Polars. This service operates as a collection of RabbitMQ consumer workers that process validation and schema management tasks asynchronously.

## 🚀 Overview

The Typechecking Service is the computational backbone of the ETL Design system, responsible for all file validation and schema processing operations. It operates as a distributed worker system that consumes messages from RabbitMQ queues and processes them using parallel computation techniques.

## ✨ Key Features

- **🔄 Asynchronous Processing**: RabbitMQ-based message consumption for scalable background processing
- **⚡ High-Performance Validation**: Polars-based data processing for fast file validation
- **📊 Parallel Computing**: Multi-worker processing with configurable concurrency levels
- **🏷️ Schema Management**: Automated JSON schema creation, versioning, and removal
- **📄 Multi-Format Support**: Handles CSV, XLSX, and XLS files seamlessly
- **🔍 Detailed Validation Reports**: Comprehensive error reporting with row-level validation results
- **🏥 Robust Error Handling**: Graceful error recovery and detailed logging
- **🔧 Thread-Safe Operations**: Multiple worker threads with proper resource management
- **💊 Health Monitoring**: Optional REST endpoint for health checks and service status

## Architecture

The service runs as a collection of specialized workers that process different types of messages:

```text
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   API Service   │────▶│   RabbitMQ      │────▶│  Typechecking   │
│   (Publisher)   │     │   (Message      │     │   Workers       │
└─────────────────┘     │    Broker)      │     └─────────────────┘
                        └─────────────────┘              │
                                 │                       │
                        ┌────────▼────────┐              ▼
                        │  Message Queues │     ┌─────────────────┐
                        │                 │     │ Database Service│
                        │ • Validation    │     │   (gRPC Proxy)  │
                        │ • Schemas       │     └─────────────────┘
                        │ • Results       │              │
                        └─────────────────┘              ▼
                                                ┌─────────────────┐
                                                │ Redis + MongoDB │
                                                │ (Schema Storage)│
                                                └─────────────────┘
```

### Worker Types

- **Validation Worker**: Processes file validation requests against JSON schemas
- **Schema Worker**: Handles schema upload, update, and removal operations
- **Worker Manager**: Coordinates worker lifecycle and handles graceful shutdown

### Data Processing Flow

1. **Message Consumption**: Workers consume messages from dedicated RabbitMQ queues
2. **File Processing**: Uploaded files are processed using Polars for high performance
3. **Schema Validation**: Files are validated against JSON schemas using jsonschema library
4. **Parallel Processing**: Large files are split across multiple worker processes
5. **Result Publishing**: Validation results are published back to result queues
6. **Status Updates**: Task status is updated in the database via gRPC

## 💊 Health Monitoring

The service optionally exposes a lightweight REST endpoint for health checks and monitoring:

### Health Endpoint

```text
GET /health
```

**Response Example:**

```json
{
  "status": "healthy",
  "service": "typechecking",
  "timestamp": "2025-10-14T10:30:00Z",
  "workers": {
    "validation_worker": "running",
    "schema_worker": "running"
  },
  "connections": {
    "rabbitmq": "connected",
    "database_service": "connected"
  },
  "queues": {
    "validation_queue_size": 0,
    "schema_queue_size": 0
  }
}
```

### Configuration

```bash
# Optional Health Check Server
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_HOST="0.0.0.0"
HEALTH_CHECK_PORT=8001
```

**Note**: The health endpoint is completely optional and can be disabled for production deployments where monitoring is handled externally.

## 🔧 Workers

### Validation Worker

Processes file validation messages from the `typechecking.validations.queue`:

- **Input**: File data (as hex), import name, task ID
- **Processing**: Multi-threaded validation using Polars dataframes
- **Output**: Detailed validation results with error reports
- **Performance**: Configurable worker concurrency and prefetch count

### Schema Worker

Handles schema management messages from the `typechecking.schemas.queue`:

- **Input**: JSON schema data, import name, operation type
- **Processing**: Schema validation, versioning, and storage
- **Output**: Schema operation results with status updates
- **Operations**: Create, update, remove schemas with rollback support

## ⚙️ Configuration

The service uses environment variables for configuration. Create a `.env` file based on `.env.example`.

### Database Configuration

```bash
# Database Service (gRPC Connection)
DATABASE_CONNECTION_HOST="localhost"
DATABASE_CONNECTION_PORT=50050
```

### RabbitMQ Configuration

```bash
# RabbitMQ Connection
RABBITMQ_HOST="localhost"
RABBITMQ_PORT=5672
RABBITMQ_VHOST="/"
RABBITMQ_USER="admin"
RABBITMQ_PASSWORD="admin"

# Worker Performance
MAX_WORKERS=4
WORKER_CONCURRENCY=4
WORKER_PREFETCH_COUNT=1

# Exchange Configuration
RABBITMQ_EXCHANGE="typechecking.exchange"
RABBITMQ_EXCHANGE_TYPE="topic"
```

### Queue Configuration

```bash
# Input Queues (Workers consume from these)
RABBITMQ_QUEUE_SCHEMAS="typechecking.schemas.queue"
RABBITMQ_QUEUE_VALIDATIONS="typechecking.validations.queue"

# Result Queues (Workers publish to these)
RABBITMQ_QUEUE_RESULTS_SCHEMAS="typechecking.schemas.results.queue"
RABBITMQ_QUEUE_RESULTS_VALIDATIONS="typechecking.validation.results.queue"

# Routing Keys for Message Binding
RABBITMQ_ROUTING_KEY_SCHEMAS="schemas.*"
RABBITMQ_ROUTING_KEY_VALIDATIONS="validation.*"
RABBITMQ_ROUTING_KEY_RESULTS_SCHEMAS="schemas.result.*"
RABBITMQ_ROUTING_KEY_RESULTS_VALIDATIONS="validation.results.*"

# Publishing Routing Keys
RABBITMQ_PUBLISHERS_ROUTING_KEY_SCHEMAS="schemas.update"
RABBITMQ_PUBLISHERS_ROUTING_KEY_VALIDATIONS="validation.request"
RABBITMQ_PUBLISHERS_ROUTING_KEY_RESULTS_SCHEMAS="schemas.results.publish"
RABBITMQ_PUBLISHERS_ROUTING_KEY_RESULTS_VALIDATIONS="validation.results.publish"
```

## 🛠️ Development

### Prerequisites

- Python 3.12.10
- RabbitMQ 4.0+
- Database Service running (for gRPC operations)

### Installation

```bash
# Install dependencies
uv sync

# Install development dependencies
uv sync --group dev
```

### Running the Service

```bash
# Start all workers
uv run python -m src.main

# Run with custom configuration
MAX_WORKERS=8 uv run python -m src.main
```

### Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run parallel tests
uv run pytest -n auto
```

## 🏗️ Project Structure

```text
typechecking/
├── src/
│   ├── core/              # Configuration and shared components
│   │   ├── config.py      # Environment variable settings
│   │   └── database_client.py  # gRPC client for database service
│   ├── handlers/          # Business logic for processing
│   │   ├── validation.py  # File validation logic
│   │   └── schemas.py     # Schema management logic
│   ├── schemas/           # Pydantic models
│   │   ├── handlers.py    # Data models for handlers
│   │   └── workers.py     # Message schemas for workers
│   ├── services/          # External service integrations
│   │   └── file_processor.py  # File processing utilities
│   ├── utils/             # Utility functions
│   │   └── __init__.py    # Logging and datetime utilities
│   ├── workers/           # RabbitMQ consumer workers
│   │   ├── validation.py  # Validation message processor
│   │   ├── schemas.py     # Schema message processor
│   │   └── utils.py       # Worker utility functions
│   └── main.py            # Worker manager and entry point
├── tests/                 # Test suite
├── logs/                  # Application logs
└── pyproject.toml         # Project configuration
```

## 📊 Performance

### Validation Performance

- **Polars Integration**: Ultra-fast dataframe operations for large files
- **Parallel Processing**: Configurable worker processes for CPU-intensive validation
- **Memory Efficiency**: Streaming file processing to handle large datasets
- **Batch Processing**: Multiple files can be processed concurrently

### Scalability Features

- **Horizontal Scaling**: Multiple worker instances can run on different machines
- **Queue-Based Architecture**: Natural load balancing through RabbitMQ
- **Resource Control**: Configurable concurrency and prefetch limits
- **Graceful Degradation**: Individual worker failures don't affect others

## 🔄 Message Processing

### Validation Message Flow

```text
1. API Service publishes ValidationMessage to 'validation.request'
2. Validation Worker consumes message from 'typechecking.validations.queue'
3. Worker processes file using Polars and validates against schema
4. Worker publishes results to 'validation.results.publish'
5. Worker updates task status in database via gRPC
```

### Schema Message Flow

```text
1. API Service publishes SchemaMessage to 'schemas.update'
2. Schema Worker consumes message from 'typechecking.schemas.queue'
3. Worker validates and stores schema in database
4. Worker publishes results to 'schemas.results.publish'
5. Worker updates task status in database via gRPC
```

## 💡 Usage Examples

### Worker Management

```python
from src.main import WorkerManager

# Create and start workers
manager = WorkerManager()
await manager.start_workers()  # Blocks until shutdown

# Graceful shutdown
manager.stop_workers()
```

### Custom Worker Configuration

```python
from src.workers.validation import ValidationWorker

# Create validation worker with custom settings
worker = ValidationWorker()
worker.start_consuming()  # Process validation messages
```

## 🔌 Integration Points

- **API Service**: Receives validation and schema messages via RabbitMQ
- **Database Service**: Stores schemas and results via gRPC protocol
- **RabbitMQ**: Message broker for asynchronous task processing
- **Protocol Buffers**: Typed interfaces for database operations

## 🤝 Dependencies

### Core Dependencies

- **polars**: High-performance dataframe library for file processing
- **jsonschema**: JSON schema validation library
- **pika**: RabbitMQ client for message consumption
- **fastapi**: For UploadFile compatibility and utilities
- **messaging-utils**: Internal library for RabbitMQ connections
- **proto-utils**: Internal library for gRPC database operations

### File Format Support

- **openpyxl**: Excel file processing (.xlsx, .xls)
- **polars[xlsx]**: Excel integration for Polars dataframes
- **CSV support**: Built-in Polars CSV reading capabilities

## Related Documentation

- [API Service](../api/): REST API that publishes messages to this service
- [Database Service](../../connections/database/): gRPC service for data storage
- [Messaging Utils](../../../packages/messaging-utils/): RabbitMQ connection library
- [Protocol Definitions](../../../packages/proto/): Shared interface specifications

<!-- A comment just to test github actions -->
