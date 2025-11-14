# DDL Generator Service

A Python gRPC service that converts Excel formula Abstract Syntax Trees (AST) into SQL expressions. This service is responsible for translating the hierarchical structure of Excel formulas into equivalent SQL statements that can be used in database queries.

## Overview

The DDL Generator service provides:

- **AST to SQL Conversion**: Transforms Excel formula ASTs into SQL expressions
- **Cell Reference Mapping**: Maps Excel cell references (A1, B2) to SQL column names
- **Type Preservation**: Maintains data types through the conversion process
- **Expression Handling**: Supports all Excel expression types (binary, unary, functions)
- **Error Management**: Comprehensive error handling and reporting

## Architecture

```text
┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Formula Parser  │───►│  DDL Generator  │───►│   SQL Builder   │
│                  │    │   (Python)      │    │                 │
└──────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │ Generator Maps: │
                        │ • Cell Refs     │
                        │ • Functions     │
                        │ • Operators     │
                        │ • Literals      │
                        └─────────────────┘
```

## Features

- **Comprehensive AST Processing**: Handles all Excel AST node types
- **Column Mapping**: Intelligent mapping of Excel columns to SQL column names
- **SQL Expression Generation**: Creates valid SQL expressions from Excel formulas
- **Type Safety**: Preserves and converts data types appropriately
- **Operator Translation**: Maps Excel operators to SQL equivalents
- **Function Support**: Converts Excel functions to SQL functions
- **Range Handling**: Processes Excel cell ranges for aggregate operations

## gRPC Service Definition

The service implements the `DDLGenerator` service defined in `ddl_generator.proto`:

```proto
service DDLGenerator {
    rpc GenerateDDL(DDLRequest) returns (DDLResponse) {}
}

message DDLRequest {
    dtypes.AST ast = 1;
    map<string, string> columns = 2;
}

message DDLResponse {
    dtypes.AstType type = 1;
    string sql = 2;
    // ... other fields for different node types
}
```

## Supported Conversions

### Cell References

| Excel    | SQL Column Mapping   | Result      |
| -------- | -------------------- | ----------- |
| `A1`   | `{"A": "user_id"}` | `user_id` |
| `B2`   | `{"B": "name"}`    | `name`    |
| `$C$1` | `{"C": "amount"}`  | `amount`  |

### Mathematical Operators

| Excel Operator | SQL Operator | Example                             |
| -------------- | ------------ | ----------------------------------- |
| `+`          | `+`        | `A1 + B1` → `user_id + amount` |
| `-`          | `-`        | `A1 - B1` → `user_id - amount` |
| `*`          | `*`        | `A1 * B1` → `user_id * amount` |
| `/`          | `/`        | `A1 / B1` → `user_id / amount` |

### Comparison Operators

| Excel Operator | SQL Operator | Example                               |
| -------------- | ------------ | ------------------------------------- |
| `=`          | `=`        | `A1 = B1` → `user_id = amount`   |
| `<>`         | `!=`       | `A1 <> B1` → `user_id != amount` |
| `>`          | `>`        | `A1 > B1` → `user_id > amount`   |
| `>=`         | `>=`       | `A1 >= B1` → `user_id >= amount` |
| `<`          | `<`        | `A1 < B1` → `user_id < amount`   |
| `<=`         | `<=`       | `A1 <= B1` → `user_id <= amount` |

### Functions

> **Note**: Currently limited to same-row operations only. Range-based aggregations are not fully implemented.

### Logical Functions

> **Note**: These functions work with same-row cell references only.

| Excel Function        | SQL Equivalent                          | Example                                            |
| --------------------- | --------------------------------------- | -------------------------------------------------- |
| `IF(A1>0, B1, C1)`  | `CASE WHEN ... THEN ... ELSE ... END` | `CASE WHEN user_id > 0 THEN name ELSE email END` |
| `AND(A1>0, B1<100)` | `... AND ...`                         | `user_id > 0 AND amount < 100`                   |
| `OR(A1>0, B1<100)`  | `... OR ...`                          | `user_id > 0 OR amount < 100`                    |

## Current Limitations & Pending Features

### ⚠️ Function Implementation Status

**Important**: This is an MVP implementation with limited function support. Many Excel functions are **not yet implemented** and will require future development.

### Supported Function Scope

The current implementation **only supports functions that operate on elements from the same row**. This means:

✅ **Supported Scenarios**:

- `A1 + B1` (same row operations)
- `IF(A1>0, B1, C1)` (conditions using same-row data)
- `A1 * B1 + C1` (mathematical operations within the same row)

❌ **Not Yet Supported**:

- Cross-row references: `A1 + A2` (different rows)
- Aggregate functions across multiple rows: `SUM(A1:A10)` (range operations)
- Inter-row dependencies and calculations
- Complex range-based functions

### Pending Function Categories

The following Excel function categories are **planned for future implementation**:

#### Mathematical Functions

- `POWER(A1, 2)` - Exponentiation
- `SQRT(A1)` - Square root
- `ABS(A1)` - Absolute value
- `ROUND(A1, 2)` - Rounding functions
- `MOD(A1, B1)` - Modulo operations

#### Text Functions

- `CONCATENATE(A1, B1)` - String concatenation
- `LEFT(A1, 5)` - Substring operations
- `RIGHT(A1, 3)` - Right substring
- `MID(A1, 2, 4)` - Middle substring
- `LEN(A1)` - String length
- `UPPER(A1)`, `LOWER(A1)` - Case conversion

#### Date/Time Functions

