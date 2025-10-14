# ETL Design Backend

A comprehensive microservices architecture for ETL (Extract, Transform, Load) operations that handles the complete lifecycle from Excel file upload to SQL generation. The backend consists of three main service groups: API services, data validation services, and parsing services, with independent workflows that can be executed separately or combined.

## 🏗️ Architecture Overview

The backend is designed as a distributed system with clear separation of concerns, using various communication patterns including REST APIs, gRPC services, and message queuing:

```text
┌─────────────────┐     ┌─────────────────┐               ┌─────────────────┐
│   Client Apps   │───▶ │   API Service   │─────────────▶ │   RabbitMQ      │
│   (Frontend)    │     │   (FastAPI)     │               │  (Message Bus)  │
└─────────────────┘     └─────────────────┘               └─────────────────┘
         ▲                       │                                │
         │               ┌───────┼───────────┐                    ▼
         │               ▼                   ▼            ┌─────────────────┐
         │       ┌─────────────────┐ ┌─────────────────┐  │  Typechecking   │
         │       │  Database Svc   │ │   PostgreSQL    │  │   Workers       │
         │       │  (gRPC Proxy)   │ │ (Direct SQLAlch)│  └─────────────────┘
         │       └─────────────────┘ └─────────────────┘           │
         │               │                    ▲                    │
         │               ▼                    │                    │
         │       ┌─────────────────┐          │                    │
         │       │ Redis + MongoDB │          │                    │
         │       └─────────────────┘          │                    │
         │                                    │                    │
         │                          ┌─────────┴─────────┐          │
         │                          │ User Management,  │          │
         │                          │ Authentication,   │          │
         │                          │ Application Data  │          │
         │                          └───────────────────┘          │
         │                                                         ▼
         │                                              ┌─────────────────┐
         └──────────────────────────────────────────────│ Webhook Server  │
                                                        │ (Notifications) │
                                                        └─────────────────┘
```

## 🚀 Service Groups

### 1. [API Service](./api/) - REST Interface & Orchestration

**Technology**: Python + FastAPI  
**Ports**: 8000 (main), 8001 (webhooks - planned)  
**Purpose**: Primary interface for client applications and workflow orchestration

**Key Features**:

- 🔐 JWT-based authentication and user management
- 📋 JSON schema management with versioning
- 📄 File validation request handling
- 🏗️ Independent workflow orchestration (validation, parsing, or combined)
- 🔄 RabbitMQ message publishing for background processing
- 💾 Redis caching and PostgreSQL direct access
- 🔔 Real-time notifications via webhook server (planned)
- 🏥 Health monitoring and metrics endpoints

**Main Endpoints**:

- Authentication: `/api/v1/login/*`
- Users: `/api/v1/users/*`
- Schemas: `/api/v1/schemas/*`
- Validation: `/api/v1/validation/*`
- Cache: `/api/v1/cache/*`
- Health: `/health`, `/metrics`
- Webhooks: `/webhooks/*` (planned)

### 2. [Typechecking Service](./typechecking/) - Data Validation Workers

**Technology**: Python + Polars + RabbitMQ  
**Port**: 8001 (optional health endpoint)  
**Purpose**: High-performance background data validation and schema processing

**Key Features**:

- ⚡ Polars-based high-performance data processing
- 🔄 RabbitMQ consumer workers (validation & schema)
- 📊 Parallel processing with configurable concurrency
- 📄 Multi-format file support (CSV, XLSX, XLS)
- 🔍 Detailed validation reports with row-level errors
- 🔔 Result notifications via temporary queues (planned: webhooks)
- 🏥 Optional health monitoring endpoint
- 🔧 Thread-safe multi-worker operations

**Worker Types**:

- **Validation Worker**: Processes file validation against JSON schemas
- **Schema Worker**: Handles schema creation, updates, and removal
- **Worker Manager**: Coordinates lifecycle and graceful shutdown

### 3. [Parsing Services](./parsers/) - Excel to SQL Conversion

**Technology**: Multi-language microservices (Python + Node.js)  
**Ports**: 8001, 50052-50054  
**Purpose**: Distributed Excel parsing and SQL generation pipeline

**Microservices**:

#### [Excel Reader](./parsers/excel-reader/) (Port 8001)

- **Tech**: Python + FastAPI → **Migrating to gRPC**
- **Role**: Main entry point and orchestrator
- Accepts Excel file uploads
- Extracts data and formulas
- Coordinates with other parsing services
- **Note**: Currently REST API, planned migration to gRPC for consistency

#### [Formula Parser](./parsers/formula-parser/) (Port 50052)

- **Tech**: Node.js + gRPC
- **Role**: Formula analysis and AST generation
- Tokenizes Excel formulas
- Builds Abstract Syntax Trees
- Handles complex formula dependencies

#### [DDL Generator](./parsers/ddl-generator/) (Port 50053)

