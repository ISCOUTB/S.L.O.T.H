import json
from typing import Dict

import grpc
from proto_utils.generated.parsers import sql_builder_pb2_grpc
from proto_utils.parsers.dtypes import (
    BuildSQLRequest,
    DDLResponse,
    SQLRequestColumnInfo,
)
from proto_utils.parsers.sql_builder_serde import SQLBuilderSerde

from src.core.config import settings


def create_test_request() -> BuildSQLRequest:
    """Create test data for SQL builder based on the example from sql_builder.py."""

    # Convert the example data to DDLResponse format that the protobuf expects
    cols: Dict[str, DDLResponse] = {
        "col1": {
            "type": "number",  # Using string type from dtypes.py
            "sql": "10",
            "number_value": 10.0,
        },
        "col2": {
            "type": "function",
            "sql": "CASE WHEN (col1) > (18) THEN 'Adult' ELSE 'Minor' END",
            "name": "IF",
            "arguments": [
                {
                    "type": "binary-expression",
                    "sql": "(col1) > (18)",
                    "operator": ">",
                    "left": {
                        "type": "cell",
                        "sql": "col1",
                        "cell": "A1",
                        "refType": "relative",
                        "column": "col1",
                    },
                    "right": {
                        "type": "number",
                        "sql": "18",
                        "number_value": 18.0,
                    },
                },
                {
                    "type": "text",
                    "sql": "'Adult'",
                    "text_value": "Adult",
                },
                {
                    "type": "text",
                    "sql": "'Minor'",
                    "text_value": "Minor",
                },
            ],
        },
        "col3": {
            "type": "cell",
            "sql": "col2",
            "cell": "B1",
            "refType": "relative",
            "column": "col2",
        },
        "col4": {
            "type": "number",
            "sql": "10",
            "number_value": 10.0,
        },
    }

    # Create dtypes info
    dtypes: Dict[str, SQLRequestColumnInfo] = {
        "col1": {"type": "INTEGER", "extra": ""},
        "col2": {"type": "TEXT", "extra": ""},
        "col3": {"type": "TEXT", "extra": ""},
        "col4": {"type": "INTEGER", "extra": ""},
    }

    return BuildSQLRequest(table_name="test_table", cols=cols, dtypes=dtypes)


def main():
    """Test the SQL builder service with sample data."""

    # Create test request
    test_request = create_test_request()

    # Create gRPC channel and stub
    channel = grpc.insecure_channel(settings.SQL_BUILDER_CHANNEL)
    stub = sql_builder_pb2_grpc.SQLBuilderStub(channel)

    try:
        # Serialize the request to protobuf
        proto_request = SQLBuilderSerde.serialize_build_sql_request(
            test_request
        )

        print("Sending SQL build request...")
        print(f"Table name: {test_request['table_name']}")
        print(f"Columns: {list(test_request['cols'].keys())}")

        # Make the gRPC call
        response = stub.BuildSQL(proto_request)

        # Deserialize the response
        python_response = SQLBuilderSerde.deserialize_build_sql_response(
            response
        )

        print("\nReceived response:")
        print(json.dumps(python_response, indent=2))

        # Print formatted SQL if successful
        if not python_response.get("error"):
            print("\nGenerated SQL expressions:")
            for level, content in python_response["content"].items():
                print(f"\nLevel {level}:")
                for sql_item in content["sql_content"]:
                    print(f"  SQL: {sql_item['sql']}")
                    print(f"  Columns: {sql_item['columns']}")
        else:
            print(f"\nError: {python_response['error']}")

    except Exception as e:
        print(f"Error calling SQL builder service: {e}")
    finally:
        channel.close()


if __name__ == "__main__":
    main()
