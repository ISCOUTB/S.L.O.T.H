# Application Core

This directory contains the core application code for the Typechecking ETL System. The application follows a modern, layered architecture with clear separation of concerns, type safety, and comprehensive documentation.

## Architecture Overview

The application is structured using a layered architecture pattern with dependency injection and clear boundaries:

```text
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                            │
│     (FastAPI routes, request/response handling,             │
│      OpenAPI documentation, middleware)                     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Controllers Layer                        │
│     (Business logic, validation orchestration,              │
│      schema management, user management)                    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Services Layer                          │
│     (File processing, data transformation,                  │
│      health checks, utility functions)                      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Data Access Layer                         │
│     (Database connections, caching, messaging,              │
│      configuration management)                              │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

- **Single Responsibility**: Each module has a clear, focused purpose
- **Dependency Injection**: Loose coupling through FastAPI's dependency system
- **Type Safety**: Comprehensive typing with Pydantic and TypedDict
- **Async First**: Non-blocking operations throughout the stack
- **Error Handling**: Consistent error propagation and recovery
- **Documentation**: Self-documenting code with comprehensive docstrings

## Directory Structure

The application follows a domain-driven design approach with clear module boundaries:

```text
app/
├── 🌐 api/                   # API layer - HTTP endpoints and routing
│   ├── main.py               # Main API router configuration
│   ├── deps.py               # Dependency injection container
│   ├── utils.py              # API utility functions
│   └── routes/               # API route definitions
│       ├── validation.py     # File validation endpoints
│       ├── schemas.py        # Schema management endpoints
│       ├── users.py          # User management endpoints
│       ├── login.py          # Authentication endpoints
│       ├── healthcheck.py    # Health check endpoints
│       └── cache.py          # Cache management endpoints
├── 🎯 controllers/           # Business logic layer
│   ├── __init__.py           # Controller exports
│   ├── validation.py         # Core validation orchestration
│   ├── schemas.py            # Schema management logic
│   ├── users.py              # User management logic
│   └── utils.py              # Controller utilities
├── ⚙️ core/                  # Infrastructure and configuration
│   ├── __init__.py           # Core module exports
│   ├── config.py             # Application configuration
│   ├── database_mongo.py     # MongoDB connection and operations
│   ├── database_redis.py     # Redis connection and caching
│   ├── database_sql.py       # PostgreSQL database operations
│   ├── init_db.py            # Database initialization
│   └── security.py           # Security utilities and JWT handling
├── 📨 messaging/             # Message queue system
│   ├── __init__.py           # Messaging exports
│   ├── connection_factory.py # RabbitMQ connection management
│   └── publishers.py         # Message publishers
├── 📋 schemas/               # Data models and type definitions
│   ├── __init__.py           # Schema exports
│   ├── api.py                # API request/response models
│   ├── controllers.py        # Controller data models
│   ├── messaging.py          # Message format definitions
│   ├── models.py             # Database model schemas
│   ├── services.py           # Service layer models
│   ├── token.py              # Authentication token models
│   ├── users.py              # User-related schemas
│   └── workers.py            # Worker process models
├── 🔧 services/              # Service layer - core business services
│   ├── __init__.py           # Service exports
│   ├── file_processor.py     # File reading and processing (Polars-based)
│   └── healthcheck.py        # System health checks
├── 👷 workers/               # Background processing
│   ├── __init__.py           # Worker exports
│   ├── schema_workers.py     # Schema processing workers
│   ├── validation_workers.py # File validation workers
│   ├── worker_manager.py     # Worker lifecycle management
│   └── utils.py              # Worker utilities
├── 🗄️ models/                # Database entity models (SQLAlchemy)
│   ├── __init__.py           # Model exports
│   ├── user_info.py          # User information model
│   └── user_roles.py         # User roles and permissions
├── 🔧 alembic/               # Database migrations
│   ├── env.py                # Alembic environment configuration
│   ├── script.py.mako        # Migration script template
│   └── versions/             # Migration versions
├── 📊 tests/                 # Test suite (currently empty)
├── initial_data.py           # Database initial data setup
├── main.py                   # Application entry point and ASGI app
└── postgres_prestart.py      # PostgreSQL pre-start checks
```

## 🔧 Core Components

### 🌐 API Layer (`api/`)

The API layer provides a robust REST interface using FastAPI with automatic documentation:

**Key Features:**

- **OpenAPI Integration**: Automatic API documentation at `/docs` and `/redoc`
- **Request Validation**: Pydantic-based input validation
- **Response Serialization**: Type-safe response formatting
- **Middleware Stack**: CORS, authentication, logging, and error handling
- **Dependency Injection**: Clean dependency management through FastAPI's DI system

**Endpoints Overview:**

```python
# Validation endpoints
POST   /api/v1/validation/upload/{import_name}    # File upload and validation
GET    /api/v1/validation/status                  # Task status tracking

