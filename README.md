# ETL Design - Excel to Database Transformation System (MVP)

A comprehensive, enterprise-grade ETL (Extract, Transform, Load) system designed to transform Excel spreadsheets into structured databases with formula parsing, data validation, and automated SQL generation capabilities.

> **⚠️ MVP Notice**: This is a Minimum Viable Product developed for academic research. The system is functional but requires significant refactoring and optimization before production use. See [MVP Status &amp; Future Development](#️-mvp-status--future-development) for details.

## 🚀 Overview

ETL Design is a sophisticated data transformation platform that bridges the gap between Excel-based data workflows and modern database systems. The project consists of two main subsystems that work together to provide a complete Excel-to-Database pipeline:

1. **Excel Parsing System**: A microservices architecture for parsing Excel formulas and generating SQL statements
2. **Typechecking System**: A high-performance data validation and schema management platform

## ⚠️ MVP Status & Future Development

**This project is currently a Minimum Viable Product (MVP)** developed as part of an degree project. While functional and demonstrating core capabilities, several aspects are planned for future development:

### Current MVP Limitations

- **Code Quality**: Some components require refactoring and optimization
- **Error Handling**: Enhanced error management and recovery mechanisms needed
- **Testing Coverage**: Additional unit and integration tests required
- **Documentation**: Some technical details and API specifications need expansion
- **Performance**: Optimization opportunities exist across all services
- **Security**: Production-ready security measures need implementation

### Planned Refactoring & Evolution

- **Architecture Review**: Complete system architecture analysis and potential redesign
- **Language Considerations**: Programming languages may change based on performance requirements and maintainability:
  - **Microservices**: Python services might be converted to Go or Rust for better performance
  - **Data Processing**: Consider specialized languages like Scala for big data scenarios
- **Database Strategy**: Potential migration to more specialized databases (e.g., TimescaleDB, ClickHouse)
- **Cloud Native**: Kubernetes deployment and cloud-native architecture patterns
- **Infrastructure as Code**: Terraform implementation for reproducible cloud deployments
- **CI/CD Pipeline**: Automated testing, building, and deployment workflows
- **API Evolution**: GraphQL integration and improved REST API design
- **Real-time Processing**: Stream processing capabilities with Apache Kafka or similar

### Roadmap Highlights

- 🔄 **Phase 1**: Code refactoring and test coverage improvement
- 🏗️ **Phase 2**: Architecture redesign and technology stack evaluation
- ☁️ **Phase 3**: Cloud-native implementation with Kubernetes orchestration and Terraform IaC
- 🚀 **Phase 4**: CI/CD pipeline implementation and automated deployment workflows
- ⚡ **Phase 5**: Performance optimization and scalability enhancements
- 🎯 **Phase 6**: Production deployment and enterprise features

**Note**: The current implementation serves as a proof of concept and research foundation. Future versions will focus on production readiness, scalability, and enterprise-grade features.

## ✨ Key Features

### Excel Parsing Capabilities

- **🔍 Formula Analysis**: Advanced Excel formula parsing with AST generation
- **🔄 SQL Translation**: Automatic conversion of Excel formulas to SQL expressions
- **📊 Multi-format Support**: Handles .xlsx, .xls, and .csv files
- **🏗️ DDL Generation**: Creates complete CREATE TABLE and INSERT statements
- **⚡ Microservices Architecture**: Distributed processing with gRPC communication

### Data Validation & Management

- **📋 Schema Validation**: Dynamic JSON schema validation with versioning
- **⚡ High Performance**: Parallel processing with Polars for large datasets
- **🔐 User Management**: Complete authentication with JWT and RBAC
- **🌐 RESTful API**: FastAPI-based endpoints with automatic documentation
- **💾 Intelligent Caching**: Redis-based caching with TTL management
- **🔀 Async Processing**: RabbitMQ message queuing for scalable operations

## 🏗️ Architecture

The system follows a modern microservices architecture with clear separation of concerns:

```text
┌─────────────────────────────────────────────────────────────┐
│                     ETL Design Platform                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │   Excel Parsing     │    │     Typechecking System     │ │
│  │     System          │    │                             │ │
│  │                     │    │                             │ │
│  │ ┌─────────────────┐ │    │ ┌─────────────────────────┐ │ │
│  │ │  Excel Reader   │ │    │ │      FastAPI Server     │ │ │
│  │ │   (REST API)    │ │    │ │     (REST API + UI)     │ │ │
│  │ └─────────────────┘ │    │ └─────────────────────────┘ │ │
│  │          │          │    │            │                │ │
│  │          ▼          │    │            ▼                │ │
│  │ ┌─────────────────┐ │    │ ┌─────────────────────────┐ │ │
│  │ │ Formula Parser  │ │    │ │     RabbitMQ Queue      │ │ │
│  │ │  (Node.js gRPC) │ │    │ │   (Async Processing)    │ │ │
│  │ └─────────────────┘ │    │ └─────────────────────────┘ │ │
│  │          │          │    │            │                │ │
│  │          ▼          │    │            ▼                │ │
│  │ ┌─────────────────┐ │    │ ┌─────────────────────────┐ │ │
│  │ │ DDL Generator   │ │    │ │    Validation Workers   │ │ │
│  │ │ (Python gRPC)   │ │    │ │   (Schema Processing)   │ │ │
│  │ └─────────────────┘ │    │ └─────────────────────────┘ │ │
│  │          │          │    │                             │ │
│  │          ▼          │    │ ┌─────────────────────────┐ │ │
│  │ ┌─────────────────┐ │    │ │      Data Stores        │ │ │
│  │ │  SQL Builder    │ │    │ │ PostgreSQL │ MongoDB    │ │ │
│  │ │ (Python gRPC)   │ │    │ │   Redis    │            │ │ │
│  │ └─────────────────┘ │    │ └─────────────────────────┘ │ │
│  └─────────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```text
ETL-Design/
├── docs/                           # Project documentation
├── apps/                           # Application services
│   ├── backend/                    # Core backend services
│   ├── connections/                # Database infrastructure
│   ├── scripts/                    # Deployment scripts
│   └── web/                        # Frontend applications (planned)
├── packages/                       # Shared packages and utilities
├── infrastructure/                 # DevOps and infrastructure (planned)
│   ├── terraform/                  # Infrastructure as Code
│   ├── k8s/                        # Kubernetes manifests
│   ├── monitoring/                 # Observability configurations
│   └── scripts/                    # Infrastructure automation
├── tools/                          # Development tools and benchmarks
└── README.md                       # This file
```

## ☁️ DevOps & Cloud Infrastructure

The ETL Design platform is being designed with modern DevOps practices and cloud-native architectures in mind:

### 🚀 Infrastructure as Code (IaC)

- **Terraform Modules**: Planned implementation for reproducible cloud infrastructure
  - **Cloud Providers**: Multi-cloud support (AWS, Azure, GCP) with provider-specific optimizations
  - **Resource Management**: Automated provisioning of databases, message queues, and compute resources
  - **Environment Isolation**: Separate infrastructure configurations for development, staging, and production
  - **Cost Optimization**: Intelligent resource scaling and cost monitoring integration

### ⚙️ Container Orchestration

- **Kubernetes Deployment**: Cloud-native orchestration with the following components:
  - **Microservices Pods**: Each service containerized with health checks and resource limits
  - **Service Mesh**: Istio integration for advanced traffic management and security
  - **Auto-scaling**: Horizontal Pod Autoscaler (HPA) and Vertical Pod Autoscaler (VPA)
  - **Storage**: Persistent volumes for databases with automated backup strategies
  - **Monitoring**: Prometheus + Grafana stack for comprehensive observability

### 🔄 CI/CD Pipeline

- **Automated Workflows**: GitHub Actions / GitLab CI integration
  - **Multi-stage Testing**: Unit tests, integration tests, and end-to-end validation
  - **Code Quality**: SonarQube integration for code coverage and security scanning
  - **Container Security**: Vulnerability scanning with Trivy and admission controllers
  - **Progressive Deployment**: Blue-green and canary deployment strategies
  - **Rollback Capabilities**: Automated rollback triggers based on health metrics

### 📊 Observability & Monitoring

- **Logging**: Centralized logging with ELK stack (Elasticsearch, Logstash, Kibana)
- **Metrics**: Custom application metrics with Prometheus and alerting rules
- **Tracing**: Distributed tracing with Jaeger for microservices communication analysis
- **Health Monitoring**: Advanced health checks with dependency validation

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose**: Latest versions for infrastructure services
- **Python**: 3.12+ with `uv` package manager
- **Node.js**: 18+ with npm
- **Git**: For cloning the repository

### 1. Clone and Setup

```bash
git clone https://github.com/ISCOUTB/etl-design.git
cd etl-design
```

### 2. Start Infrastructure Services

Deploy the required databases and message brokers:

```bash
# Deploy all infrastructure services using provided scripts
cd apps/scripts/

# Start databases
bash ./deploy_postgres_docker.sh  # PostgreSQL for user data
bash ./deploy_mongo_docker.sh     # MongoDB for schemas
bash ./deploy_redis_docker.sh     # Redis for caching

# Start message broker
bash ./deploy_rabbitmq_docker.sh  # RabbitMQ for async processing
```

### 3. Start Core Backend Services

#### Database Service (gRPC)

Centralized database connection service for MongoDB and Redis:

```bash
cd apps/connections/database/
cp .env.example .env
# Edit .env with your database configuration
uv sync
uv run python -m src.server
```

#### API Service (REST + FastAPI)

Main REST API with authentication and user management:

```bash
cd apps/backend/api/
cp .env.example .env
# Edit .env with your configuration
uv sync
uv run python -m src.main
```

#### Typechecking Service (Workers)

Background workers for data validation:

```bash
cd apps/backend/typechecking/
cp .env.example .env
# Edit .env with your configuration
uv sync
uv run python -m src.main
```

### 4. Start Excel Parsing Services

Start each parsing microservice (in separate terminals):

```bash
cd apps/backend/parsers/

# Excel Reader (REST API)
cd excel-reader
cp .env.example .env
uv sync
uv run python src/server_rest.py

# Formula Parser (Node.js gRPC)
cd ../formula-parser
cp .env.example .env
npm install
moon run formula-parser:run

# DDL Generator (Python gRPC)
cd ../ddl-generator
cp .env.example .env
uv sync
uv run python src/server.py

# SQL Builder (Python gRPC)
cd ../sql-builder
cp .env.example .env
uv sync
uv run python src/server.py
```

### 5. Verify Installation

Once all services are running, verify the installation:

- **API Documentation**: <http://localhost:8000/docs>
- **Excel Reader**: <http://localhost:8001>
- **Health Checks**: All services should respond to their respective health endpoints

### Service Architecture Overview

The system consists of several independent services that work together:

1. **Infrastructure Layer**: PostgreSQL, MongoDB, Redis, RabbitMQ
2. **Database Service**: gRPC proxy for MongoDB/Redis operations (Port: 50050)
3. **API Service**: FastAPI REST server with authentication (Port: 8000)
4. **Typechecking Workers**: RabbitMQ consumers for validation
5. **Excel Parsing Services**: Microservices for Excel processing (Ports: 8001, 50052-50054)

## 🔧 Configuration

### Environment Setup

Each service requires configuration through environment variables. For each service, copy the provided `.env.example` file to `.env` and customize the values according to your environment:

```bash
# For database service
cp apps/connections/database/.env.example apps/connections/database/.env

# For backend services
cp apps/backend/api/.env.example apps/backend/api/.env
cp apps/backend/typechecking/.env.example apps/backend/typechecking/.env

# For parsing services  
cp apps/backend/parsers/formula-parser/.env.example apps/backend/parsers/formula-parser/.env
cp apps/backend/parsers/ddl-generator/.env.example apps/backend/parsers/ddl-generator/.env
cp apps/backend/parsers/sql-builder/.env.example apps/backend/parsers/sql-builder/.env
cp apps/backend/parsers/excel-reader/.env.example apps/backend/parsers/excel-reader/.env
```

**Important**: Edit each `.env` file to match your local development environment, including database connections, ports, and security settings. See the individual service README files for detailed configuration options.

## 📚 Usage Examples

### Excel Formula Processing

```bash
# Process an Excel file with formulas
curl -X POST "http://localhost:8001/excel-parser" \
  -H "Content-Type: multipart/form-data" \
  -F "spreadsheet=@sample.xlsx" \
  -F "table_name=users" \
  -F 'dtypes_str={"Sheet1": {"id": {"type": "INTEGER", "extra": "PRIMARY KEY"}, "name": {"type": "TEXT"}, "age": {"type": "INTEGER"}}}'
```

**Response**:

```json
{
  "Sheet1": "CREATE TABLE users_Sheet1 (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)"
}
```

### Data Validation

```bash
# Validate a dataset against a schema
curl -X POST "http://localhost:8000/api/v1/validation/upload/user_schema_v1" \
  -H "Content-Type: multipart/form-data" \
  -F "spreadsheet_file=@data.csv"
```

## 📊 Performance

The system is designed for high performance and scalability:

- **Excel Processing**: Handles files up to 100MB with complex formulas
- **Data Validation**: Processes 1M+ rows with sub-second validation
- **Concurrent Processing**: Supports multiple parallel validation jobs
- **Caching**: Redis-based caching reduces processing time by 60-80%
- **Async Operations**: Non-blocking operations for improved throughput

## 🤝 Contributing

**Important**: As this is an MVP, contributions should focus on research, experimentation, and proof-of-concept improvements rather than production-ready features.

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow coding standards**:
   - Python: PEP 8 with type hints
   - JavaScript: Standard Style
   - Commit messages: Conventional Commits
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request**

### Development Guidelines

- **Experimental Features**: Feel free to experiment with new technologies and approaches
- **Code Quality**: While this is an MVP, maintain readable and well-documented code
- **Testing**: Add tests for critical functionality, even if coverage isn't complete
- **Documentation**: Document your experiments and findings for future reference
- **Architecture**: Consider future refactoring plans when making changes

### Areas for Contribution

- **Performance Analysis**: Benchmarking and optimization opportunities
- **Technology Evaluation**: Research alternative languages and frameworks
- **Feature Prototyping**: New functionality proof-of-concepts
- **Error Handling**: Improved error management and recovery
- **Testing**: Additional test coverage and testing strategies
- **Documentation**: API documentation and usage examples
- **DevOps & Infrastructure**: Kubernetes manifests, Terraform modules, and CI/CD pipeline improvements
- **Cloud Architecture**: Multi-cloud deployment strategies and cost optimization
- **Security**: Container security scanning, vulnerability assessment, and compliance frameworks

## 📖 Documentation

- **[Applications Overview](./apps/README.md)**: Complete service directory and navigation guide
- **[Backend Services](./apps/backend/README.md)**: Backend architecture and service guide  
- **[Excel Parsing System](./apps/backend/parsers/README.md)**: Complete microservices documentation
- **[API Service](./apps/backend/api/README.md)**: REST API and authentication service
- **[Typechecking System](./apps/backend/typechecking/README.md)**: Data validation platform guide
- **[API Documentation](http://localhost:8000/docs)**: Interactive OpenAPI docs (when running)
- **[Kubernetes Manifests](./infrastructure/k8s/README.md)**: Container orchestration configurations (planned)
- **Research Papers**: Available in the `docs/` directory

## 🐛 Troubleshooting

### Common Issues

1. **Port Conflicts**: Ensure ports 8000, 8001, 50050, 50052-50054 are available
2. **Docker Issues**: Run `docker-compose down && docker-compose up --build`
3. **Database Connection**: Verify database services are running and accessible
4. **Memory Issues**: Increase Docker memory allocation for large files
5. **Kubernetes Deployment**: Check pod status and logs using `kubectl get pods` and `kubectl logs`
6. **Infrastructure Provisioning**: Verify Terraform state and cloud resource availability

## 🏆 Academic Context

This project is part of an engineering degree project at **Universidad Tecnológica de Bolívar** focusing on:

- **Data Transformation Pipelines**: Modern ETL architecture patterns
- **Microservices Design**: Distributed system implementation
- **Excel Formula Analysis**: Academic research on spreadsheet processing
- **Performance Optimization**: High-throughput data processing techniques

## 📄 License

This project is developed as part of an academic degree project at Universidad Tecnológica de Bolívar. All rights reserved.

## 👥 Authors

**Engineering Degree Project**
Diederik Montaño  
Mauro Gonzalez  
Juan Perez  
Universidad Tecnológica de Bolívar  
Faculty of Engineering
