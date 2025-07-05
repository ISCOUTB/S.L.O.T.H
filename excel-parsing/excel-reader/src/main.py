import grpc
from clients.dtypes import utils
from services.get_data import get_data_from_spreadsheet
from clients.dtypes import dtypes_pb2
from clients.ddl_generator import ddl_generator_pb2, ddl_generator_pb2_grpc
from clients.formula_parser import formula_parser_pb2, formula_parser_pb2_grpc

from services import dtypes
from typing import Generator, Dict
from core.config import settings


FORMULA_PARSER_CHANNEL = grpc.insecure_channel(settings.FORMULA_PARSER_CHANNEL)
FORMULA_PARSER_STUB = formula_parser_pb2_grpc.FormulaParserStub(FORMULA_PARSER_CHANNEL)

DDL_GENERATOR_CHANNEL = grpc.insecure_channel(settings.DDL_GENERATOR_CHANNEL)
DDL_GENERATOR_STUB = ddl_generator_pb2_grpc.DDLGeneratorStub(DDL_GENERATOR_CHANNEL)


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
) -> str:
    print(ast)
    print(columns)
    request = ddl_generator_pb2.DDLRequest(ast=ast)
    request.columns.update(columns)
    response: ddl_generator_pb2.DDLResponse = stub.GenerateDDL(request)
    return response.sql


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


def parse_formulas(
    filename: str, file_bytes: bytes
) -> Dict[str, dtypes.DataInfo | dtypes.ColumnsInfo]:
    content = get_data_from_spreadsheet(filename, file_bytes)
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


def main(filename: str, file_bytes: bytes) -> dtypes.DataInfo:
    content = parse_formulas(filename, file_bytes)
    result = content["result"]
    columns = content["columns"]
    for sheet, cols in result.items():
        for col, cells in cols.items():
            for i, cell in enumerate(cells):
                result[sheet][col][i]["sql"] = generate_ddl(
                    DDL_GENERATOR_STUB, cell["ast"], columns[sheet]
                )
                result[sheet][col][i]["ast"] = utils.parse_ast(cell["ast"])

    return result


if __name__ == "__main__":
    import json
    import os.path

    file_example = "../../typechecking/backend/static/acme__users__sample1.xlsx"

    with open(file_example, "rb") as file:
        file_bytes = file.read()

    filename = os.path.basename(file_example)
    result = main(filename, file_bytes)
    print(json.dumps(result, indent=4, ensure_ascii=False))
