# S.L.O.T.H - Excel to Database Transformation System (MVP)

A comprehensive, enterprise-grade ETL (Extract, Transform, Load) system designed to transform Excel spreadsheets into structured databases with formula parsing, data validation, and automated SQL generation capabilities.

> **⚠️ MVP Notice**: This is a Minimum Viable Product developed for academic research. The system is functional but requires significant refactoring and optimization before production use. See [MVP Status &amp; Future Development](#️-mvp-status--future-development) for details.

## 🚀 Overview

S.L.O.T.H is a microservices platform for migrating business logic from spreadsheets into traditional database-backed workflows, with PostgreSQL as the primary target. The repository is organized around a small set of production-shaped services that work together to ingest spreadsheets, validate data, parse formulas, generate SQL, and persist workflow state.

The system is split into these main runtime areas:

1. **Core API**: Orchestrates authentication, users, schemas, uploads, tasks, and events.
2. **Web App**: Nuxt frontend for interacting with the backend.
3. **Database Service**: gRPC proxy for MongoDB and Redis.
4. **Parsing Subsystem**: Excel Reader plus modular formula, DDL, and SQL generation services.
5. **Typechecking Service**: RabbitMQ consumers for validation and insertion workflows.

## 📚 Publications

The S.L.O.T.H. architecture and its research contributions have been presented in the following IEEE conference publications:

1. **Optimized ETL-Based Architecture for Migrating Business Logic Contained in Spreadsheets** — IEEE Colombian Caribbean Conference (C3), 2025. [https://doi.org/10.1109/C366505.2025.11340371](https://doi.org/10.1109/C366505.2025.11340371)
   - Presents a microservices architecture with asynchronous parallel processing, RabbitMQ-based task distribution, and formula parsing with ASTs and dependency graphs to translate spreadsheet logic into SQL.

2. **ETL-Based Architecture for Business Rule Centralization and Version Control** — IEEE Colombian Caribbean Conference (BCC), 2025. [https://doi.org/10.1109/BCC63751.2025.11725832](https://doi.org/10.1109/BCC63751.2025.11725832)
   - Addresses the extraction, standardization, centralization, reuse, and version control of business rules through an ETL-based architecture.

## ⚠️ MVP Status & Future Development

**This project is currently a Minimum Viable Product (MVP)** developed as part of an engineering degree project. It is functional and demonstrates the full architecture, but there are still areas that need refinement before production use.

### Current MVP Limitations

- **Code Quality**: Some components require refactoring and optimization
- **Error Handling**: Enhanced error management and recovery mechanisms needed
- **Testing Coverage**: Additional unit and integration tests required
- **Documentation**: Some technical details and API specifications need expansion
- **Performance**: Optimization opportunities exist across all services
- **Security**: Production-ready security measures need implementation

### Planned Refactoring & Evolution

- **Architecture review**: Consolidate the service boundaries and remove duplication between the API and parsing workflows.
- **Code quality**: Improve error handling, typing, and test coverage across all services.
- **Performance**: Optimize validation, parsing, and database access paths.
- **Documentation**: Expand service-level docs and keep diagrams synchronized with the implementation.
- **Delivery hardening**: Improve CI/CD consistency and release automation.

### Roadmap Highlights

- 🔄 **Phase 1**: Harden the current implementation with better tests and service-level validation.
- 🏗️ **Phase 2**: Refine the service boundaries and keep the parsing pipeline modular.
- ☁️ **Phase 3**: Maintain Docker Swarm deployment with Terraform + Ansible provisioning.
- 🚀 **Phase 4**: Keep GitHub Actions workflows aligned with the release process.
- ⚡ **Phase 5**: Improve observability, throughput, and failure handling.
- 🎯 **Phase 6**: Prepare the platform for a production-grade deployment model.

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

The current architecture is centered on Docker Swarm and a small number of clear runtime responsibilities:

```text
Client Browser
  │
  ▼
Traefik Reverse Proxy
  ├── Web App (Nuxt)
  ├── Core API (FastAPI)
  └── Observability endpoints

Core API
  ├── PostgreSQL
  ├── RabbitMQ
  ├── Database Service (gRPC)
  └── Parsing Subsystem (REST + gRPC)

Typechecking Service
  ├── RabbitMQ consumers
  ├── Database Service (gRPC)
  └── Parsing Subsystem (insert / SQL generation)

Database Service
  ├── MongoDB
  └── Redis
```

The parsing subsystem is intentionally modular:

1. **Excel Reader** orchestrates spreadsheet ingestion and request coordination.
2. **Formula Parser** converts Excel formulas into ASTs.
3. **DDL Generator** turns ASTs into SQL-ready expressions.
4. **SQL Builder** assembles final `CREATE TABLE` and `INSERT` statements.

## 📁 Project Structure

```text
S.L.O.T.H/
├── docs/                        # Architecture diagrams and research material
├── .github/                     # CI/CD workflows and GitHub Actions
├── iac/                         # Terraform, Ansible, Swarm and deployment scripts
├── apps/
│   ├── backend/
│   │   ├── api/                 # Core API service
│   │   ├── parsers/             # Excel parsing subsystem
│   │   └── typechecking/        # RabbitMQ workers
│   ├── connections/
│   │   └── database/            # gRPC proxy for MongoDB and Redis
│   └── web/                     # Nuxt frontend
├── packages/                    # Proto definitions, generated clients and shared utilities
├── tools/                       # Development tooling
└── README.md                    # Repository overview
```

## ☁️ DevOps & Cloud Infrastructure

The current delivery model is based on Docker Swarm, GitHub Actions, and infrastructure provisioning with Terraform plus Ansible.

### 🚀 Infrastructure as Code (IaC)

- **Terraform** provisions the Swarm cluster and supporting AWS resources.
- **Ansible** installs Docker, mounts shared storage, and initializes the Swarm cluster.
- **Environment separation** is handled through dedicated development, staging, and production definitions.

### ⚙️ Container Orchestration

- **Docker Swarm** is the active orchestrator for application deployment.
- **Traefik** handles ingress routing and reverse proxying.
- **Service discovery** and stack updates are managed through Swarm stack files.

### 🔄 CI/CD Pipeline

- **GitHub Actions** runs service tests and image builds.
- **Release workflows** build and publish images, update stack files, and trigger deployments.
- **Versioning** is handled through tagged releases and commit-based stack updates.

### 📊 Observability & Monitoring

- **Prometheus** collects metrics.
- **Grafana** visualizes dashboards and service health.
- **Loki** stores logs.
- **Tempo** provides distributed traces.
- **Grafana Alloy** acts as the collector/forwarder in the current Swarm setup.

## 🚀 Quick Start

### Prerequisites

- **Docker** and access to the Swarm cluster
- **Python 3.12+** with `uv`
- **Node.js 18+** with `npm`
- **Terraform** and **Ansible** for infrastructure provisioning

### Working Locally

1. Clone the repository and open the workspace root.
2. Copy the `.env.example` files for the service you want to run.
3. Start the required infrastructure services first: PostgreSQL, MongoDB, Redis, and RabbitMQ.
4. Start the service you want to work on using its own README.

### Deployment

- Infrastructure provisioning and cluster bootstrap live in `iac/`.
- Swarm deployment definitions live in `iac/swarm/`.
- CI/CD workflows live in `.github/workflows/`.

### Service Map

1. **Core API**: [apps/backend/api/](./apps/backend/api/README.md)
2. **Typechecking**: [apps/backend/typechecking/](./apps/backend/typechecking/README.md)
3. **Parsing subsystem**: [apps/backend/parsers/](./apps/backend/parsers/README.md)
4. **Database proxy**: [apps/connections/database/](./apps/connections/database/README.md)
5. **Frontend**: [apps/web/](./apps/web)

## 🔧 Configuration

Each service owns its own configuration. Copy the matching `.env.example` into `.env` before running it, and keep the values aligned with your environment.

Service-specific configuration details are documented in the README for each service.

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
- **DevOps & Infrastructure**: Docker Swarm, Terraform, Ansible, and CI/CD pipeline improvements
- **Cloud Architecture**: Multi-cloud deployment strategies and cost optimization
- **Security**: Container security scanning, vulnerability assessment, and compliance frameworks

## 📚 Documentation

- **[Applications Overview](./apps/README.md)**: High-level navigation across runtime services.
- **[Backend Services](./apps/backend/README.md)**: Backend architecture and runtime flows.
- **[Excel Parsing System](./apps/backend/parsers/README.md)**: Parsing pipeline and service decomposition.
- **[API Service](./apps/backend/api/README.md)**: Authentication, orchestration, and task APIs.
- **[Typechecking System](./apps/backend/typechecking/README.md)**: RabbitMQ worker architecture and validation flows.
- **[Database Service](./apps/connections/database/README.md)**: gRPC proxy for MongoDB and Redis.
- **[Architecture Diagrams](./docs/diagrams/)**: Source of truth for runtime and deployment diagrams.
- **[Infrastructure](./iac/)**: Terraform, Ansible, and Swarm deployment assets.

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**: Verify that the service ports documented in each README are free.
2. **Missing dependencies**: Confirm that PostgreSQL, MongoDB, Redis, and RabbitMQ are reachable before starting backend services.
3. **Environment variables**: Double-check the copied `.env` files for hostnames, ports, and credentials.
4. **Swarm deployment issues**: Inspect the Swarm stack files and the GitHub Actions deployment logs.
5. **Infrastructure provisioning**: Verify Terraform state and Ansible execution if nodes or shared storage are missing.

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
