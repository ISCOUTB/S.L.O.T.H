# Excel Parsing Microservices

A distributed system for parsing Excel files and converting Excel formulas into SQL expressions. This system is designed as a collection of microservices that work together to provide a complete ETL (Extract, Transform, Load) solution for Excel data processing.

## Architecture Overview

The Excel Parsing system consists of several specialized microservices that communicate via gRPC and REST APIs:

```text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Excel Reader  │◄──►│  Formula Parser  │    │  DDL Generator  │
│   (REST API)    │    │   (gRPC Server)  │◄──►│  (gRPC Server)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         └────────────────────────┼───────────────────────┘
                                  ▼
                         ┌─────────────────┐
                         │   SQL Builder   │
                         │  (gRPC Server)  │
                         └─────────────────┘
```

## Microservices

### 1. [Excel Reader](./excel-reader/README.md)

- **Type**: REST API Service (Python/FastAPI)
- **Purpose**: Main entry point for processing Excel files
- **Responsibilities**:
  - Accepts Excel file uploads via REST API
  - Extracts data and formulas from Excel sheets
  - Orchestrates communication with other microservices
  - Returns generated SQL statements

### 2. [Formula Parser](./formula-parser/README.md)

- **Type**: gRPC Server (Node.js)
- **Purpose**: Parses Excel formulas into Abstract Syntax Trees (AST)
- **Responsibilities**:
  - Tokenizes Excel formulas
  - Builds Abstract Syntax Trees from formula tokens
  - Provides structured representation of Excel formulas

### 3. [DDL Generator](./ddl-generator/README.md)

- **Type**: gRPC Server (Python)
- **Purpose**: Converts Excel formula ASTs into SQL expressions
- **Responsibilities**:
  - Processes AST nodes into SQL equivalents
  - Maps Excel cell references to SQL column names
  - Handles different types of Excel expressions (functions, operators, etc.)

### 4. [SQL Builder](./sql-builder/README.md)

- **Type**: gRPC Server (Python)
- **Purpose**: Constructs final SQL statements from processed expressions
- **Responsibilities**:
  - Combines individual SQL expressions into complete statements
  - Manages SQL dependencies and execution order
  - Generates CREATE TABLE and INSERT statements

## Protocol Buffers

The system uses Protocol Buffers for inter-service communication, defined in the [`proto/`](./proto/) directory:

- `dtypes.proto` - Common data types (AST, tokens, enums)
- `formula_parser.proto` - Formula parser service interface
- `ddl_generator.proto` - DDL generator service interface  
- `sql_builder.proto` - SQL builder service interface

## Quick Start

### Prerequisites

- Python 3.12.10
- Node.js 18+
- Docker (optional)

### Environment Setup

1. Copy environment configuration:

   ```bash
   cp .env.example .env
   ```

2. Start services in order:

   ```bash
   # Start Formula Parser (Node.js)
   cd formula-parser && npm install && moon run formula-parser:run

   # Start DDL Generator (Python)
   cd ddl-generator && uv sync && uv run python src/server.py

   # Start SQL Builder (Python)  
   cd sql-builder && uv sync && uv run python src/server.py

   # Start Excel Reader (Python)
   cd excel-reader && uv sync && uv run python src/server_rest.py
   ```

### Using the System

Send a POST request to the Excel Reader service:

```bash
curl -X POST "http://localhost:8001/excel-parser" \
  -H "Content-Type: multipart/form-data" \
  -F "spreadsheet=@your_file.xlsx" \
  -F "table_name=my_table" \
  -F 'dtypes_str={"Sheet1": {"col1": {"type": "INTEGER"}, "col2": {"type": "TEXT"}}}'
```

## Development

### Project Structure

```text
excel-parsing/
├── proto/                 # Protocol Buffer definitions
├── excel-reader/         # REST API service
├── formula-parser/       # Formula parsing service
├── ddl-generator/        # DDL generation service
├── sql-builder/          # SQL building service
├── .env.example          # Environment configuration template
└── README.md            # This file
```

### Adding New Features

1. Update relevant Protocol Buffer definitions in `proto/`
2. Regenerate client code for affected services
3. Implement feature in appropriate service(s)
4. Update documentation

## Contributing

1. Follow the established code style for each language (Python: PEP 8, JavaScript: Standard)
2. Write tests for new functionality
3. Update documentation when adding features
4. Use meaningful commit messages

## License

This project is part of an engineering thesis project at Universidad Tecnológica de Bolívar.
