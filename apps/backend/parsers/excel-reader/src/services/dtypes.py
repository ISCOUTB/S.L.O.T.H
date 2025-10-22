from typing import Dict, Optional, TypedDict

from proto_utils.generated.parsers import dtypes_pb2
from proto_utils.parsers.dtypes import AST


class CellData(TypedDict):
    """
    TypedDict for representing cell data in an Excel sheet.

    Attributes:
        cell (str): The cell coordinate (e.g., "A1").
        value (str | float | int | None): The value of the cell, which can be a string, float, int, or None.
        data_type (str): The data type of the cell value (e.g., "s", "n", etc.).
        is_formula (bool): Indicates whether the cell contains a formula.
        ast (Optional[AST | dtypes_pb2.AST]): The Abstract Syntax Tree representation of the formula,
            if applicable. This can be either a custom AST or a protobuf AST.
        sql (Optional[str]): The SQL representation of the cell value, typically used for database operations.
    """

    cell: str
    value: str | float | int | None
    data_type: str
    is_formula: bool
    ast: Optional[AST | dtypes_pb2.AST] = None
    sql: Optional[str] = None


ColumnsInfo = Dict[str, Dict[str, str]]
DataInfo = Dict[str, Dict[str, list[CellData]]]


class SpreadsheetContent(TypedDict):
    """
    TypedDict for representing the content of a spreadsheet.

    Attributes:
        raw_data (DataInfo): The raw data extracted from the spreadsheet.
        columns (Dict[str, Dict[str, str]]): A Dictionary mapping sheet names to lists of column values.
        data (DataInfo): A Dictionary mapping sheet names to Dictionaries of cell data.
    """

    raw_data: DataInfo
    columns: ColumnsInfo
    data: DataInfo


class ParseFormulasResult(TypedDict):
    """
    TypedDict for representing the result of parsing formulas in a spreadsheet.

    Attributes:
        result (DataInfo): A Dictionary mapping sheet names to Dictionaries of cell data with parsed formulas.
        columns (ColumnsInfo): A Dictionary mapping sheet names to lists of column values.
    """

    result: DataInfo
    columns: ColumnsInfo