- **Tech**: Python + gRPC
- **Role**: Database schema generation
- Converts AST to SQL expressions
- Maps Excel references to SQL columns
- Handles data type inference

#### [SQL Builder](./parsers/sql-builder/) (Port 50054)

- **Tech**: Python + gRPC
- **Role**: Final SQL statement construction
- Combines expressions into complete SQL
- Manages dependencies and execution order
- Generates CREATE TABLE and INSERT statements

## 🔄 Workflow Architecture

The backend supports multiple independent workflows that can be executed separately based on user needs:

### Current Implementation

**Data Validation Pipeline**: Complete workflow for validating spreadsheet data against JSON schemas

```text
1. Client uploads file with schema → API Service
2. API validates schema existence → Database Service
3. API publishes validation message → RabbitMQ
4. Typechecking workers validate data → Results
5. Workers publish to result queues → (Future: Webhook notifications)
6. Status updated in database → Client polling/notifications
```

### Planned Workflows

**Excel Parsing Pipeline**: Independent workflow for converting Excel files to SQL

```text
1. Client uploads Excel file → Excel Reader (REST → gRPC)
2. Formula extraction → Formula Parser (gRPC)
3. Schema generation → DDL Generator (gRPC)
4. SQL building → SQL Builder (gRPC)
5. Complete SQL package → Client
```

**Combined Workflows**: Flexible integration of validation and parsing based on user requirements

- **Independent execution**: Each workflow runs separately
- **Parallel processing**: Both workflows can run simultaneously
- **User choice**: Client selects which workflows to execute

**Note**: The specific integration patterns between validation and parsing workflows are still being planned. The exact implementation will be determined based on user requirements and use case analysis.

### Notification Architecture (Planned)

**Real-time Notifications**: Replace polling with webhook-based notifications

```text
1. Task completion → Workers publish to result queues
2. Background service → Webhook delivery to API webhook server
3. Webhook server → Real-time client notifications
4. Future: Proxy layer for webhook routing and management
```

## 🛠️ Technology Stack

### Core Technologies

- **Python 3.12.10**: Primary language for API, validation, and parsing services
- **Node.js 18+**: Formula parsing service
- **FastAPI**: REST API framework
- **gRPC**: Inter-service communication
- **Protocol Buffers**: Service interface definitions
- **RabbitMQ**: Message queuing and async processing
- **PostgreSQL**: User and application data
- **Redis**: Caching and session storage
- **MongoDB**: Schema and metadata storage

### Performance & Scaling

- **Polars**: High-performance data processing
- **uvloop**: High-performance async event loop
- **Connection pooling**: Database and message broker connections
- **Horizontal scaling**: Multiple worker instances
- **Load balancing**: Natural queue-based distribution

### Development Tools

- **UV**: Fast Python package management
- **Alembic**: Database migration management
- **Pydantic**: Data validation and serialization
- **Ruff**: Code formatting and linting
- **Pytest**: Testing framework
- **Docker**: Containerization support

## ⚙️ Configuration

Each service has its own `.env.example` file. Key configuration areas:

### API Service Configuration

```bash
# Server
SERVER_HOST=localhost
SERVER_PORT=8000
API_V1_STR=/api/v1

# Database connections
POSTGRES_HOST=localhost             # Direct SQL connection
DATABASE_CONNECTION_HOST=localhost  # gRPC Database Service

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_EXCHANGE=typechecking.exchange

# Security
SECRET_KEY=your_secret_key_here

# Webhook Server (Planned)
WEBHOOK_SERVER_ENABLED=false
WEBHOOK_SERVER_PORT=8001
```

### Typechecking Configuration

```bash
# Performance
MAX_WORKERS=4
WORKER_CONCURRENCY=4
WORKER_PREFETCH_COUNT=1

# Health monitoring (optional)
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_PORT=8001

# Result queues (temporary, future: webhooks)
RABBITMQ_QUEUE_RESULTS_SCHEMAS=typechecking.schemas.results.queue
RABBITMQ_QUEUE_RESULTS_VALIDATIONS=typechecking.validation.results.queue
```

### Parsing Services Configuration

