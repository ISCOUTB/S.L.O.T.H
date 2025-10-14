# Protocol Buffer Definitions

This directory contains Protocol Buffer (.proto) definitions for all gRPC services in the ETL Design platform. These definitions establish the communication contracts between microservices and define the data structures used throughout the system.

## 📋 Overview

The protocol buffers are organized into two main categories:

- **Database Services**: gRPC definitions for database operations and task management
- **Parser Services**: gRPC definitions for Excel formula parsing and SQL generation

## 🗂️ Directory Structure

```text
proto/
├── database/                    # Database service definitions
│   ├── database.proto          # Main database service interface
│   ├── mongo.proto             # MongoDB operations
│   ├── redis.proto             # Redis operations
│   └── utils.proto             # Shared utilities and data types
└── parsers/                     # Excel parsing service definitions
    ├── ddl_generator.proto     # DDL generation service
    ├── dtypes.proto            # Shared data types and AST structures
    ├── formula_parser.proto    # Formula parsing service
    └── sql_builder.proto       # SQL building service
```

## 🗄️ Database Services

### DatabaseService (`database/database.proto`)

Main unified interface for database operations including:

- **Redis Operations**: Key-value storage, caching, and cache management
- **MongoDB Operations**: JSON schema management and document storage
- **Task Management**: Asynchronous task tracking and status updates

**Key Features**:

- Unified API for multiple database systems
- Task lifecycle management with state tracking
- Cache operations with TTL support
- JSON schema validation and versioning

### Supporting Services

- **`mongo.proto`**: MongoDB-specific operations for schema management
- **`redis.proto`**: Redis operations for caching and key-value storage
- **`utils.proto`**: Shared data types and utility structures

## 🔧 Parser Services

### Formula Parser (`parsers/formula_parser.proto`)

Converts Excel formulas into structured representations:

- **Input**: Raw Excel formula strings (e.g., `=SUM(A1:A5)`)
- **Output**: Tokens and Abstract Syntax Trees (AST)
- **Purpose**: First stage of Excel-to-SQL transformation pipeline

### DDL Generator (`parsers/ddl_generator.proto`)

Transforms parsed formulas into SQL expressions:

- **Input**: AST from Formula Parser + column mappings
- **Output**: SQL expressions and DDL statements
- **Features**: Handles cell references, ranges, functions, and operators

### SQL Builder (`parsers/sql_builder.proto`)

Constructs complete SQL statements:

- **Input**: DDL responses + column type information
- **Output**: Ready-to-execute SQL statements
- **Purpose**: Final stage of Excel-to-SQL transformation

### Data Types (`parsers/dtypes.proto`)

Shared data structures for parsing operations:

- **AST Types**: Binary expressions, functions, cell references, literals
- **Reference Types**: Relative, absolute, and mixed cell references
- **Token Structures**: Formula tokenization for parsing

## 🔄 Service Communication Flow

```text
Excel Formula → Formula Parser → DDL Generator → SQL Builder → Database Service
     ↓               ↓               ↓              ↓              ↓
   String          Tokens          AST           SQL         Storage
                    AST
```

## 🚀 Usage

These Protocol Buffer definitions are used by:

- **Backend Services**: [`apps/backend/parsers/`](../../apps/backend/parsers/)
- **Database Service**: [`apps/connections/`](../../apps/connections/)
- **Client Libraries**: [`packages/proto-utils/`](../proto-utils/)

## 🔧 Code Generation

Protocol buffer classes are generated for different languages:

- **Python**: Used by backend services
- **JavaScript/TypeScript**: Used by frontend and Node.js services
- **Rust**: Planned for future high-performance services

## 📖 Protocol Buffer Structure

### AST Node Types

- `AST_BINARY_EXPRESSION`: Mathematical operations (+, -, *, /)
- `AST_CELL_RANGE`: Range references (A1:B5)
- `AST_FUNCTION`: Excel functions (SUM, AVERAGE, etc.)
- `AST_CELL`: Individual cell references (A1, $B$2)
- `AST_NUMBER`: Numeric literals
- `AST_LOGICAL`: Boolean values (TRUE/FALSE)
- `AST_TEXT`: String literals
- `AST_UNARY_EXPRESSION`: Unary operations (negation)

### Reference Types

- `REF_RELATIVE`: Adjusts when copied (A1)
- `REF_ABSOLUTE`: Fixed when copied ($A$1)
- `REF_MIXED`: Partially fixed ($A1, A$1)

## 🏗️ Integration

These definitions integrate with:

- **gRPC Services**: All parsing and database microservices
- **Data Validation**: Type-safe communication between services
- **Documentation**: Self-documenting API contracts
- **Development Tools**: IDE support and code generation

---

> **Note**: These Protocol Buffer definitions serve as the single source of truth for service communication. All microservices must implement these contracts exactly as defined.
