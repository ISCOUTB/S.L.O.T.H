# ETL Design API Service

A comprehensive FastAPI-based REST API that serves as the main interface for the ETL Design system. This service handles user authentication, file validation requests, schema management, and communication with backend processing services.

## 🚀 Overview

The API Service is the primary entry point for users and external applications to interact with the ETL Design system. It provides a complete REST API with authentication, user management, file upload capabilities, and real-time status tracking for validation and schema operations.

## ✨ Key Features

- **🔐 Authentication & Authorization**: JWT-based authentication with role-based access control
- **👥 User Management**: Complete CRUD operations for user accounts with admin controls
- **📋 Schema Management**: Upload, update, and remove JSON schemas with versioning support
- **📄 File Validation**: Upload spreadsheet files (CSV, XLSX, XLS) for validation against schemas
- **🏗️ Excel Parsing Workflow**: Orchestrates complete ETL process from validation to SQL generation
- **💾 Intelligent Caching**: Redis-based response caching for improved performance
- **🔄 Asynchronous Processing**: RabbitMQ integration for background task processing
- **🌐 REST API**: Comprehensive endpoints with automatic OpenAPI documentation
- **🏥 Health Monitoring**: System health checks and status endpoints
- **🔒 Type Safety**: Full Pydantic model validation and type checking

## Architecture

The API Service acts as the communication layer between users and the processing backend:

```text
┌─────────────────┐     ┌─────────────────┐             ┌─────────────────┐
│   Client Apps   │────▶│   API Service   │────────────▶│   RabbitMQ      │
│   (Web/Mobile)  │     │   (FastAPI)     │             │   (Publisher)   │
└─────────────────┘     └─────────────────┘             └─────────────────┘
                                │                                 │
                        ┌───────┼───────────┐                     ▼
                        ▼                   ▼                ┌─────────────────┐
                ┌─────────────────┐ ┌─────────────────┐  │  Typechecking   │
                │  Database Svc   │ │   PostgreSQL    │  │   Workers       │
                │  (gRPC Proxy)   │ │ (Direct SQLAlch)│  └─────────────────┘
                └─────────────────┘ └─────────────────┘
                        │                    ▲
                        ▼                    │
                ┌─────────────────┐          │
                │ Redis + MongoDB │          │
                └─────────────────┘          │
                                             │
                                   ┌─────────┴─────────┐
                                   │ User Management,  │
                                   │ Authentication,   │
                                   │ Application Data  │
                                   └───────────────────┘
```

### Data Flow Separation

- **Cache & Schemas**: API ↔ Database Service (gRPC) ↔ Redis/MongoDB  
- **Users & Auth**: API ↔ PostgreSQL (Direct SQLAlchemy)

## 🏗️ ETL Workflow Orchestration

The API Service orchestrates the complete ETL process from file validation to SQL generation. This workflow integrates typechecking validation with excel parsing services to provide end-to-end data transformation.

### Complete ETL Pipeline

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   File Upload   │───▶│   Validation    │───▶│ Excel Parsing   │
│   (API Service) │    │ (Typechecking)  │    │   (Parsers)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Schema Check   │    │ Data Validation │    │ SQL Generation  │
│  (Database Svc) │    │  (Polars/JSON)  │    │ (DDL + INSERT)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Workflow Stages

1. **📄 File Upload & Schema Validation**
   - API receives Excel/CSV file upload
   - Validates file format and basic structure
   - Checks if corresponding JSON schema exists

2. **🔍 Data Validation (via Typechecking)**
   - API publishes validation message to RabbitMQ
   - Typechecking workers validate data against schema
   - Results include detailed validation reports

3. **🏗️ Excel Parsing Pipeline** *(Planned Integration)*
   - **Formula Extraction**: Parse Excel formulas and dependencies
   - **DDL Generation**: Create table definitions from validated data
   - **SQL Building**: Generate INSERT statements from clean data
   - **Result Consolidation**: Return complete SQL package

### Future ETL Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/etl/process/{import_name}` | Complete ETL: validation + parsing + SQL |
| `GET` | `/api/v1/etl/status/{task_id}` | Track ETL pipeline progress |
| `GET` | `/api/v1/etl/results/{task_id}` | Download generated SQL files |
| `POST` | `/api/v1/etl/validate-and-parse` | Two-stage validation then parsing |

