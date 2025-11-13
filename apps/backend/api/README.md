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
- **🔔 Real-time Notifications**: Webhook server for task completion notifications
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
         ▲                      │                                 │
         │              ┌───────┼───────────┐                     ▼
         │              ▼                   ▼            ┌─────────────────┐
         │      ┌─────────────────┐ ┌─────────────────┐  │  Typechecking   │
         │      │  Database Svc   │ │   PostgreSQL    │  │   Workers       │
         │      │  (gRPC Proxy)   │ │ (Direct SQLAlch)│  └─────────────────┘
         │      └─────────────────┘ └─────────────────┘           │
         │              │                    ▲                    │ Results
         │              ▼                    │                    ▼
         │      ┌─────────────────┐          │              ┌─────────────────┐
         │      │ Redis + MongoDB │          │              │ Webhook Server  │
         │      └─────────────────┘          │              │  (Notifications)│
         │                                   │              └─────────────────┘
         │                         ┌─────────┴─────────┐           │
         │                         │ User Management,  │           │ Webhooks
         │                         │ Authentication,   │           │
         │                         │ Application Data  │           │
         │                         └───────────────────┘           │
         └─────────────────────────────────────────────────────────┘
```

### Service Components

- **Main API Server**: REST endpoints for user interaction (Port 8000)
- **Webhook Server**: *(Planned)* Dedicated server for task completion notifications
- **Proxy Integration**: *(Future)* Proxy layer for webhook routing

### Data Flow Separation

- **Cache & Schemas**: API ↔ Database Service (gRPC) ↔ Redis/MongoDB  
- **Users & Auth**: API ↔ PostgreSQL (Direct SQLAlchemy)
- **Task Notifications**: Workers → Webhook Server → Client notifications

## 🏗️ ETL Workflow Orchestration

The API Service orchestrates different ETL workflows that can be executed independently or in combination based on user needs. The exact implementation and flow details are currently being designed.

### Available Workflows

**Data Validation**: File validation against JSON schemas via the Typechecking service

- Requires pre-defined JSON schema
- Uses RabbitMQ for asynchronous processing
- Provides detailed validation reports

**Excel Parsing**: *(Planned Integration)* Excel file processing to SQL generation via Parser services

- Independent of validation workflow
- Processes Excel formulas and data structure
- Generates SQL DDL and INSERT statements

**Combined Processing**: *(Future)* Flexible combination of validation and parsing workflows

- User-configurable workflow selection
- Can execute workflows independently or together
- Results delivered separately or combined based on requirements

### Future Workflow Endpoints *(Design in Progress)*

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/workflows/*` | Workflow execution endpoints (design TBD) |
| `GET` | `/api/v1/workflows/status/{task_id}` | Track workflow progress |
| `GET` | `/api/v1/workflows/results/{task_id}` | Download workflow results |

### Integration Points

- **Typechecking Service**: Data validation and schema compliance
- **Excel Reader Service**: *(Current: REST API, Future: gRPC)* Excel file processing coordination
- **Formula Parser Service**: *(Planned)* Complex formula analysis integration
- **DDL Generator Service**: *(Planned)* Database schema generation
- **SQL Builder Service**: *(Planned)* INSERT statement generation

**Note**: The specific workflow implementation and API design are currently being developed. The Excel Reader service currently operates as a REST API but will be migrated to gRPC for consistency with other parsing services. The exact endpoints and flow will be determined based on user requirements and system architecture decisions.

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

### 🔔 Webhook Endpoints *(Planned)*

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/webhooks/task-completed` | Receive task completion notifications |
| `POST` | `/webhooks/validation-results` | Receive validation task results |
| `POST` | `/webhooks/parsing-results` | Receive parsing task results |

**Note**: Webhook server will run on a separate port and be used exclusively for receiving task completion notifications from background workers. Client notifications will be implemented via WebSockets, Server-Sent Events, or similar real-time mechanisms.

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

# Webhook Server (Planned)
WEBHOOK_SERVER_ENABLED=false
WEBHOOK_SERVER_HOST="localhost"
WEBHOOK_SERVER_PORT=8001
WEBHOOK_SECRET_KEY="webhook_secret_key"
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

### Real-time Notifications *(Planned)*

1. **Task Completion**: Workers publish results to temporary result queues
2. **Webhook Delivery**: Background process sends webhook to dedicated webhook server
3. **Client Notification**: Webhook server notifies clients via real-time mechanisms
4. **Proxy Integration**: *(Future)* Proxy layer for webhook routing and management

**Note**: The current implementation uses polling for status updates. Real-time notifications via webhooks are planned for improved user experience.

### Workflow Processing *(Future)*

**Current**: Data validation workflow fully implemented via Typechecking service

**Planned**: Excel parsing workflows and flexible workflow orchestration

**Design Goals**:

- Independent workflow execution options
- User-configurable processing requirements  
- Flexible result delivery (separate or combined)

**Note**: Specific workflow implementations and integration patterns are currently being designed.

## 🤝 Integration Points

- **Database Service**: gRPC client for Redis/MongoDB operations
- **Typechecking Service**: RabbitMQ message publishing for async processing
- **Excel Reader Service**: *(Current: REST, Future: gRPC)* Excel file processing coordination
- **Formula Parser Service**: *(Planned)* Complex formula analysis integration
- **DDL Generator Service**: *(Planned)* Database schema generation
- **SQL Builder Service**: *(Planned)* INSERT statement generation
- **Webhook Notifications**: *(Planned)* Real-time task completion notifications
- **Frontend Applications**: REST API endpoints for UI integration
- **External Systems**: Authentication and user management for third-party apps

**Migration Notes**:

- Excel Reader currently uses REST API but will be migrated to gRPC for consistency
- Webhook system is planned to replace polling-based status checking
- Proxy integration for webhook routing will be implemented in future iterations

## Related Documentation

- [Typechecking Service](../typechecking/): Background processing workers
- [Database Service](../../connections/database/): Centralized database operations
- [Protocol Definitions](../../../packages/proto/): Shared interface specifications

<!-- A comment just to test github actions -->
