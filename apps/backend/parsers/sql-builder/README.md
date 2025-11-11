# SQL Builder Service

A Python gRPC service that constructs complete SQL statements from individual DDL expressions and column metadata. This service is responsible for assembling final CREATE TABLE and INSERT statements by managing dependencies and execution order of SQL expressions.

## Overview

The SQL Builder service provides:

- **SQL Statement Assembly**: Combines individual SQL expressions into complete statements
- **Dependency Resolution**: Manages execution order of interdependent SQL expressions
- **Schema Generation**: Creates complete CREATE TABLE statements with all columns
- **Data Insertion**: Generates INSERT statements with proper value ordering
- **Error Management**: Validates SQL expressions and reports construction errors

## Architecture

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  DDL Generator  │───►│   SQL Builder   │───►│  Final SQL      │
│                 │    │   (Python)      │    │  Statements     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Dependencies:   │
                       │ • Graph Analysis│
                       │ • Order Sorting │
                       │ • SQL Validation│
                       └─────────────────┘
```

## Features

- **Dependency Graph Construction**: Builds dependency graphs for SQL expressions
- **Topological Sorting**: Orders SQL statements based on dependencies
- **SQL Statement Generation**: Creates valid CREATE TABLE and INSERT statements
- **Column Type Management**: Handles different SQL data types and constraints
- **Expression Validation**: Validates SQL expressions before assembly
- **Error Reporting**: Comprehensive error handling and reporting

## gRPC Service Definition

The service implements the `SQLBuilder` service defined in `sql_builder.proto`:

```proto
service SQLBuilder {
    rpc BuildSQL(BuildSQLRequest) returns (BuildSQLResponse);
}

message BuildSQLRequest {
    message ColumnInfo {
        string type = 1; // Data type of the column (e.g., "INTEGER", "TEXT")
        string extra = 2; // Additional SQL constraints (e.g., "NOT NULL", "PRIMARY KEY")
    }

    map<string, ddl_generator.DDLResponse> cols = 1;
    map<string, ColumnInfo> dtypes = 2;
    string table_name = 3;
}

message BuildSQLResponse {
    message Sentence {
        repeated string sql = 1;
    }

    map<int32, Sentence> content = 1;
    optional string error = 2;
}
```

## Key Capabilities

### Dependency Resolution

The service analyzes SQL expressions to identify dependencies and creates a proper execution order:

```text
Example Dependencies:
column_c = column_a + column_b  # Depends on column_a and column_b
column_d = column_c * 2         # Depends on column_c
```

**Execution Order**:

1. `column_a` and `column_b` (independent)
2. `column_c` (depends on a and b)
3. `column_d` (depends on c)

### SQL Statement Types

#### CREATE TABLE Statements

Generates complete table creation statements with:

- Column definitions
- Data types
- Constraints (PRIMARY KEY, NOT NULL, etc.)
- Generated columns (calculated fields)

#### INSERT Statements

Creates data insertion statements with:

- Proper value ordering
- Type conversion
- Expression evaluation

### Column Type Support

| SQL Type | Description | Example |
|----------|-------------|---------|
| `INTEGER` | Whole numbers | `42`, `-10` |
| `NUMERIC` | Decimal numbers | `3.14`, `99.99` |
| `TEXT` | String values | `'John Doe'`, `'Sample Text'` |
| `BOOLEAN` | True/false values | `TRUE`, `FALSE` |
| `DATE` | Date values | `'2023-01-01'` |
| `TIMESTAMP` | Date and time | `'2023-01-01 12:00:00'` |

### Expression Types

#### Simple Columns

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER
);
```

#### Calculated Columns

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    birth_year INTEGER,
    current_year INTEGER,
    age INTEGER GENERATED ALWAYS AS (current_year - birth_year) STORED
);
```

#### Complex Expressions

```sql
CREATE TABLE users (
    salary NUMERIC,
    bonus NUMERIC,
    is_eligible BOOLEAN GENERATED ALWAYS AS (salary > 50000) STORED,
    total_compensation NUMERIC GENERATED ALWAYS AS (salary + bonus) STORED
);
```

## Installation

### Prerequisites

- Python 3.12.10
- uv (package manager)

### Setup

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Configure environment:

   ```bash
   cp ../.env.example .env
   # Edit .env with your configuration
   ```

3. Start the service:

   ```bash
   uv run python src/server.py
   ```

## Configuration

Environment variables (see `.env.example`):

```env
# SQL Builder Configuration
SQL_BUILDER_HOST="localhost"
SQL_BUILDER_PORT="50054"
SQL_BUILDER_DEBUG=True
```

## Development

### Project Structure

```text
sql-builder/
├── src/
│   ├── server.py                    # gRPC server setup
│   ├── client.py                    # Test client
│   ├── clients/                     # Generated Protocol Buffer files
│   │   ├── sql_builder_pb2.py
│   │   ├── sql_builder_pb2.pyi
│   │   ├── sql_builder_pb2_grpc.py
│   │   ├── ddl_generator_pb2.py
│   │   ├── ddl_generator_pb2.pyi
│   │   ├── ddl_generator_pb2_grpc.py
│   │   ├── dtypes_pb2.py
│   │   ├── dtypes_pb2.pyi
│   │   ├── dtypes_pb2_grpc.py
│   │   └── utils.py                 # Protocol Buffer utilities
│   ├── core/
│   │   └── config.py                # Configuration management
│   ├── handlers/
│   │   └── sql_builder.py           # Request handling logic
│   ├── services/
│   │   ├── sql_builder.py           # Main service logic
│   │   ├── dtypes.py                # Type definitions
│   │   ├── create_graph.py          # Dependency analysis
│   │   ├── builder.py               # SQL statement construction
│   │   └── utils.py                 # SQL validation utilities
│   └── tests/                       # Test files
├── scripts/                         # Utility scripts
├── pyproject.toml                   # Project configuration
├── Dockerfile                       # Container configuration
└── README.md                        # This file
```

### Key Components

#### Main Service (`services/sql_builder.py`)

The entry point that orchestrates the SQL building process:

```python
def build_sql(request_data):
    # 1. Parse input data
    # 2. Analyze dependencies
    # 3. Build dependency graph
    # 4. Generate SQL statements in order
    # 5. Return structured response
