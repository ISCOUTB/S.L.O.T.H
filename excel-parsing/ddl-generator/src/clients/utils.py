from services import dtypes
from typing import Dict, Callable, Literal
from clients import dtypes_pb2, ddl_generator_pb2


MAPS: Dict[dtypes.AstTypes, Callable[[dtypes_pb2.AST], dtypes.AST]] = {
    "binary-expression": lambda ast: parse_binary(ast),
    "cell-range": lambda ast: parse_cell_range(ast),
    "function": lambda ast: parse_function(ast),
    "cell": lambda ast: parse_cell(ast),
    "number": lambda ast: parse_number(ast),
    "logical": lambda ast: parse_logical(ast),
    "text": lambda ast: parse_text(ast),
}


AST_TYPES_MAPPING: Dict[dtypes_pb2.AstType, dtypes.AstTypes] = {
    dtypes_pb2.AstType.AST_BINARY_EXPRESSION: "binary-expression",
    dtypes_pb2.AstType.AST_CELL_RANGE: "cell-range",
    dtypes_pb2.AstType.AST_FUNCTION: "function",
    dtypes_pb2.AstType.AST_CELL: "cell",
    dtypes_pb2.AstType.AST_NUMBER: "number",
    dtypes_pb2.AstType.AST_LOGICAL: "logical",
    dtypes_pb2.AstType.AST_TEXT: "text",
}

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


def parse_ast(ast: dtypes_pb2.AST) -> dtypes.AST:
    ast_type = parse_ast_type(ast.type)
    if ast_type == "unknown":
        raise ValueError(f"Unknown AST type: {ast.type}")

    return MAPS[ast_type](ast)


def parse_ast_type(
    ast_type: dtypes_pb2.AstType,
) -> dtypes.AstTypes | Literal["unknown"]:
    return AST_TYPES_MAPPING.get(ast_type, "unknown")


def parse_ref_type(
    ref_type: dtypes_pb2.RefType,
) -> dtypes.RefTypes | Literal[""]:
    ref_types_mapping = {
        dtypes_pb2.RefType.REF_RELATIVE: "relative",
        dtypes_pb2.RefType.REF_ABSOLUTE: "absolute",
        dtypes_pb2.RefType.REF_MIXED: "mixed",
    }

    return ref_types_mapping.get(ref_type, "")


def parse_binary(ast: dtypes_pb2.AST) -> dtypes.AST:
    return dtypes.AST(
        type="binary-expression",
        operator=ast.operator,
        left=parse_ast(ast.left),
        right=parse_ast(ast.right),
    )


def parse_cell_range(ast: dtypes_pb2.AST) -> dtypes.AST:
    return dtypes.AST(
        type="cell-range",
        left=parse_ast(ast.left),  # parse_cell
        right=parse_ast(ast.right),  # parse_cell
    )


def parse_function(ast: dtypes_pb2.AST) -> dtypes.AST:
    return dtypes.AST(
        type="function",
        name=ast.name,
        arguments=[parse_ast(arg) for arg in ast.arguments],
    )


def parse_cell(ast: dtypes_pb2.AST) -> dtypes.AST:
    reftype = parse_ref_type(ast.refType)
    extra = {"refType": ast.refType} if reftype == "" else {}
    return dtypes.AST(type="cell", key=ast.key, **extra)


def parse_number(ast: dtypes_pb2.AST) -> dtypes.AST:
    return dtypes.AST(
        type="number",
        value=ast.number_value,
    )


def parse_logical(ast: dtypes_pb2.AST) -> dtypes.AST:
    return dtypes.AST(
        type="logical",
        value=ast.logical_value,
    )


def parse_text(ast: dtypes_pb2.AST) -> dtypes.AST:
    return dtypes.AST(
        type="text",
        value=ast.text_value,
    )


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