```bash
# Excel Reader (Current: REST, Future: gRPC)
EXCEL_READER_PORT=8001

# Service endpoints
FORMULA_PARSER_PORT=50052
DDL_GENERATOR_PORT=50053
SQL_BUILDER_PORT=50054
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12.10
- Node.js 18+
- PostgreSQL 17+
- RabbitMQ 4.0+
- Redis 7+
- MongoDB 8+

### Development Setup

1. **Clone and navigate to backend**:

   ```bash
   git clone https://github.com/ISCOUTB/etl-design.git
   cd etl-design/apps/backend
   ```

2. **Set up API Service**:

   ```bash
   cd api
   cp .env.example .env
   uv sync
   bash scripts/prestart.sh
   uv run python -m src.main
   ```

3. **Set up Typechecking Service**:

   ```bash
   cd ../typechecking
   cp .env.example .env
   uv sync
   uv run python -m src.main
   ```

4. **Set up Parsing Services**:

   ```bash
   # Formula Parser (Node.js)
   cd ../parsers/formula-parser
   npm install
   npm run dev

   # DDL Generator
   cd ../ddl-generator
   uv sync
   uv run python src/server.py

   # SQL Builder
   cd ../sql-builder
   uv sync
   uv run python src/server.py

   # Excel Reader (Current: REST)
   cd ../excel-reader
   uv sync
   uv run python src/server_rest.py
   ```

### Production Deployment

Use Docker or systemd services for production deployment. Each service includes Dockerfile for containerization.

## 📊 Monitoring & Health Checks

### Health Endpoints

- **API Service**: `GET /health`, `GET /health/detailed`, `GET /metrics`
- **Typechecking**: `GET /health` (optional, configurable)
- **Parsing Services**: Individual health checks per service

### Logging

Each service generates structured logs:

- **API**: `logs/api_*.log`
- **Typechecking**: `logs/typechecking_*.log`
- **Parsers**: Individual log files per service

### Metrics

- Request/response metrics via FastAPI
- Worker performance metrics
- Queue depth and processing rates
- Database connection health
- Cache hit rates

## 🔌 Integration Points

### Internal Communication

- **REST APIs**: Client ↔ API Service, Excel Reader orchestration (current)
- **gRPC**: Parsing service communication, Database Service operations
- **RabbitMQ**: Async task processing, worker communication
- **Direct SQL**: User management, application data
- **Webhooks**: *(Planned)* Real-time task completion notifications

### External Integration

- **Frontend Applications**: REST API consumption
- **Database Systems**: PostgreSQL, Redis, MongoDB
- **Message Brokers**: RabbitMQ clustering
- **Monitoring Systems**: Metrics export, log aggregation
- **Notification Systems**: *(Planned)* Webhook-based real-time updates

## 🧪 Testing

### Running Tests

```bash
# API Service tests
cd api && uv run pytest

# Typechecking tests
cd typechecking && uv run pytest

# Parser tests (individual services)
cd parsers/formula-parser && npm test
cd parsers/ddl-generator && uv run pytest
```

### Integration Testing

Integration tests validate the complete workflows:

- File upload through API
- Validation processing
- Parsing coordination
- SQL generation
- Notification delivery (when implemented)

## 📚 Documentation

### Service Documentation

- [API Service](./api/README.md) - REST API and workflow orchestration
- [Typechecking Service](./typechecking/README.md) - Background validation workers
- [Parsing Services](./parsers/README.md) - Excel to SQL conversion pipeline

### Protocol Documentation

- [Protocol Buffers](../../packages/proto/) - Service interface definitions
- [Messaging Utils](../../packages/messaging-utils/) - RabbitMQ utilities
- [Proto Utils](../../packages/proto-utils/) - gRPC client libraries

## 🎯 Development Roadmap

### Current State

- ✅ Complete validation pipeline (API → Typechecking)
- ✅ Individual parsing services functional
- ✅ User management and authentication
- ✅ Schema management system
- ✅ Result queues for task completion

### In Progress

- 🔄 Webhook notification system
- 🔄 Excel Reader migration from REST to gRPC
- 🔄 Integration testing suite
- 🔄 Health monitoring implementation

### Planned

- 📋 Complete workflow orchestration via API Service
- 📋 Real-time notifications replacing polling
- 📋 Proxy layer for webhook routing
- 📋 Advanced caching strategies
- 📋 Horizontal scaling optimization
- 📋 Performance monitoring dashboard

## 🔄 Migration Notes

### Ongoing Migrations

1. **Excel Reader REST → gRPC**: Planned migration for consistency with other parsing services
2. **Polling → Webhooks**: Result queues are temporary, will be replaced with webhook notifications
3. **Proxy Integration**: Future proxy layer for webhook routing and management

### Architecture Evolution

- **Current**: Mixed REST/gRPC with polling-based status checking
- **Target**: Consistent gRPC services with webhook-based real-time notifications
- **Benefits**: Improved performance, consistency, and user experience

## 🤝 Contributing

1. **Code Style**: Follow established conventions (Python: PEP 8, Node.js: Standard)
2. **Testing**: Write tests for new functionality
3. **Documentation**: Update relevant README files
4. **Protocol Buffers**: Regenerate clients when updating .proto files
5. **Environment**: Test with all dependent services running
6. **Migration Awareness**: Consider ongoing migrations when making changes

## Related Documentation

- [Database Service](../connections/database/) - Centralized database operations
- [Messaging Service](../connections/messaging/) - RabbitMQ connection management
- [Frontend Applications](../web/) - Client interfaces
- [Deployment](../../infrastructure/k8s/) - Kubernetes configurations