- `TODAY()` - Current date
- `NOW()` - Current date and time
- `DATE(A1, B1, C1)` - Date construction
- `YEAR(A1)`, `MONTH(A1)`, `DAY(A1)` - Date parts
- `DATEDIF(A1, B1, "D")` - Date differences

#### Lookup Functions

- `VLOOKUP(A1, range, col, FALSE)` - Vertical lookup
- `HLOOKUP(A1, range, row, FALSE)` - Horizontal lookup
- `INDEX(range, row, col)` - Index-based lookup
- `MATCH(A1, range, 0)` - Value matching

#### Advanced Logical Functions

- `IFERROR(A1/B1, 0)` - Error handling
- `ISBLANK(A1)` - Blank value checking
- `ISNUMBER(A1)` - Type checking functions

### Range Operation Limitations

Currently, the system has significant limitations with range operations:

- **Range Functions**: Functions like `SUM(A1:A10)` are partially implemented but not fully functional
- **Cross-Row Dependencies**: Cannot handle formulas that reference multiple rows
- **Dynamic Ranges**: No support for dynamic or variable ranges
- **Array Formulas**: Excel array formulas are not supported

### Future Development Roadmap

1. **Phase 1**: Complete same-row function implementations
2. **Phase 2**: Add support for cross-row references and dependencies
3. **Phase 3**: Implement range-based aggregate functions
4. **Phase 4**: Add advanced Excel functions (lookup, date/time, text manipulation)
5. **Phase 5**: Support for array formulas and complex range operations

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
# DDL Generator Configuration
DDL_GENERATOR_HOST="localhost"
DDL_GENERATOR_PORT="50053"
DDL_GENERATOR_DEBUG=True
```

## Development

### Project Structure

```text


ddl-generator/
├── src/
│   ├── server.py                    # gRPC server setup
│   ├── client.py                    # Test client
│   ├── clients/                     # Generated Protocol Buffer files
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
│   │   └── ddl_generator.py         # Request handling logic
│   ├── services/
│   │   ├── ddl_generator.py         # Main service logic
│   │   ├── dtypes.py                # Type definitions
│   │   └── generator.py             # Core generation logic
│   │   └── sql.py                   # SQL Generation based on functions
│   │   └── utils.py
│   └── tests/                       # Test files
├── scripts/                         # Utility scripts
├── pyproject.toml                   # Project configuration
├── Dockerfile                       # Container configuration
└── README.md                        # This file
```

### Key Components

#### Main Service (`services/ddl_generator.py`)

The entry point that processes input data and routes to appropriate generators:

```python
def generate_ddl(data: InputData) -> AllOutputs:
    ast: AST = data["ast"]
    columns: Dict[str, str] = data["columns"]
    return MAPS[ast["type"]](ast, columns)
```

#### Generator Maps

The service uses a mapping system to route different AST node types to their corresponding generators:

- **Cell References** → `cell.py`
- **Binary Expressions** → `binary_expression.py`
- **Functions** → `function.py`
- **Literals** → `literals.py`
- **Cell Ranges** → `cell_range.py`
- **Unary Expressions** → `unary_expression.py`

#### Type System

The service maintains a comprehensive type system for:

- **AST Node Types**: Mapping between Protocol Buffer and Python types
- **SQL Data Types**: Converting Excel types to SQL equivalents
- **Column Mappings**: Managing Excel column to SQL column relationships

### Error Handling

The service provides comprehensive error handling:

- **Unsupported AST Types**: Reports unknown node types
- **Invalid Column Mappings**: Handles missing column references
- **Malformed AST**: Validates AST structure
- **SQL Generation Errors**: Reports issues in SQL construction

## API Examples

### Cell Reference Conversion

**Input**:

```json
{
  "ast": {
    "type": "cell",
    "name": "A1",
    "refType": "relative"
  },
  "columns": {
    "A": "user_id"
  }
}
```

**Output**:

```json
{
  "type": "cell",
  "sql": "user_id",
  "cell": "A1",
  "refType": "relative",
  "column": "user_id"
}
```

### Binary Expression Conversion

**Input**:

```json
{
  "ast": {
    "type": "binary-expression",
    "operator": "+",
    "left": {"type": "cell", "name": "A1"},
    "right": {"type": "number", "value": 10}
  },
  "columns": {
    "A": "amount"
  }
}
```

**Output**:

```json
{
  "type": "binary-expression",
  "sql": "amount + 10",
  "operator": "+",
  "left": {"sql": "amount", "type": "cell"},
  "right": {"sql": "10", "type": "number"}
}
```

### Function Conversion

**Input**:

```json
{
  "ast": {
    "type": "function",
    "name": "SUM",
    "arguments": [{
      "type": "cell-range",
      "start": "A1",
      "end": "A10"
    }]
  },
  "columns": {
    "A": "sales"
  }
}
```

**Output**:

```json
{
  "type": "function",
  "sql": "SUM(sales)",
  "name": "SUM",
  "arguments": [{
    "sql": "sales",
    "type": "cell-range"
  }]
}
```

## Dependencies

### Core Dependencies

- **grpcio**: gRPC server implementation
- **grpcio-tools**: Protocol Buffer compilation
- **pydantic-settings**: Configuration management
- **asyncio**: Asynchronous server operations

## Monitoring and Logging

- **Debug Mode**: Detailed logging when `DDL_GENERATOR_DEBUG=True`
- **Request Logging**: Logs incoming AST structures and generated SQL
- **Error Tracking**: Comprehensive error reporting with context
- **Performance Monitoring**: Built-in timing for conversion operations
