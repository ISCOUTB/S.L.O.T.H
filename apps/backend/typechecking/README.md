# Typechecking ETL System

A high-performance, enterprise-grade data validation system designed for ETL processes that validates spreadsheet files (CSV, XLSX, XLS) against JSON schemas using parallel processing, message queuing, and modern distributed architecture patterns.

## 🚀 Overview

This system provides a robust, scalable solution for validating large datasets in spreadsheet formats. Built with modern Python technologies, it employs a microservices architecture with RabbitMQ for asynchronous processing, MongoDB for schema management, Redis for caching, PostgreSQL for user management, and FastAPI for a high-performance REST API interface. The system uses Polars for high-performance data processing and supports comprehensive user authentication and authorization.

## ✨ Key Features

- **🔄 Multi-format Support**: Validates CSV, XLSX, and XLS files with intelligent parsing using Polars
- **⚡ Parallel Processing**: Uses multi-threading and async operations for high-performance validation
- **🔀 Asynchronous Processing**: RabbitMQ-based message queuing for scalable operations
- **📋 Schema Management**: Dynamic JSON schema validation with versioning and rollback support
- **� User Management**: Complete authentication system with JWT tokens and role-based access control
- **�💾 Intelligent Caching**: Redis-based caching with TTL management for improved performance
- **🌐 RESTful API**: FastAPI-based endpoints with automatic OpenAPI documentation
- **🐳 Docker Support**: Containerized deployment with Docker Compose for easy setup
- **📊 Performance Testing**: Built-in benchmarking and performance analysis tools with Jupyter notebooks
- **🔒 Type Safety**: Comprehensive Pydantic models and TypedDict schemas
- **📈 Real-time Monitoring**: Task progress tracking and system health monitoring

## Architecture

The system follows a modern microservices architecture with clear separation of concerns:

```text
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   FastAPI       │────▶│   RabbitMQ      │────▶│   Workers       │
│   Web Server    │     │   Message Queue │     │   (Validation + │
│   (REST API)    │     │   (Async Jobs)  │     │    Schema Mgmt) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                                                │
         ▼                                                ▼
┌─────────────────┐                              ┌─────────────────┐
│   Redis         │                              │   MongoDB       │
│   (Caching +    │                              │   (JSON Schemas │
│   Task Status)  │                              │   + Metadata)   │
└─────────────────┘                              └─────────────────┘
         │                                                
         ▼                                                
┌─────────────────┐                              
│   PostgreSQL    │                              
│   (User Mgmt +  │                              
│   Application   │                              
│   Data)         │                              
└─────────────────┘                              
```

### Component Responsibilities

- **FastAPI Server**: HTTP API endpoints, request validation, response formatting, authentication
- **RabbitMQ**: Message queuing, task distribution, async processing coordination
- **Workers**: File validation, schema processing, parallel computation (ValidationWorker, SchemaWorker)
- **Redis**: Result caching, task status tracking, session management
- **MongoDB**: JSON schema storage, metadata persistence, version control
- **PostgreSQL**: User management, authentication data, application configuration

## 📋 Prerequisites

- **Python**: 3.12+ (with `uv` package manager recommended)
- **Docker**: Latest version with Docker Compose
- **MongoDB**: 7.0+ (provided via Docker)
- **Redis**: 7.4+ (provided via Docker)
- **RabbitMQ**: 4.0+ with management plugin (provided via Docker)
- **PostgreSQL**: 17+ (provided via Docker)

## 🚀 Quick Start

### Using Docker Compose (Recommended)

- Clone the repository:

```bash
git clone https://github.com/ISCOUTB/etl-design.git
cd etl-design/typechecking
```

- Edit environment file:

```bash
cp .env.example .env
# Edit .env with your specific configuration
```

- Start the services:

```bash
docker-compose up --build -d
```

### Manual Installation

- Install dependencies:

```bash
uv sync

# Activate Virtual Environment
source .venv/bin/activate
```

- Start workers:

```bash
cd backend
python -m app.workers.worker_manager
```

- Start the API server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔌 API Endpoints

The system provides a comprehensive REST API with automatic OpenAPI documentation available at `/docs`.

