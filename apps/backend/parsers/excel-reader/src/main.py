from typing import Dict, Generator

from proto_utils.generated.parsers import (
    ddl_generator_pb2,
    ddl_generator_pb2_grpc,
    dtypes_pb2,
    formula_parser_pb2,
    formula_parser_pb2_grpc,
    sql_builder_pb2,
    sql_builder_pb2_grpc,
)
from proto_utils.parsers import (
    DTypesSerde,
    SQLBuilderSerde,
)

from src.services import dtypes
from src.services.get_data import get_data_from_spreadsheet
from src.services.utils import monitor_performance


def parse_formula(
    stub: formula_parser_pb2_grpc.FormulaParserStub, formula: str
) -> dtypes_pb2.AST:
    request = formula_parser_pb2.FormulaParserRequest(formula=formula)
    response: formula_parser_pb2.FormulaParserResponse = stub.ParseFormula(
        request
    )
    return response.ast


def generate_ddl(
    stub: ddl_generator_pb2_grpc.DDLGeneratorStub,
    ast: dtypes_pb2.AST,
    columns: Dict[str, str],
    raw: bool = False,
) -> ddl_generator_pb2.DDLResponse | str:
    request = ddl_generator_pb2.DDLRequest(ast=ast, columns=columns)
    response: ddl_generator_pb2.DDLResponse = stub.GenerateDDL(request)
    return response if raw else response.sql


@monitor_performance("generate_sql")
def generate_sql(
    stub: sql_builder_pb2_grpc.SQLBuilderStub,
    cols: Dict[str, ddl_generator_pb2.DDLResponse],
    dtypes: Dict[str, Dict[str, str]],
    table_name: str,
) -> str:
    request = sql_builder_pb2.BuildSQLRequest(
        cols=cols,
        dtypes={
            dtype: sql_builder_pb2.BuildSQLRequest.ColumnInfo(
                type=dtypes[dtype]["type"], extra=dtypes[dtype].get("extra", "")
            )
            for dtype in dtypes
        },
        table_name=table_name,
    )
    response: sql_builder_pb2.BuildSQLResponse = stub.BuildSQL(request)
    sql_expressions = SQLBuilderSerde.deserialize_build_sql_response(response)[
        "content"
    ]
    sql_expression = ""
    for level in sorted(sql_expressions.keys()):
        for content in sql_expressions[level]:
            prefix = "" if level == 0 else "\n"
            sql_expression += f"{prefix}{content['sql']}"

    return sql_expression


def generate_data(
    data: dtypes.DataInfo,
) -> Generator[Dict[str, str | dtypes.CellData], None, None]:
    for sheet, cols in data.items():
        for col, cells in cols.items():
            for i, cell in enumerate(cells[:1]):
                yield {
                    "sheet": sheet,
                    "col": col,
                    "cell": cell,
                    "index": i,
                }


@monitor_performance("parse_formulas")
def parse_formulas(
    *,
    formula_parser_stub: formula_parser_pb2_grpc.FormulaParserStub,
    filename: str,
    file_bytes: bytes,
    limit: int = 50,
    fill_spaces: str = "_",
) -> dtypes.ParseFormulasResult:
    content = get_data_from_spreadsheet(
        filename,
        file_bytes,
        limit=limit,
        fill_spaces=fill_spaces,
    )
    data = content["data"]
    result = {}
    for cell_data in generate_data(data):
        sheet = cell_data["sheet"]
        col = cell_data["col"]
        cell = cell_data["cell"]
        if cell["data_type"] == "s":
            cell["value"] = f'"{cell["value"]}"'

        if sheet not in result:
            result[sheet] = {}
        if col not in result[sheet]:
            result[sheet][col] = []

        cell["ast"] = parse_formula(formula_parser_stub, str(cell["value"]))
        result[sheet][col].append(cell)

    return dtypes.ParseFormulasResult(result=result, columns=content["columns"])


@monitor_performance("main")
def main(
    *,
    formula_parser_stub: formula_parser_pb2_grpc.FormulaParserStub,
    ddl_generator_stub: ddl_generator_pb2_grpc.DDLGeneratorStub,
    filename: str,
    file_bytes: bytes,
    limit: int = 50,
    fill_spaces: str = " ",
) -> dtypes.ParseFormulasResult:
    content = parse_formulas(
        filename=filename,
        file_bytes=file_bytes,
        limit=limit,
        fill_spaces=fill_spaces,
        formula_parser_stub=formula_parser_stub,
    )

    result = content["result"]
    columns = content["columns"]
    for sheet, cols in result.items():
        for col, cells in cols.items():
            for i, cell in enumerate(cells):
                result[sheet][col][i]["sql"] = generate_ddl(
                    ddl_generator_stub,
                    cell["ast"],
                    columns[sheet],
                    raw=True,
                )
                result[sheet][col][i]["ast"] = DTypesSerde.deserialize_ast(
                    cell["ast"]
                )

    return dtypes.ParseFormulasResult(result=result, columns=columns)
