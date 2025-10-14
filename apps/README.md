# Applications Directory

This directory contains all the application services that make up the ETL Design platform. The system is organized into several main categories of services, each with specific responsibilities in the data transformation pipeline.

## 🏗️ Architecture Overview

The ETL Design platform consists of independent but interconnected microservices:

```text
apps/
├── backend/                    # Core backend services
│   ├── api/                   # FastAPI REST API service
│   ├── typechecking/          # Data validation workers
│   └── parsers/               # Excel parsing microservices
│       ├── excel-reader/      # Excel file processing service
│       ├── formula-parser/    # Excel formula parsing (Node.js)
│       ├── ddl-generator/     # AST to SQL conversion
│       └── sql-builder/       # Final SQL assembly
├── connections/               # Database infrastructure
├── scripts/                   # Deployment and utility scripts
└── web/                       # Frontend applications (planned)
```

## 📋 Service Directory

### 🔧 Backend Services

#### Core API Service

- **Location**: [`backend/api/`](./backend/api/README.md)
- **Technology**: FastAPI + SQLAlchemy + PostgreSQL
- **Purpose**: REST API endpoints, user authentication, workflow orchestration
- **Key Features**: JWT authentication, user management, schema validation endpoints, webhook server (planned)
- **Dependencies**: PostgreSQL, RabbitMQ, Database Service (gRPC)

#### Data Validation Service

- **Location**: [`backend/typechecking/`](./backend/typechecking/README.md)
- **Technology**: Python + Polars + RabbitMQ
- **Purpose**: Background data validation and processing workers
- **Key Features**: High-performance validation, parallel processing, health monitoring
- **Dependencies**: RabbitMQ, Database Service (gRPC), Redis/MongoDB

#### Excel Parsing Services

- **Location**: [`backend/parsers/`](./backend/parsers/README.md)
- **Technology**: Multi-language microservices (Python + Node.js)
- **Purpose**: Complete Excel-to-SQL transformation pipeline
- **Services**:
  - **Excel Reader**: File processing and coordination
  - **Formula Parser**: Excel formula AST generation (Node.js)
  - **DDL Generator**: Database schema creation (Python)
  - **SQL Builder**: Final SQL statement assembly (Python)

### 🗄️ Infrastructure Services

#### Database Services

- **Location**: [`connections/`](./connections/README.md)
- **Purpose**: Centralized database proxy and connection management
- **Key Features**: gRPC database service for MongoDB and Redis operations
- **Technologies**: MongoDB, Redis

#### Deployment Scripts

- **Location**: [`scripts/`](./scripts/)
- **Purpose**: Container deployment and environment setup
- **Available Scripts**:
  - `deploy_postgres_docker.sh` - PostgreSQL container setup
  - `deploy_mongo_docker.sh` - MongoDB container setup
  - `deploy_redis_docker.sh` - Redis container setup
  - `deploy_rabbitmq_docker.sh` - RabbitMQ container setup

### 🌐 Frontend (Planned)

- **Location**: [`web/`](./web/)
- **Status**: Planned for future development
- **Purpose**: Web interface for the ETL platform

## 🚀 Quick Navigation

### Getting Started

1. **First Time Setup**: Start with the [main README](../README.md) for system overview
2. **Backend Services**: See [backend README](./backend/README.md) for comprehensive architecture guide
3. **Infrastructure**: Review [connections README](./connections/README.md) for database setup

### Development Workflow

1. **API Development**: Work with [`backend/api/`](./backend/api/README.md)
2. **Data Processing**: Develop workers in [`backend/typechecking/`](./backend/typechecking/README.md)
3. **Excel Features**: Extend parsing in [`backend/parsers/`](./backend/parsers/README.md)

### Operations & Deployment

1. **Database Setup**: Deployment scripts are available in [`scripts/`](./scripts/)
2. **Service Configuration**: Each service has its own `.env.example`
3. **Health Monitoring**: Health endpoints are planned for all services

## 🔄 Data Flow

The services work together in two main workflows:

### Validation Workflow

```text
User → API Service → RabbitMQ → Typechecking Workers → Database Service → Storage
```

### Parsing Workflow

```text
User → Excel Reader → Formula Parser → DDL Generator → SQL Builder → Results
```

> **Note**: These workflows are independent and can operate concurrently. Integration patterns between validation and parsing are still being planned.

## 🏃 Running Services

### Development Mode

```bash
# Start infrastructure first (from workspace root)
cd apps/scripts/
bash ./deploy_postgres_docker.sh
bash ./deploy_mongo_docker.sh
bash ./deploy_redis_docker.sh
bash ./deploy_rabbitmq_docker.sh

# Start backend services
cd ../backend/api/
uv run python -m src.main

cd ../typechecking/
uv run python -m src.main

# Start parsing services
cd ../parsers/excel-reader/
uv run python src/server_rest.py

# See individual service READMEs for detailed instructions
```

## 📊 Service Status

| Service | Status | Technology | Port | Health Endpoint |
|---------|--------|------------|------|----------------|
| API Service | ✅ Active | FastAPI | 8000 | Planned |
| Typechecking | ✅ Active | Python + Polars | - | Planned |
| Database Service | ✅ Active | gRPC | 50050 | gRPC health |
| Excel Reader | 🔄 Migrating | Python → gRPC | 8001 | Planned |
| Formula Parser | ✅ Active | Node.js | 50052 | gRPC health |
| DDL Generator | ✅ Active | Python | 50053 | gRPC health |
| SQL Builder | ✅ Active | Python | 50054 | gRPC health |

## 🔮 Future Development

### Planned Features

- **Web Interface**: React-based frontend for easier interaction
- **Excel Reader Migration**: REST API → gRPC service conversion
- **Webhook Notifications**: Real-time status updates and notifications
- **Advanced Monitoring**: Comprehensive logging and metrics collection

### Architecture Evolution

- **Service Mesh**: Potential Istio integration for better service communication
- **Event Sourcing**: Consider event-driven architecture patterns
- **API Gateway**: Centralized routing and rate limiting
- **Auto-scaling**: Kubernetes-based horizontal scaling

## 📚 Documentation Links

- **[System Overview](../README.md)** - Complete platform documentation
- **[Backend Architecture](./backend/README.md)** - Detailed backend service guide
- **[Database Infrastructure](./connections/README.md)** - Database services and connections
- **[API Documentation](http://localhost:8000/docs)** - Interactive OpenAPI docs (when running)

## 🔧 Troubleshooting

### Common Issues

1. **Service Dependencies**: Ensure infrastructure services (PostgreSQL, RabbitMQ, etc.) are running first
2. **Port Conflicts**: Check that required ports (8000, 8001, 50050, 50052-50054) are available
3. **Environment Variables**: Each service requires proper `.env` configuration
4. **gRPC Connections**: Verify network connectivity between parsing services

---

> **💡 Tip**: Start by reading the [backend README](./backend/README.md) for a comprehensive understanding of how all these services work together!