### 📄 File Validation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/validation/upload/{import_name}` | Upload and validate spreadsheet files |
| `GET` | `/api/v1/validation/status` | Check validation task status and progress |

### 🏷️ Schema Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/schemas/upload/{import_name}` | Upload JSON schema with versioning |
| `GET` | `/api/v1/schemas/status` | Get schema upload status and metadata |
| `DELETE` | `/api/v1/schemas/remove/{import_name}` | Remove schema with rollback support |

### 👥 User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/users/info` | Get current user information |
| `GET` | `/api/v1/users/search/{username}` | Get specific user details |
| `GET` | `/api/v1/users/search` | List all users (paginated) |
| `POST` | `/api/v1/users/create` | Create new user |
| `PATCH` | `/api/v1/users/update/{username}` | Update user information |
| `DELETE` | `/api/v1/users/delete/{username}` | Delete user |

### 🔐 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/login/access-token` | Login and get JWT access token |
| `GET` | `/api/v1/login/test-token` | Test token validity |

### 🏥 System Health & Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/healthcheck` | Comprehensive health check of all services |
| `GET` | `/api/v1/healthcheck/simple` | Basic API availability check |

### 💾 Cache Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/cache` | Get cache statistics and stored keys |
| `DELETE` | `/api/v1/cache/clear` | Clear all cached data |

## 💡 Usage Examples

### Complete Workflow Example

#### 1. Authenticate and Get Access Token

```bash
# Login to get access token
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin&rol=admin"
```

#### 2. Upload a JSON Schema

```bash
# Create a user schema
cat > user_schema.json << EOF
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "email": {"type": "string", "format": "email"},
    "age": {"type": "integer", "minimum": 0}
  },
  "required": ["name", "email"]
}
EOF

# Upload the schema
curl -X POST "http://localhost:8000/api/v1/schemas/upload/user_data" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <your_token>" \
     -d @user_schema.json
```

#### 3. Validate a CSV File

```bash
# Create sample data
cat > users.csv << EOF
name,email,age
John Doe,john@example.com,30
Jane Smith,jane@example.com,25
EOF

# Validate the file
curl -X POST "http://localhost:8000/api/v1/validation/upload/user_data" \
     -H "Content-Type: multipart/form-data" \
     -H "Authorization: Bearer <your_token>" \
     -F "spreadsheet_file=@users.csv"
```

#### 4. Check Validation Status

```bash
# Get status by task ID
curl -H "Authorization: Bearer <your_token>" \
     "http://localhost:8000/api/v1/validation/status?task_id=<task_id>"

# Or get status by import name
curl -H "Authorization: Bearer <your_token>" \
     "http://localhost:8000/api/v1/validation/status?import_name=user_data"
```

### Advanced Features

#### User Management

```bash
# Create a new user
curl -X POST "http://localhost:8000/api/v1/users/create" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <admin_token>" \
     -d '{
       "username": "newuser",
       "password": "password123",
       "rol": "user",
       "is_active": true
     }'

# Get user information
curl -H "Authorization: Bearer <your_token>" \
     "http://localhost:8000/api/v1/users/search/newuser"
```

#### Schema Versioning

```bash
# Upload new version of schema
curl -X POST "http://localhost:8000/api/v1/schemas/upload/user_data?new=true" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <your_token>" \
     -d @updated_schema.json

# Remove schema (with rollback)
curl -X DELETE "http://localhost:8000/api/v1/schemas/remove/user_data" \
     -H "Authorization: Bearer <your_token>"
```

#### Performance Monitoring

```bash
# Check system health
curl -H "Authorization: Bearer <your_token>" \
     "http://localhost:8000/api/v1/healthcheck"

# View cache statistics
curl -H "Authorization: Bearer <your_token>" \
     "http://localhost:8000/api/v1/cache"

# Clear cache
curl -X DELETE -H "Authorization: Bearer <your_token>" \
     "http://localhost:8000/api/v1/cache/clear"
```

## ⚙️ Configuration

The system uses environment variables for configuration with sensible defaults. Create a `.env` file based on `.env.example`.

### Core Settings

```bash
# API Configuration
API_V1_STR="/api/v1"
CORS_ORIGINS="*"

# Performance Settings
MAX_WORKERS=8
WORKER_CONCURRENCY=4
WORKER_PREFETCH_COUNT=1
```