# Schema management endpoints  
POST   /api/v1/schemas/upload/{import_name}       # Schema upload with versioning
GET    /api/v1/schemas/status                     # Schema operation status
DELETE /api/v1/schemas/remove/{import_name}       # Schema removal with rollback

# User management endpoints
GET    /api/v1/users/info                         # Get current user info
GET    /api/v1/users/search/{username}            # Search for users
POST   /api/v1/users/create                       # Create new user
PUT    /api/v1/users/update/{username}            # Update user information
DELETE /api/v1/users/delete/{username}            # Delete user

# Authentication endpoints
POST   /api/v1/login/access-token                 # User authentication
GET    /api/v1/login/test-token                   # Test token validity

# System monitoring
GET    /api/v1/healthcheck                        # Comprehensive health check
GET    /api/v1/healthcheck/simple                 # Basic availability check
GET    /api/v1/cache                              # Cache statistics
DELETE /api/v1/cache/clear                        # Cache management
```

### 🎯 Controllers Layer (`controllers/`)

The controllers orchestrate business logic and coordinate between services:

**Validation Controller** (`validation.py`):

- **File Processing Orchestration**: Manages the complete validation workflow
- **Parallel Processing**: Implements multi-threaded validation for performance
- **Error Aggregation**: Collects and structures validation errors
- **Progress Tracking**: Real-time status updates via Redis

**Schema Controller** (`schemas.py`):

- **Schema Lifecycle Management**: Upload, validation, versioning, and removal
- **Comparison Logic**: Intelligent schema diffing to prevent duplicates
- **Version Control**: Complete history with rollback capabilities
- **Active Schema Management**: Handles schema activation and deactivation

**User Controller** (`users.py`):

- **User Authentication**: Handles login and token validation
- **User Management**: CRUD operations for user accounts
- **Role-based Access**: Manages user roles and permissions
- **Cache Integration**: Redis-based caching for user data

### 🔧 Services Layer (`services/`)

Reusable business services that encapsulate domain logic:

**File Processor Service** (`file_processor.py`):

```python
class FileProcessor:
    """High-performance file processing service using Polars."""
    
    @staticmethod
    async def process_file(upload_file: UploadFile) -> Tuple[bool, Any, Optional[str]]:
        """
        Process uploaded files with format detection and optimization.
        
        Supported formats:
        - CSV: Fast parsing with automatic delimiter detection
        - XLSX: Excel files with multiple sheet support
        - XLS: Legacy Excel format support
        
        Returns:
            (success, data_frame, error_message)
        """
