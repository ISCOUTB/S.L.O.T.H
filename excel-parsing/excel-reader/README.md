# Excel Reader Service

A FastAPI-based REST service that serves as the main entry point for the Excel Parsing system. This service processes Excel files, extracts formulas and data, and orchestrates communication with other microservices to generate SQL statements.

## Overview

The Excel Reader service is responsible for:

- Accepting Excel file uploads via REST API
- Extracting data and formulas from Excel worksheets
- Coordinating with Formula Parser, DDL Generator, and SQL Builder services
- Processing Excel files in various formats (.xlsx, .xls, .csv)
- Returning generated SQL CREATE and INSERT statements

## Architecture

```text
┌─────────────────┐
│   Client        │
│                 │
└─────────┬───────┘
          │ HTTP POST
          ▼
┌─────────────────┐
│  Excel Reader   │◄──► Formula Parser (gRPC)
│   (FastAPI)     │◄──► DDL Generator (gRPC)
│                 │◄──► SQL Builder (gRPC)
└─────────────────┘
```

## Features

- **Multi-format Support**: Handles .xlsx, .xls, and .csv files
- **Formula Parsing**: Extracts and processes Excel formulas
- **Data Type Mapping**: Maps Excel data types to SQL equivalents
- **Performance Monitoring**: Built-in performance tracking for operations
- **Flexible Configuration**: Environment-based configuration
- **CORS Support**: Enabled for cross-origin requests

## API Endpoints

### POST /excel-parser

Processes an Excel file and returns generated SQL statements.

**Request:**

- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `spreadsheet` (file): Excel file to process
  - `dtypes_str` (string): JSON string defining column data types
  - `table_name` (string): Base name for generated tables
  - `limit` (int, optional): Maximum number of rows to process (default: 50)

**Example Request:**

```bash
curl -X POST "http://localhost:8001/excel-parser" \
  -H "Content-Type: multipart/form-data" \
  -F "spreadsheet=@sample.xlsx" \
  -F "table_name=users" \
  -F 'dtypes_str={"Sheet1": {"id": {"type": "INTEGER", "extra": "PRIMARY KEY"}, "name": {"type": "TEXT"}, "age": {"type": "INTEGER"}}}'
```

**Response:**

```json
{
  "Sheet1": "CREATE TABLE users_Sheet1 (id INTEGER PRIMARY KEY, name TEXT, age INTEGER); INSERT INTO users_Sheet1 (id, name, age) VALUES (1, 'John', 25);"
}
```

## Configuration

Environment variables (see `.env.example`):

```env
# Excel Reader Configuration
EXCEL_READER_HOST="localhost"
EXCEL_READER_PORT="8001"
EXCEL_READER_DEBUG=True

# Dependent Services
FORMULA_PARSER_HOST="localhost"
FORMULA_PARSER_PORT="50052"
DDL_GENERATOR_HOST="localhost"
DDL_GENERATOR_PORT="50053"
SQL_BUILDER_HOST="localhost"
SQL_BUILDER_PORT="50054"
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
   uv run python src/server_rest.py
   ```

## Development

### Project Structure

```text
excel-reader/
├── src/
│   ├── main.py              # Core processing logic
│   ├── server_rest.py       # FastAPI REST server
│   ├── clients/             # gRPC client implementations
│   │   ├── ddl_generator/   # DDL Generator client
│   │   ├── formula_parser/  # Formula Parser client
│   │   ├── sql_builder/     # SQL Builder client
│   │   └── dtypes/          # Common data types
│   ├── core/
│   │   └── config.py        # Configuration management
│   ├── services/
│   │   ├── get_data.py      # Excel data extraction
│   │   ├── utils.py         # Utility functions
│   │   └── dtypes.py        # Type definitions
│   └── tests/               # Test files
├── scripts/                 # Utility scripts
├── pyproject.toml          # Project configuration
├── Dockerfile              # Container configuration
└── README.md               # This file
```

### Key Components

#### Core Processing (`main.py`)

The main processing pipeline includes:

1. **Formula Parsing**: Extracts formulas and sends them to Formula Parser service
2. **DDL Generation**: Converts parsed ASTs to SQL expressions via DDL Generator
3. **SQL Building**: Constructs final SQL statements using SQL Builder service

#### Data Extraction (`services/get_data.py`)

Handles reading various Excel file formats:

- OpenPyXL for .xlsx/.xls files
- CSV parsing with conversion to Excel format
- Formula extraction and cell data processing

#### REST API (`server_rest.py`)

FastAPI application providing:

- File upload handling
- Request validation
- Response formatting
- CORS configuration

### Running Tests

```bash
uv run python -m pytest src/tests/
```

### Performance Monitoring

The service includes built-in performance monitoring using the `@monitor_performance` decorator. Monitor logs to track:

- Excel file processing time
- Formula parsing duration
- SQL generation performance

## Dependencies

### Core Dependencies

- **FastAPI**: Web framework for building APIs
- **openpyxl**: Excel file reading and manipulation
- **grpcio**: gRPC client for service communication
- **pydantic**: Data validation and settings management

### Service Communication

The service communicates with:

- **Formula Parser** (port 50052): Excel formula tokenization and AST generation
- **DDL Generator** (port 50053): AST to SQL expression conversion
- **SQL Builder** (port 50054): Final SQL statement construction

## Error Handling

The service handles various error conditions:

- **Invalid file formats**: Returns HTTP 400 with descriptive error
- **Empty files**: Validates file content before processing
- **Service communication errors**: Graceful degradation with error reporting
- **Invalid JSON parameters**: Validates dtypes_str parameter

## Monitoring and Logging

- **Structured Logging**: Uses Python's logging module with INFO level
- **Performance Tracking**: Built-in timing for operations
- **Request Logging**: Logs incoming requests and processing status
- **Error Reporting**: Detailed error messages for debugging
