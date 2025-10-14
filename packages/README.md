# Shared Packages

This directory contains reusable packages and utilities that are shared across multiple services in the ETL Design platform. These packages provide common functionality, type definitions, and communication utilities.

## 📋 Overview

The packages are organized as independent modules that can be imported and used by various services throughout the platform. They provide standardized interfaces, Protocol Buffer definitions, and utility functions.

## 🗂️ Directory Structure

```text
packages/
├── proto/                      # Protocol Buffer definitions
├── proto-utils/                # Protocol Buffer utilities
└── messaging-utils/            # RabbitMQ messaging utilities  
```

## 📦 Available Packages

### Protocol Buffer Definitions (`proto/`)

**Purpose**: Central repository for all gRPC service definitions

**Contains**:

- Database service interfaces (Redis, MongoDB, task management)
- Parser service interfaces (formula parsing, DDL generation, SQL building)
- Shared data types and message structures
- Communication contracts between microservices

**Documentation**: [Protocol Buffer Definitions](./proto/README.md)

### Protocol Buffer Utilities (`proto-utils/`)

**Purpose**: Language-specific generated code and client utilities

**Contains**:

- **JavaScript/TypeScript**: `@etl-design/packages-proto-utils-js`
- **Python**: `proto-utils`

**Features**:

- Generated gRPC client libraries
- Type-safe service interfaces
- Helper utilities for client connections
- Multi-format builds (CommonJS, ES modules, TypeScript declarations)

**Documentation**: [Protocol Buffer Utilities](./proto-utils/README.md)

### Messaging Utilities (`messaging-utils/`)

**Purpose**: RabbitMQ communication and message publishing

**Contains**:

- **Python**: `messaging-utils`

**Features**:

- RabbitMQ connection factory and management
- Type-safe message publishers for validation and schema operations
- Standardized message formatting and routing
- Integration with Protocol Buffer message types

**Documentation**: [Messaging Utilities](./messaging-utils/README.md)

### Testing Utilities (`test/`)

**Purpose**: Shared testing utilities and helpers (internal development)

**Note**: This package is for internal testing and development purposes.

## 🔄 Package Dependencies

```text
Application Services
        ↓
    proto-utils  ←──── proto (definitions)
        ↓               ↓
messaging-utils ←──── proto-utils
        ↓
   Applications
```

## 🚀 Usage

### Protocol Buffer Services

```typescript
// JavaScript/TypeScript
import { DatabaseServiceClient } from '@etl-design/packages-proto-utils-js';
const client = new DatabaseServiceClient('localhost:50051');
```

```python
# Python
from proto_utils.database import DatabaseClient
client = DatabaseClient('localhost:50051')
```

### Message Publishing

```python
# Python
from messaging_utils.messaging.publishers import Publisher
from proto_utils.messaging.dtypes import Metadata, ValidationTasks

publisher = Publisher()
task_id = publisher.publish_validation_request(
    routing_key="validation.request",
    file_data=file_content,
    import_name="user_schema_v1",
    metadata=Metadata(filename="data.csv", priority=1),
    task=ValidationTasks.SAMPLE_VALIDATION
)
)
```

## 🏗️ Integration

These packages are used by:

- **Backend Services**: [`apps/backend/`](../apps/backend/)
  - API Service: Uses proto-utils and messaging-utils
  - Typechecking Service: Uses proto-utils and messaging-utils
  - Parser Services: Uses proto-utils

- **Connection Services**: [`apps/connections/`](../apps/connections/)
  - Database Service: Implements proto interfaces

- **Future Services**: Ready for additional microservices

## 🔧 Development

### Building All Packages

```bash
# Protocol Buffer utilities
cd proto-utils/proto-utils-js/
npm run generate && npm run build

cd ../proto-utils-py/
uv run python -m build

# Messaging utilities
cd ../../messaging-utils/messaging-utils-py/
uv run python -m build
```

### Adding New Protocol Buffers

1. Add `.proto` files to [`proto/`](./proto/)
2. Update generation scripts in [`proto-utils/`](./proto-utils/)
3. Regenerate client libraries
4. Update [`messaging-utils/`](./messaging-utils/) if needed

### Versioning

Each package follows semantic versioning:

- **proto**: Version changes when service interfaces change
- **proto-utils**: Version follows proto definitions
- **messaging-utils**: Independent versioning for utility features

## 📊 Package Status

| Package | Language | Status | Version | Purpose |
|---------|----------|--------|---------|---------|
| proto | Proto3 | ✅ Active | - | Service definitions |
| proto-utils-js | TypeScript | ✅ Active | 1.0.0 | JS/TS gRPC clients |
| proto-utils-py | Python | ✅ Active | 0.1.0 | Python gRPC clients |
| messaging-utils-py | Python | ✅ Active | 0.1.0 | RabbitMQ utilities |

## 🧪 Testing

Each package includes comprehensive testing:

- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-package compatibility
- **Type Tests**: TypeScript and Python type checking
- **gRPC Tests**: Service communication validation

---

> **Note**: These packages form the foundation for service communication in the ETL Design platform. Changes should be carefully coordinated to maintain backward compatibility.
