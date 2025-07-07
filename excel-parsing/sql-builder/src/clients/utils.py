from typing import Dict
from services import dtypes
from clients import dtypes_pb2, ddl_generator_pb2, sql_builder_pb2


AST_TYPES_TO_PROTO: Dict[dtypes.AstTypes, dtypes_pb2.AstType] = {
    "binary-expression": dtypes_pb2.AstType.AST_BINARY_EXPRESSION,
    "cell-range": dtypes_pb2.AstType.AST_CELL_RANGE,
    "function": dtypes_pb2.AstType.AST_FUNCTION,
    "cell": dtypes_pb2.AstType.AST_CELL,
    "number": dtypes_pb2.AstType.AST_NUMBER,
    "logical": dtypes_pb2.AstType.AST_LOGICAL,
    "text": dtypes_pb2.AstType.AST_TEXT,
}

REFTYPES_TO_PROTO: Dict[dtypes.RefTypes, dtypes_pb2.RefType] = {
    "relative": dtypes_pb2.RefType.REF_RELATIVE,
    "absolute": dtypes_pb2.RefType.REF_ABSOLUTE,
    "mixed": dtypes_pb2.RefType.REF_MIXED,
}


def parse_output_to_proto(output: dtypes.AllOutputs) -> ddl_generator_pb2.DDLResponse:
    ast_type: dtypes_pb2.AstType = AST_TYPES_TO_PROTO.get(
        output["type"], dtypes_pb2.AstType.AST_UNKNOWN
    )
    sql = str(output.get("sql", ""))

    if ast_type == dtypes_pb2.AstType.AST_CELL:
        return ddl_generator_pb2.DDLResponse(
            type=ast_type,
            cell=output["cell"],
            refType=REFTYPES_TO_PROTO.get(
                output["refType"], dtypes_pb2.RefType.REF_UNKNOWN
            ),
            column=output.get("column", ""),
            error=output.get("error", ""),
            sql=sql,
        )

    if ast_type in {
        dtypes_pb2.AstType.AST_NUMBER,
        dtypes_pb2.AstType.AST_LOGICAL,
        dtypes_pb2.AstType.AST_TEXT,
    }:
        response = ddl_generator_pb2.DDLResponse(type=ast_type, sql=sql)
        if ast_type == dtypes_pb2.AstType.AST_NUMBER:
            response.number_value = output["value"]
        if ast_type == dtypes_pb2.AstType.AST_LOGICAL:
            response.logical_value = output["value"]
        if ast_type == dtypes_pb2.AstType.AST_TEXT:
            response.text_value = output["value"]
        return response

    if ast_type == dtypes_pb2.AstType.AST_BINARY_EXPRESSION:
        return ddl_generator_pb2.DDLResponse(
            type=ast_type,
            operator=output["operator"],
            left=parse_output_to_proto(output["left"]),
            right=parse_output_to_proto(output["right"]),
            sql=sql,
        )

    if ast_type == dtypes_pb2.AstType.AST_CELL_RANGE:
        return ddl_generator_pb2.DDLResponse(
            type=ast_type,
            start=output["start"],
            end=output["end"],
            cells=output["cells"],
            columns=output["columns"],
            error=output.get("error", None),
            sql=sql,
        )

    if ast_type == dtypes_pb2.AstType.AST_FUNCTION:
        return ddl_generator_pb2.DDLResponse(
            type=ast_type,
            name=output["name"],
            arguments=[parse_output_to_proto(arg) for arg in output["arguments"]],
            sql=sql,
        )

    return ddl_generator_pb2.DDLResponse(
        type=ast_type,
        sql=sql,
        error=output.get("error", ""),
    )


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
            level: sql_builder_pb2.BuildSQLResponse.Sentence(expr)
            for level, expr in sql_expressions["content"].items()
        },
        error=None,
    )