```

#### Dependency Analyzer (`services/dependency_analyzer.py`)

Analyzes SQL expressions to identify column dependencies:

- **Graph Construction**: Builds dependency graphs using igraph
- **Cycle Detection**: Identifies circular dependencies
- **Topological Sorting**: Orders statements for execution

#### Statement Builder (`services/statement_builder.py`)

Constructs final SQL statements:

- **CREATE TABLE**: Assembles table creation statements
- **Column Definitions**: Handles regular and generated columns
- **INSERT Statements**: Creates data insertion statements
- **Constraint Handling**: Manages PRIMARY KEY, NOT NULL, etc.

#### Validators (`services/validators.py`)

Validates SQL expressions and data types:

- **SQL Syntax**: Validates generated SQL expressions
- **Type Compatibility**: Ensures data type consistency
- **Constraint Validation**: Verifies constraint compatibility

### Error Handling

The service provides comprehensive error handling:

- **Circular Dependencies**: Detects and reports dependency cycles
- **Missing Dependencies**: Identifies unresolved column references

## API Examples

### Simple Table Creation

**Input**:

```json
{
  "cols": {
    "id": {
      "type": "cell",
      "sql": "id",
      "column": "id"
    },
    "name": {
      "type": "text",
      "sql": "'John Doe'",
      "text_value": "John Doe"
    }
  },
  "dtypes": {
    "id": {"type": "INTEGER", "extra": "PRIMARY KEY"},
    "name": {"type": "TEXT", "extra": "NOT NULL"}
  },
  "table_name": "users"
}
```

**Output**:

```json
{
  "content": {
    "0": {
      "sql": [
        "CREATE TABLE users (",
        "  id INTEGER PRIMARY KEY,",
        "  name TEXT NOT NULL",
        ");"
      ]
    }
  }
}
```

### Table with Calculated Columns

**Input**:

```json
{
  "cols": {
    "salary": {
      "type": "number",
      "sql": "50000",
      "number_value": 50000
    },
    "bonus": {
      "type": "number",
      "sql": "5000",
      "number_value": 5000
    },
    "total": {
      "type": "binary-expression",
      "sql": "salary + bonus",
      "operator": "+"
    }
  },
  "dtypes": {
    "salary": {"type": "NUMERIC"},
    "bonus": {"type": "NUMERIC"},
    "total": {"type": "NUMERIC"}
  },
  "table_name": "payroll"
}
```

**Output**:

```json
{
  "content": {
    "0": {
      "sql": [
        "CREATE TABLE payroll (",
        "  salary NUMERIC,",
        "  bonus NUMERIC,",
        "  total NUMERIC GENERATED ALWAYS AS (salary + bonus) STORED",
        ");"
      ]
    },
    "1": {
      "sql": [
        "INSERT INTO payroll (salary, bonus) VALUES (50000, 5000);"
      ]
    }
  }
}
```

### Complex Dependencies

**Input**: Multiple interconnected calculated columns

**Output**: Properly ordered SQL statements ensuring dependencies are resolved in correct sequence.

## Dependencies

### Core Dependencies

- **grpcio**: gRPC server implementation
- **grpcio-tools**: Protocol Buffer compilation
- **igraph**: Graph analysis for dependency resolution
<!-- - **sqlglot**: SQL parsing and validation -->
- **pydantic-settings**: Configuration management

### Dependency Analysis

The service uses igraph for:

- **Graph Construction**: Building dependency relationships
- **Cycle Detection**: Identifying circular dependencies
- **Topological Sorting**: Ordering statements for execution

<!-- ### SQL Processing

Uses sqlglot for:

- **SQL Parsing**: Analyzing SQL expression syntax
- **Validation**: Ensuring SQL correctness
- **Optimization**: Optimizing generated queries -->

## Monitoring and Logging

- **Debug Mode**: Detailed logging when `SQL_BUILDER_DEBUG=True`
- **Request Logging**: Logs incoming requests and generated SQL
- **Dependency Analysis**: Logs dependency resolution process
- **Error Tracking**: Comprehensive error reporting with context
- **Performance Monitoring**: Built-in timing for SQL generation