```

**Health Check Service** (`healthcheck.py`):

- **Service Monitoring**: MongoDB, Redis, RabbitMQ, PostgreSQL connectivity checks
- **Performance Metrics**: Response time and availability tracking
- **Dependency Validation**: Ensures all required services are operational

### ⚙️ Core Infrastructure (`core/`)

Manages system configuration and provides infrastructure abstractions:

**Configuration Management** (`config.py`):

```python
class Settings(BaseSettings):
    """Type-safe configuration with environment variable support."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"]
    
    # Performance Settings
    MAX_WORKERS: int = 8
    WORKER_CONCURRENCY: int = 4
    
    # Database Configuration
    MONGO_HOST: str = "localhost"
    REDIS_HOST: str = "localhost"
    RABBITMQ_HOST: str = "localhost"
    POSTGRES_HOST: str = "localhost"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
```

**Database Connections**:

- **MongoDB Client** (`database_mongo.py`): Schema storage with connection pooling
- **Redis Client** (`database_redis.py`): Caching and task status management  
- **PostgreSQL Client** (`database_sql.py`): User data and relational storage
- **Connection Management**: Automatic reconnection and health monitoring

### 📨 Messaging System (`messaging/`)

Implements robust asynchronous message processing:

**Connection Factory** (`connection_factory.py`):

```python
class ConnectionFactory:
    """Thread-safe RabbitMQ connection management."""
    
    @classmethod
    def get_connection(cls) -> pika.BlockingConnection:
        """Get or create thread-local connection with automatic recovery."""
        
    @classmethod
    def close_connections(cls) -> None:
        """Gracefully close all connections."""
```

**Message Publishers** (`publishers.py`):

- **Validation Publisher**: Publishes file validation requests with metadata
- **Schema Publisher**: Handles schema update and removal messages
- **Message Formatting**: Standardized JSON message structure with UUIDs
- **Priority Queuing**: Message priority system for optimal processing order

### 📋 Data Models (`schemas/`)

Type-safe data models using Pydantic for validation and serialization:

**Model Categories**:

- **API Schemas** (`api.py`): Request/response models for HTTP endpoints
- **Domain Models** (`models.py`): Core business object definitions  
- **Message Schemas** (`messaging.py`): Queue message format specifications
- **User Schemas** (`users.py`): User management and authentication models
- **Token Schemas** (`token.py`): JWT token structure definitions

**Type Safety Features**:

```python
# Strongly typed message contracts
class ValidationMessage(TypedDict):
    id: str                    # UUID task identifier
    task: ValidationTasks      # Literal task type ("sample_validation")
    timestamp: str             # ISO format timestamp
    file_data: str            # Hex-encoded binary data
    import_name: str          # Schema identifier
    metadata: dict            # File metadata
    priority: int             # Processing priority (1-10)
    date: str                 # Date of message creation


# Pydantic models for validation
class FileUploadResponse(BaseModel):
    task_id: str
    status: str
    message: str
    import_name: str
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "uuid-here",
                "status": "processing", 
                "message": "File validation started",
                "import_name": "user_data"
            }
        }
```

### 👷 Workers (`workers/`)

Background processing components with enhanced capabilities:

**Worker Architecture**:

- **Schema Workers**: Handle schema upload, validation, and removal operations
- **Validation Workers**: Process file validation requests asynchronously  
- **Worker Manager**: Orchestrates worker lifecycle and scaling
- **Message Acknowledgment**: Reliable message processing with proper ACK/NACK

**Schema Workers** (`schema_workers.py`):

```python
class SchemaWorkers:
    """Handles schema management operations."""
    
    async def process_schema_message(self, message: SchemaMessage) -> None:
        """
        Process schema operations:
        - upload_schema: Create/update schemas with validation
        - remove_schema: Remove schemas with version rollback
        
        Features:
        - JSON Schema Draft 7 validation
        - Version control with rollback
        - Redis status tracking
        - Error recovery and logging
        """
```

**Validation Workers** (`validation_workers.py`):

```python
class ValidationWorkers:
    """Processes file validation requests."""
    
    async def process_validation_message(self, message: ValidationMessage) -> None:
        """
        Process file validation:
        - Hex-to-binary conversion for safe data transmission
        - Multi-format file support (CSV, XLSX, XLS)
        - Parallel validation with progress tracking
        - Structured result publishing
        
        Performance features:
        - Async processing for non-blocking operations
        - Memory-efficient chunked processing
        - Real-time progress updates via Redis
        """
```

## Key Features

### File Processing

The system supports multiple spreadsheet formats:

```python
# Example: Processing different file types
from app.services.file_processor import FileProcessor

# Supports CSV, XLSX, XLS files
success, data, error = await FileProcessor.process_file(upload_file)
```

### Parallel Validation

Multi-threaded validation for performance:

```python
# Example: Parallel validation configuration
from app.controllers.validation import validate_file_against_schema

result = await validate_file_against_schema(
    file=upload_file,
    import_name="user_data",
    n_workers=4  # Configurable worker count
)
```

### Schema Management

Dynamic schema validation and versioning:

```python
# Example: Schema operations
from app.controllers.schemas import get_active_schema

schema = get_active_schema("user_data")  # Note: synchronous function
```

### Caching Strategy

Redis-based caching for improved performance:

- **Result Caching**: Validation results cached by task ID
- **Schema Caching**: Active schemas cached for quick access
- **TTL Management**: Configurable cache expiration times

### Message Queue Integration

Asynchronous processing with RabbitMQ:

- **Validation Queue**: File validation requests
- **Schema Queue**: Schema update operations  
- **Result Publishing**: Validation results broadcast
- **Dead Letter Queues**: Failed message handling

## Configuration

### Environment Variables

Key configuration options:

```bash
# RabbitMQ configuration
RABBITMQ_HOST="localhost"
RABBITMQ_PORT="5672"
RABBITMQ_VHOST="/"
RABBITMQ_USER="guest"
RABBITMQ_PASSWORD="guest"

# Worker configuration
MAX_WORKERS=8
WORKER_CONCURRENCY=4
WORKER_PREFETCH_COUNT=1

# API configuration
API_V1_STR="/api/v1"
CORS_ORIGINS="*"

# MongoDB configuration
MONGO_PORT="27017"
MONGO_HOST="localhost"
MONGO_INITDB_ROOT_USERNAME="admin"
MONGO_INITDB_ROOT_PASSWORD="admin"
MONGO_DB="json_schemas"
MONGO_COLLECTION="schemas"

# Redis configuration
REDIS_PASSWORD="root"
REDIS_PORT="6379"
REDIS_HOST="localhost"
```

### Database Schema

MongoDB collections:

- `schemas`: Active JSON schemas
- `schema_releases`: Schema version history
- `validation_results`: Validation result cache

Redis keys:

- `task:{task_id}`: Validation task results
- `schema:{import_name}`: Cached schemas
- `import:{import_name}`: Import metadata

## Development Guidelines

### Adding New Endpoints

1. Define Pydantic models in `schemas/api.py`
2. Create route handler in `api/routes/`
3. Implement business logic in `controllers/`
4. Add services in `services/` if needed
5. Update tests

### Error Handling

Use standardized error responses:

```python
from fastapi import HTTPException
from app.schemas.api import ApiResponse

# Standard error response
raise HTTPException(400, "Validation failed")

# Structured API response
return ApiResponse(
    status="error",
    code=400,
    message="Validation failed",
    data={"errors": validation_errors}
)
```

### Logging

Use structured logging throughout:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Processing validation request", extra={
    "task_id": task_id,
    "import_name": import_name,
    "file_size": file_size
})
```

### Testing

- Unit tests for individual components (planned)
- Integration tests for API endpoints (planned)  
- Performance benchmarks available in `../tests/testing_typechecking.ipynb`
- Mock external dependencies for testing

## Performance Considerations

### Optimization Strategies

1. **Parallel Processing**: Configurable worker threads
2. **Chunked Processing**: Memory-efficient large file handling
3. **Caching**: Redis-based result and schema caching
4. **Connection Pooling**: Efficient database connections
5. **Async Operations**: Non-blocking I/O operations

### Memory Management

- Stream processing for large files
- Garbage collection optimization
- Connection pooling limits
- Cache size management

### Monitoring

- Health check endpoints
- Performance metrics collection
- Error rate monitoring
- Queue depth monitoring

## Extension Points

The architecture supports easy extension:

1. **New File Formats**: Add processors in `services/file_processor.py`
2. **Custom Validation Rules**: Extend validation logic in `controllers/`
3. **Additional Databases**: Add connections in `core/`
4. **New Message Types**: Define in `schemas/messaging.py`
5. **Worker Types**: Add new workers in `workers/`

## Troubleshooting

Common issues and solutions:

1. **Connection Issues**: Check database/queue connectivity
2. **Memory Issues**: Reduce worker count or chunk size
3. **Validation Errors**: Check schema format and data compatibility
4. **Performance Issues**: Monitor worker utilization and queue depth

## Recent Updates

### API Layer Enhancements

#### Schema Management Routes (`api/routes/schemas.py`)

- **Upload Schema Endpoint**: New `POST /upload/{import_name}` endpoint with advanced features:
  - Support for both raw and processed schema formats
  - Cache-first strategy with `new` parameter to bypass caching
  - Asynchronous processing with task ID tracking
  - Automatic schema comparison to prevent duplicate uploads
  
- **Schema Status Tracking**: Enhanced `GET /status` endpoint:
  - Query by task_id or import_name
  - Returns detailed task information and progress
  - Support for multiple task tracking per import_name
  
- **Schema Removal**: New `DELETE /remove/{import_name}` endpoint:
  - Safe schema removal with version rollback
  - Asynchronous processing with result tracking
  - Maintains schema history for rollback operations

#### Validation Routes (`api/routes/validation.py`)

- **File Upload Processing**: Enhanced `POST /upload/{import_name}` endpoint:
  - Multi-format file support (CSV, XLSX, XLS)
  - Rich metadata extraction (filename, content_type, size)
  - Hex-encoded file data for reliable transmission
  - Asynchronous validation with progress tracking
  
- **Validation Status**: Improved `GET /status` endpoint:
  - Real-time validation progress monitoring
  - Task lookup by task_id or import_name
  - Comprehensive error handling and reporting

### Controller Layer Improvements

#### Schema Controller (`controllers/schemas.py`)

- **Schema Comparison Logic**: Enhanced `compare_schemas()` function for accurate equality checking
- **Data Validation**: Improved `validate_data_chunk()` with comprehensive error reporting
- **Active Schema Management**: Robust `get_active_schema()` and `save_schema()` functions
- **Schema Versioning**: New `remove_schema()` function with rollback capabilities
- **Raw Schema Processing**: Enhanced `create_schema()` with support for raw and processed formats

### Infrastructure Layer Updates

#### Redis Integration (`core/database_redis.py`)

- **Advanced Task Management**: Comprehensive task tracking system:
  - Task status updates with field-level granularity
  - Import name indexing for efficient task lookup
  - Multi-task support per import name
  - Cache expiration and cleanup mechanisms
  
- **Enhanced Data Structures**: Optimized Redis operations:
  - Hash-based task storage for atomic updates
  - Set-based import name indexing
  - JSON serialization for complex data types
  - Connection pooling and error handling

#### Messaging System (`messaging/publishers.py`)

- **ValidationPublisher Enhancements**:
  - Detailed message documentation and schemas
  - Priority-based message queuing
  - Hex-encoded file data transmission
  - Comprehensive metadata support
  - UUID-based task identification
  
- **Message Formatting**: Standardized message structure:
  - ISO timestamp formatting
  - Persistent delivery mode
  - Priority-based routing
  - Structured error handling

### Schema Layer Updates

#### Messaging Schemas (`schemas/messaging.py`)

- **TypedDict Implementation**: Strongly typed message contracts:
  - `ValidationMessage` schema for file validation requests
  - `SchemaMessage` schema for schema update operations
  - Literal types for task classification
  - Comprehensive field documentation
  
- **Message Standards**: Defined message structure standards:
  - Unique task identification
  - Timestamp consistency
  - Priority system implementation
  - Metadata standardization

### Worker Layer Enhancements

#### Schema Workers (`workers/schema_workers.py`)

- **Enhanced Processing Pipeline**:
  - Improved schema creation and validation logic
  - Real-time Redis status updates
  - Comprehensive error handling and logging
  - Proper message acknowledgment patterns
  
- **Connection Management**: Thread-safe RabbitMQ operations:
  - Connection factory integration
  - Graceful shutdown handling
  - QoS configuration for optimal throughput
  - Error recovery mechanisms

#### Validation Workers (`workers/validation_workers.py`)

- **File Processing Improvements**:
  - Enhanced hex-to-binary conversion
  - UploadFile object creation from binary data
  - Asynchronous validation processing
  - Structured result publishing
  
- **Progress Tracking**: Real-time validation monitoring:
  - Step-by-step progress updates
  - Detailed error reporting
  - Result summarization
  - Cache integration for status persistence

### Performance Optimizations

- **Caching Strategy**: Multi-level caching with Redis
- **Async Processing**: Non-blocking operations throughout the pipeline
- **Connection Pooling**: Efficient resource utilization
- **Message Queuing**: Priority-based task distribution
- **Memory Management**: Optimized data structures and garbage collection

### API Consistency

- **Standardized Responses**: Consistent ApiResponse format across all endpoints
- **Error Handling**: Uniform error response structure
- **Status Codes**: HTTP status code standardization
- **Documentation**: Comprehensive endpoint documentation with examples

### Message Queue System

#### Enhanced Message Schemas (`schemas/messaging.py`)

The system now uses strongly typed message contracts for reliable communication:

##### ValidationMessage Schema

```python
class ValidationMessage(TypedDict):
    """Message format for file validation requests"""
    id: str                    # Unique task identifier (UUID)
    task: ValidationTasks      # Task type: "sample_validation"
    timestamp: str             # ISO format timestamp
    file_data: str            # Hex-encoded binary file content
    import_name: str          # Schema identifier for validation
    metadata: dict            # File metadata (filename, content_type, size)
    priority: int             # Message priority (1-10)
```

**Usage Example:**

```python
# Publishing a validation request
task_id = publisher.publish_validation_request(
    file_data=file_content,
    import_name="user_schema",
    metadata={
        "filename": "users.csv",
        "content_type": "text/csv",
        "size": 1024,
        "priority": 5
    },
    task="sample_validation"
)
```

##### SchemaMessage Schema

```python
class SchemaMessage(TypedDict):
    """Message format for schema update requests"""
    id: str                    # Unique task identifier (UUID)
    task: SchemasTasks        # Task type: "upload_schema" | "remove_schema"
    timestamp: str             # ISO format timestamp
    schema: dict              # JSON schema definition
    import_name: str          # Schema identifier
    raw: bool                 # Raw format flag
```

**Usage Example:**

```python
# Publishing a schema update
task_id = publisher.publish_schema_update(
    schema={
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"]
    },
    import_name="person_schema",
    raw=False,
    task="upload_schema"
)
```

#### Enhanced Publishers (`messaging/publishers.py`)

##### ValidationPublisher

- **Hex Encoding**: File data converted to hexadecimal for safe JSON transmission
- **Priority Queuing**: Message priority system for processing order optimization
- **Persistent Delivery**: Messages marked as persistent for reliability
- **UUID Generation**: Unique task identifiers for tracking
- **Routing Keys**: Optimized message routing (`validation.request`)

##### Message Publishing Flow

```python
# Internal message creation and publishing
message: ValidationMessage = {
    "id": str(uuid.uuid4()),
    "task": task,
    "timestamp": datetime.now().isoformat(),
    "file_data": file_data.hex(),  # Hex encoding for safe transmission
    "import_name": import_name,
    "metadata": metadata,
    "priority": metadata.get("priority", 5),
}

# Publish with properties
channel.basic_publish(
    exchange="typechecking.exchange",
    routing_key="validation.request",
    body=json.dumps(message),
    properties=pika.BasicProperties(
        message_id=task_id,
        timestamp=int(datetime.now().timestamp()),
        delivery_mode=pika.DeliveryMode.Persistent,
        priority=message["priority"],
    ),
)
```

#### Queue Infrastructure

- **Validation Queue**: `typechecking.validation.queue` for file validation requests
- **Schema Queue**: `typechecking.schema.queue` for schema management operations
- **Exchange**: `typechecking.exchange` with topic routing
- **Dead Letter Queues**: Automatic failure handling and message requeuing
- **Priority Support**: Message priority levels for processing optimization

#### Connection Management (`messaging/connection_factory.py`)

- **Thread Safety**: Separate connections per worker thread
- **Connection Pooling**: Efficient resource utilization
- **Automatic Reconnection**: Robust connection recovery
- **Graceful Shutdown**: Proper connection cleanup

---

## Current Implementation Status

This README reflects the actual current state of the application as of the latest updates:

### Implemented Features

- **Complete API Layer**: All endpoints implemented with FastAPI
- **User Management**: Full authentication and user CRUD operations
- **Schema Management**: Upload, versioning, and removal with rollback
- **File Validation**: Multi-format support with async processing
- **Message Queue System**: RabbitMQ integration with typed contracts
- **Database Layer**: MongoDB, Redis, and PostgreSQL integration
- **Worker System**: Background processing for validation and schema tasks

### Areas for Development

- **Unit Testing**: Test suite is planned but not yet implemented
- **Performance Optimization**: Additional caching and optimization strategies
- **Monitoring**: Enhanced metrics collection and observability
- **Documentation**: API examples and integration guides

### Architecture Notes

- Uses **Polars** for high-performance data processing
- Implements **SQLAlchemy** models for PostgreSQL operations
- Follows **Domain-Driven Design** principles
- Emphasizes **type safety** with Pydantic and TypedDict
- Supports **horizontal scaling** through worker processes

This documentation is maintained to accurately reflect the codebase and is updated with each major feature release.