### Database Configuration

```bash
# MongoDB Settings
MONGO_HOST="localhost"
MONGO_PORT="27017"
MONGO_INITDB_ROOT_USERNAME="admin"
MONGO_INITDB_ROOT_PASSWORD="admin"
MONGO_DB="json_schemas"
MONGO_COLLECTION="schemas"

# Redis Settings
REDIS_HOST="localhost"
REDIS_PORT="6379"
REDIS_PASSWORD="root"
REDIS_EXPIRE_SECONDS=300

# RabbitMQ Settings
RABBITMQ_HOST="localhost"
RABBITMQ_PORT="5672"
RABBITMQ_VHOST="/"
RABBITMQ_USER="guest"
RABBITMQ_PASSWORD="guest"
```

## 🚀 Performance & Benchmarks

The system is engineered for high-performance data validation with several optimization strategies.

### Performance Features

- **🔄 Parallel Processing**: Multi-threaded validation with configurable worker pools
- **📦 Chunked Processing**: Memory-efficient handling of large files using Polars
- **⚡ Asynchronous Architecture**: Non-blocking operations through aio-pika and message queuing
- **💾 Intelligent Caching**: Redis-based caching with optimized data structures
- **🔧 Connection Pooling**: Efficient database connection management
- **📊 Real-time Monitoring**: Task progress tracking and performance metrics

### Optimization Strategies

#### Scaling Configuration

```bash
# Increase worker threads for CPU-intensive tasks
MAX_WORKERS=16
WORKER_CONCURRENCY=8
```

#### Performance Tuning

- **CPU Optimization**: Adjust `MAX_WORKERS` based on available cores (default: 8)
- **Memory Optimization**: Configure worker concurrency for large file processing (default: 4)
- **Network Optimization**: Use connection pooling and persistent connections
- **Cache Optimization**: Fine-tune Redis TTL and eviction policies (default: 300 seconds)
- **File Processing**: Polars-based processing for optimal memory usage and speed

### Monitoring Metrics

The system provides comprehensive performance monitoring:

- **Processing Time**: Track validation duration per file
- **Memory Usage**: Monitor peak memory consumption
- **Queue Depth**: RabbitMQ queue length monitoring
- **Cache Hit Rate**: Redis cache effectiveness metrics
- **Error Rates**: Track validation success/failure ratios

## 🛠️ Development

### Project Structure

```text
typechecking/backend/
├── app/                     # Main application code
│   ├── api/                # FastAPI routes and endpoints
│   │   ├── main.py         # API router configuration
│   │   ├── deps.py         # Dependency injection
│   │   ├── utils.py        # API utilities
│   │   └── routes/         # Route definitions
│   │       ├── validation.py   # File validation endpoints
│   │       ├── schemas.py      # Schema management endpoints
│   │       ├── users.py        # User management endpoints
│   │       ├── login.py        # Authentication endpoints
│   │       ├── healthcheck.py  # Health check endpoints
│   │       └── cache.py        # Cache management endpoints
│   ├── controllers/        # Business logic layer
│   ├── core/              # Configuration and database connections
│   ├── messaging/         # RabbitMQ message handling
│   ├── models/            # SQLAlchemy database models
│   ├── schemas/           # Pydantic models and type definitions
│   ├── services/          # Reusable business services
│   │   ├── file_processor.py   # Polars-based file processing
│   │   └── healthcheck.py      # System health checks
│   └── workers/           # Background processing workers
│       ├── validation_workers.py   # File validation workers
│       ├── schema_workers.py       # Schema processing workers
│       ├── worker_manager.py       # Worker lifecycle management
│       └── utils.py               # Worker utilities
├── tests/                 # Test files and performance benchmarks
│   ├── testing_typechecking.ipynb # Performance testing notebook
│   ├── testing_typechecking.py    # Performance test implementation
│   ├── data/              # Test data files (CSV, Excel)
│   └── figures/           # Performance visualization results
├── static/               # Sample data files for testing
├── docker-compose.yml    # Docker services configuration
├── pyproject.toml        # Python project configuration
└── README.md            # This documentation
```