### Integration Points

- **Typechecking Service**: Data validation and schema compliance
- **Excel Reader**: Formula extraction and data processing
- **Formula Parser**: Complex formula dependency analysis  
- **DDL Generator**: Database schema generation
- **SQL Builder**: INSERT statement generation

**Note**: The excel parsing integration is currently in development. The API Service will serve as the orchestration layer that coordinates the workflow between validation (typechecking) and parsing (excel-reader) services.

## 🔌 API Endpoints

The API provides comprehensive REST endpoints with automatic OpenAPI documentation available at `/docs`.

### 🔐 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/login/access-token` | Login and get JWT access token |
| `GET` | `/api/v1/login/test-token` | Test token validity |

### 👥 User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/users/info` | Get current user information |
| `GET` | `/api/v1/users/search/{username}` | Get specific user details |
| `GET` | `/api/v1/users/search` | List all users (paginated) |
| `POST` | `/api/v1/users/create` | Create new user |
| `PATCH` | `/api/v1/users/update/{username}` | Update user information |
| `DELETE` | `/api/v1/users/delete/{username}` | Delete user |

### 🏷️ Schema Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/schemas/upload/{import_name}` | Upload JSON schema with versioning |
| `GET` | `/api/v1/schemas/status` | Get schema upload status and metadata |
| `DELETE` | `/api/v1/schemas/remove/{import_name}` | Remove schema with rollback support |

### 📄 File Validation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/validation/upload/{import_name}` | Upload and validate spreadsheet files |
| `GET` | `/api/v1/validation/status` | Check validation task status and progress |

### 💾 Cache Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/cache` | Get cache statistics and stored keys |
| `DELETE` | `/api/v1/cache/clear` | Clear all cached data |

### 🏥 Health & Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Basic health check with service status |
| `GET` | `/health/detailed` | Detailed health info including dependencies |
| `GET` | `/metrics` | Application metrics for monitoring systems |

## 💡 Usage Examples

### Authentication Flow

```bash
# Login to get access token
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin&rol=admin"

# Use token for authenticated requests
export TOKEN="<your_access_token>"
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/users/info"
```

### Schema Management

```bash
# Upload a JSON schema
curl -X POST "http://localhost:8000/api/v1/schemas/upload/user_data" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "type": "object",
       "properties": {
         "name": {"type": "string"},
         "email": {"type": "string", "format": "email"},
         "age": {"type": "integer", "minimum": 0}
       },
       "required": ["name", "email"]
     }'

# Check schema status
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/schemas/status?import_name=user_data"
```

### File Validation

```bash
# Upload and validate a CSV file
curl -X POST "http://localhost:8000/api/v1/validation/upload/user_data" \
     -H "Authorization: Bearer $TOKEN" \
     -F "spreadsheet_file=@users.csv"

# Check validation status
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/validation/status?import_name=user_data"
```

### User Management

```bash
# Create a new user
curl -X POST "http://localhost:8000/api/v1/users/create" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "newuser",
       "email": "newuser@example.com",
       "full_name": "New User",
       "password": "securepassword"
     }'

# Get user information
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/users/search/newuser"
```

## ⚙️ Configuration

The service uses environment variables for configuration. Create a `.env` file based on `.env.example`.

### API Configuration

```bash
# Server Settings
SERVER_HOST="localhost"
SERVER_PORT=8000
SERVER_DEBUG=false
API_V1_STR="/api/v1"
CORS_ORIGINS="http://localhost,http://localhost:3000,http://localhost:8000"

# Security
SECRET_KEY="your_secret_key_here"
FIRST_SUPERUSER="admin"
FIRST_SUPERUSER_PASSWORD="admin_password"

# Health Monitoring
HEALTH_CHECK_ENABLED=true
HEALTH_ENDPOINTS_INCLUDE_DETAILED=true
```

### Database Configuration

