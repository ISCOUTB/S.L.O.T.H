from typing import Dict
from services import dtypes
from clients import dtypes_pb2, ddl_generator_pb2, sql_builder_pb2


AST_TYPES_MAPPING: Dict[dtypes_pb2.AstType, dtypes.AstTypes] = {
    dtypes_pb2.AstType.AST_BINARY_EXPRESSION: "binary-expression",
    dtypes_pb2.AstType.AST_CELL_RANGE: "cell-range",
    dtypes_pb2.AstType.AST_FUNCTION: "function",
    dtypes_pb2.AstType.AST_CELL: "cell",
    dtypes_pb2.AstType.AST_NUMBER: "number",
    dtypes_pb2.AstType.AST_LOGICAL: "logical",
    dtypes_pb2.AstType.AST_TEXT: "text",
    dtypes_pb2.AstType.AST_UNARY_EXPRESSION: "unary-expression",
}

REFTYPES_MAPPING: Dict[dtypes_pb2.RefType, dtypes.RefTypes] = {
    dtypes_pb2.RefType.REF_RELATIVE: "relative",
    dtypes_pb2.RefType.REF_ABSOLUTE: "absolute",
    dtypes_pb2.RefType.REF_MIXED: "mixed",
}


def parse_ddlresponse(response: ddl_generator_pb2.DDLResponse) -> dtypes.AllOutputs:
    """
    Converts a DDLResponse protobuf message to a dictionary format.

    Args:
        response (ddl_generator_pb2.DDLResponse): The DDLResponse protobuf message.

    Returns:
        dtypes.AllOutputs: The parsed output as a dictionary.
    """
    ast_type: dtypes_pb2.AstType = response.type
    ast_type_str: dtypes.AstTypes = AST_TYPES_MAPPING.get(ast_type, "unknown")
    if ast_type_str == "binary-expression":
        return {
            "type": ast_type_str,
            "left": parse_ddlresponse(response.left),
            "right": parse_ddlresponse(response.right),
            "operator": response.operator,
            "sql": response.sql,
        }

    if ast_type_str == "cell-range":
        return {
            "type": ast_type_str,
            "start": response.start,
            "end": response.end,
            "cells": [cell for cell in response.cells],
            "columns": [col for col in response.columns],
            "error": response.error,
            "sql": response.sql,
        }

    if ast_type_str == "function":
        return {
            "type": ast_type_str,
            "name": response.name,
            "arguments": [parse_ddlresponse(arg) for arg in response.arguments],
            "sql": response.sql,
        }

    if ast_type_str == "cell":
        return {
            "type": ast_type_str,
            "cell": response.cell,
            "refType": REFTYPES_MAPPING.get(response.refType, ""),
            "column": response.column,
            "error": response.error,
            "sql": response.sql,
        }

    if ast_type_str == "unary-expression":
        return {
            "type": ast_type_str,
            "operand": parse_ddlresponse(response.operand),
            "operator": response.operator,
            "sql": response.sql,
        }

    if ast_type_str == "number":
        value = response.number_value
    elif ast_type_str == "text":
        value = response.text_value
    else:
        value = response.logical_value

    return {
        "type": ast_type_str,
        "value": value,
        "sql": response.sql,
    }


def parse_to_sql_response(
    sql_expressions: dtypes.SQLExpressions,
) -> sql_builder_pb2.BuildSQLResponse:
    """
    Converts SQL expressions to a gRPC response format.

    Args:
        sql_expressions (dtypes.SQLExpressions): Dictionary mapping column names to their SQL expressions.

    Returns:
        sql_builder_pb2.BuildSQLResponse: The response containing the SQL expressions.
    """
    if sql_expressions["error"]:
        return sql_builder_pb2.BuildSQLResponse(
            content=None,
            error=sql_expressions["error"],
        )

    return sql_builder_pb2.BuildSQLResponse(
        content={
            level: sql_builder_pb2.BuildSQLResponse.Content(
                sql_content=[
                    sql_builder_pb2.BuildSQLResponse.SQLContent(
                        sql=expr["sql"],
                        columns=expr["columns"],
                    )
                    for expr in exprs
                ]
            )
            for level, exprs in sql_expressions["content"].items()
        },
        error=None,
    )
