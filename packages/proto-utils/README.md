# Protocol Buffer Utilities

This directory contains language-specific utility libraries for working with Protocol Buffer definitions in the ETL Design platform. These packages provide generated code, helper functions, and client utilities for gRPC communication.

## 📋 Overview

The proto-utils packages generate and package Protocol Buffer code for different runtime environments, enabling type-safe communication between microservices.

## 🗂️ Directory Structure

```text
proto-utils/
├── proto-utils-js/          # JavaScript/TypeScript utilities
│   ├── src/
│   │   ├── generated/       # Generated protobuf code
│   │   ├── utils/           # Helper utilities
│   │   └── index.ts         # Main exports
│   ├── package.json         # NPM package configuration
│   └── tsconfig.json        # TypeScript configuration
└── proto-utils-py/          # Python utilities  
    ├── src/
    │   └── proto_utils/     # Python package
    ├── pyproject.toml       # Python package configuration
    └── scripts/             # Build and generation scripts
```

## 📦 Packages

### JavaScript/TypeScript Package

**Package Name**: `@etl-design/packages-proto-utils-js`

**Features**:

- Generated TypeScript definitions from Protocol Buffers
- gRPC client utilities for Node.js and browser environments
- Type-safe service interfaces
- Build configuration with tsup for multiple output formats

**Dependencies**:

- `@grpc/grpc-js`: gRPC implementation for Node.js
- `google-protobuf`: Google's Protocol Buffer runtime
- `protoc`: Protocol Buffer compiler
- `protoc-gen-ts`: TypeScript code generator

**Output Formats**:

- CommonJS (`./dist/index.js`)
- ES Modules (`./dist/index.mjs`)
- TypeScript declarations (`./dist/index.d.ts`)

### Python Package

**Package Name**: `proto-utils`

**Features**:

- Generated Python classes from Protocol Buffers
- gRPC client and server utilities
- Type hints and mypy compatibility
- Integration with Python backend services

**Dependencies**:

- `grpcio`: gRPC Python implementation
- `grpcio-tools`: Protocol Buffer compiler tools

**Requirements**:

- Python 3.12+
- Compatible with backend services in `apps/backend/`

## 🔧 Code Generation

Both packages include scripts for generating Protocol Buffer code from the definitions in [`packages/proto/`](../proto/):

### JavaScript Generation

```bash
cd proto-utils-js/
npm run generate  # Generates TypeScript definitions
npm run build     # Builds distribution packages
```

### Python Generation

```bash
cd proto-utils-py/
./scripts/generate.sh  # Generates Python classes
python -m build        # Builds wheel package
```

## 🚀 Usage

### JavaScript/TypeScript

```typescript
import { DatabaseServiceClient } from '@etl-design/packages-proto-utils-js';

// Create gRPC client
const client = new DatabaseServiceClient('localhost:50051');

// Use type-safe service calls
const response = await client.redisPing({});
```

### Python

```python
from proto_utils import DatabaseServiceClient

# Create gRPC client
client = DatabaseServiceClient('localhost:50051')

# Use generated service methods
response = client.redis_ping({})
```

## 🏗️ Integration

These utilities are used by:

- **Backend Services**: Python services in [`apps/backend/`](../../apps/backend/)
- **Node.js Services**: Formula Parser service
- **Frontend Applications**: Future web interface (planned)
- **Development Tools**: Testing and debugging utilities

## 📊 Generated Services

The utilities provide client code for all gRPC services:

### Database Services

- `DatabaseServiceClient`: Unified database operations
- Redis operations: Key-value storage and caching
- MongoDB operations: Schema and document management
- Task management: Asynchronous operation tracking

### Parser Services

- `FormulaParserClient`: Excel formula parsing
- `DDLGeneratorClient`: SQL DDL generation
- `SQLBuilderClient`: Complete SQL statement construction

## 🔧 Development

### Building JavaScript Package

```bash
cd proto-utils-js/
npm install
npm run generate
npm run build
npm run lint
```

### Building Python Package

```bash
cd proto-utils-py/
uv sync
uv run python -m build
```

## 🧪 Testing

Both packages include integration with the ETL Design testing framework:

- **Unit Tests**: Testing generated code functionality
- **Integration Tests**: Testing gRPC communication
- **Type Tests**: Ensuring type safety and compatibility

---

> **Note**: These packages are automatically generated from Protocol Buffer definitions. Manual modifications should be made to the source `.proto` files, not the generated code.
