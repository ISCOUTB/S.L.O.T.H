import grpc
from clients.dtypes import utils
from services.get_data import get_data_from_spreadsheet
from services.utils import monitor_performance 

from clients.dtypes import dtypes_pb2
from clients.ddl_generator import ddl_generator_pb2, ddl_generator_pb2_grpc
from clients.formula_parser import formula_parser_pb2, formula_parser_pb2_grpc

from clients.sql_builder import utils as sql_builder_utils
from clients.sql_builder import sql_builder_pb2, sql_builder_pb2_grpc

from services import dtypes
from typing import Generator, Dict
from core.config import settings
from utils import logger


FORMULA_PARSER_CHANNEL = grpc.insecure_channel(settings.FORMULA_PARSER_CHANNEL)
FORMULA_PARSER_STUB = formula_parser_pb2_grpc.FormulaParserStub(FORMULA_PARSER_CHANNEL)

DDL_GENERATOR_CHANNEL = grpc.insecure_channel(settings.DDL_GENERATOR_CHANNEL)
DDL_GENERATOR_STUB = ddl_generator_pb2_grpc.DDLGeneratorStub(DDL_GENERATOR_CHANNEL)

SQL_BUILDER_CHANNEL = grpc.insecure_channel(settings.SQL_BUILDER_CHANNEL)
SQL_BUILDER_STUB = sql_builder_pb2_grpc.SQLBuilderStub(SQL_BUILDER_CHANNEL)


def parse_formula(
    stub: formula_parser_pb2_grpc.FormulaParserStub, formula: str
) -> Dict:
    request = formula_parser_pb2.FormulaParserRequest(formula=formula)
    response: formula_parser_pb2.FormulaParserResponse = stub.ParseFormula(request)
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
    sql_expressions = sql_builder_utils.parse_sql_builder_response(response)["content"]
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
    filename: str, file_bytes: bytes, limit: int = 50, fill_spaces: str = "_"
) -> Dict[str, dtypes.DataInfo | dtypes.ColumnsInfo]:
    content = get_data_from_spreadsheet(
        filename, file_bytes, limit=limit, fill_spaces=fill_spaces
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

        cell["ast"] = parse_formula(FORMULA_PARSER_STUB, str(cell["value"]))
        result[sheet][col].append(cell)

    return {"result": result, "columns": content["columns"]}


@monitor_performance("main")
def main(
    filename: str, file_bytes: bytes, limit: int = 50, fill_spaces: str = " "
) -> Dict[str, dtypes.DataInfo | dtypes.ColumnsInfo]:
    content = parse_formulas(filename, file_bytes, limit, fill_spaces=fill_spaces)
    result = content["result"]
    columns = content["columns"]

    result = content["result"]
    columns = content["columns"]
    for sheet, cols in result.items():
        for col, cells in cols.items():
            for i, cell in enumerate(cells):
                result[sheet][col][i]["sql"] = generate_ddl(
                    DDL_GENERATOR_STUB, cell["ast"], columns[sheet], raw=True
                )
                result[sheet][col][i]["ast"] = utils.parse_ast(cell["ast"])

    return {"result": result, "columns": columns}


if __name__ == "__main__":
    pass