```bash
# PostgreSQL (User Management - Direct Connection)
POSTGRES_HOST="localhost"
POSTGRES_PORT=5432
POSTGRES_USER="admin"
POSTGRES_PASSWORD="admin"
POSTGRES_DB="typechecking_db"

# Database Service (gRPC - Redis/MongoDB Operations)
DATABASE_CONNECTION_HOST="localhost"
DATABASE_CONNECTION_PORT=50050
```

### RabbitMQ Configuration

```bash
# RabbitMQ Publishing
RABBITMQ_HOST="localhost"
RABBITMQ_PORT=5672
RABBITMQ_USER="admin"
RABBITMQ_PASSWORD="admin"
RABBITMQ_VHOST="/"

# Worker Configuration
MAX_WORKERS=4
WORKER_CONCURRENCY=4
WORKER_PREFETCH_COUNT=1

# Exchange and Queues
RABBITMQ_EXCHANGE="typechecking.exchange"
RABBITMQ_EXCHANGE_TYPE="topic"
RABBITMQ_QUEUE_SCHEMAS="typechecking.schemas.queue"
RABBITMQ_QUEUE_VALIDATIONS="typechecking.validations.queue"

# Publishing Routing Keys
RABBITMQ_PUBLISHERS_ROUTING_KEY_SCHEMAS="schemas.update"
RABBITMQ_PUBLISHERS_ROUTING_KEY_VALIDATIONS="validation.request"
```

## 🛠️ Development

### Prerequisites

- Python 3.12+
- PostgreSQL 17+
- RabbitMQ 4.0+
- Database Service running

### Installation

```bash
# Install dependencies
uv sync

# Run database migrations
uv run alembic upgrade head

# Create initial data
uv run python -m src.initial_data
```

Or just running the script [prestart.sh](./scripts/prestart.sh).

### Running the Service

```bash
# Development mode
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## 🏗️ Project Structure

```text
api/
├── src/
│   ├── api/               # FastAPI routes and dependencies
│   │   ├── routes/        # API endpoint definitions
│   │   ├── deps.py        # Dependency injection
│   │   ├── main.py        # Router configuration
│   │   └── utils.py       # API utilities
│   ├── controllers/       # Business logic layer
│   ├── core/             # Configuration and database
│   ├── messaging/        # RabbitMQ publisher
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic models
│   ├── utils/            # Utility functions
│   └── main.py           # Application entry point
├── scripts/              # Deployment scripts
├── logs/                 # Application logs
└── alembic/             # Database migrations
```

## 🔄 Communication Flow

### Request Processing

1. **Client Request**: HTTP request to FastAPI endpoint
2. **Authentication**: JWT token validation and user authorization
3. **Business Logic**: Controllers handle business rules and validation
4. **Database Operations**: Via Database Service (gRPC) or direct SQL
5. **Message Publishing**: Async tasks sent to RabbitMQ
6. **Response**: Immediate response with task ID for tracking

### Background Processing

1. **Message Publishing**: API publishes to RabbitMQ queues
2. **Worker Consumption**: Typechecking service consumes messages
3. **Status Updates**: Workers update task status via Database Service
4. **Result Retrieval**: Clients poll status endpoints for completion

### ETL Pipeline Processing *(Future)*

1. **File Upload**: Client uploads Excel/CSV file with schema reference
2. **Validation Stage**: API coordinates validation via Typechecking service
3. **Parsing Stage**: API coordinates Excel parsing via Parser services
4. **SQL Generation**: DDL Generator and SQL Builder create database scripts
5. **Result Delivery**: Complete SQL package returned to client

## 🤝 Integration Points

- **Database Service**: gRPC client for Redis/MongoDB operations
- **Typechecking Service**: RabbitMQ message publishing for async processing
- **Excel Reader Service**: *(Planned)* REST/gRPC communication for file parsing
- **Formula Parser Service**: *(Planned)* Complex formula analysis integration
- **DDL Generator Service**: *(Planned)* Database schema generation
- **SQL Builder Service**: *(Planned)* INSERT statement generation
- **Frontend Applications**: REST API endpoints for UI integration
- **External Systems**: Authentication and user management for third-party apps

## Related Documentation

- [Typechecking Service](../typechecking/): Background processing workers
- [Database Service](../../connections/database/): Centralized database operations
- [Protocol Definitions](../../../packages/proto/): Shared interface specifications
