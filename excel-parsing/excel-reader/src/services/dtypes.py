from clients.dtypes import dtypes_pb2
from typing import TypedDict, Literal, Optional, Union, Any, Dict


AstTypes = Literal[
    "binary-expression",  # e.g., "a + b"
    "cell-range",  # e.g., "A1:B2"
    "function",  # e.g., "SUM(A1:B2)"
    "cell",  # e.g., "A1"
    "number",  # e.g., 42
    "logical",  # e.g., true
    "text",  # e.g., "Hello, World!"
    "unary-expression",  # e.g., "-a" or "NOT a"
]

RefTypes = Literal[
    "relative",  # Obtained from a cell reference like "A1" or "B2"
    "absolute",  # Obtained from a cell reference like "$A$1" or "$B$2"
    "mixed",  # Obtained from a cell reference like "A$1" or "$B2"
    "",  # Empty string for cases where the reference type is not applicable
]


class AST(TypedDict):
    """
    Represents an Abstract Syntax Tree (AST) node.
    Each node can represent a binary expression, a cell range,
    a function call, or a single cell reference in spreadsheet formulas.

    Attributes:
        type (AstTypes): The type of the AST node indicating its structure and purpose.
        operator (Optional[str]): The operator for binary expressions such as "+", "-", "*", "/".
            Only used when type indicates a binary expression.
        left (Optional["AST"]): The left operand for binary expressions, the range start for
            cell ranges, or the first argument for functions. Used for binary expressions,
            functions, and cell ranges.
        right (Optional["AST"]): The right operand for binary expressions, the range end for
            cell ranges, or additional arguments for functions. Used for binary expressions,
            functions, and cell ranges.
        arguments (Optional[list["AST"]]): A list of AST nodes representing the arguments
            passed to function calls. Only used when type indicates a function.
        name (Optional[str]): The name identifier of the function being called, such as
            "SUM", "AVERAGE", "COUNT". Only used for function type nodes.
        refType (Optional[str]): The type of cell reference indicating the range format,
            such as "A1:B2" for ranges or "A1" for single cells. Only used for cell
            reference type nodes.
        key (Optional[str]): The specific cell reference key, such as "A1", "B2", or
            "C3:D5". Only used for cell reference type nodes.
        value (Optional[float | str | bool]): The numeric value for nodes representing numbers. Only used
            for number type nodes.
        operand (Optional[str]): The operator for unary expressions, such as "-" for negation.
    """

    type: AstTypes
    operator: Optional[str]
    left: Optional["AST"]
    right: Optional["AST"]
    arguments: Optional[list["AST"]]
    name: Optional[str]
    refType: Optional[RefTypes]
    key: Optional[str]
    value: Optional[float | str | bool]
    operand: Optional[str]


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


class NumberMapsOutput(TypedDict):
    """
    Represents the output of number mapping.

    Attributes:
        type (Literal["number"]): The type of the mapping, always "number".
        value (float): The numeric value represented by the AST node.
        sql (str): The string representation of the number, e.g., "42".
    """

    type: Literal["number"]
    value: float
    sql: str


class LogicalMapsOutput(TypedDict):
    """
    Represents the output of logical mapping.

    Attributes:
        type (Literal["logical"]): The type of the mapping, always "logical".
        value (bool): The boolean value represented by the AST node.
        sql (str): The string representation of the logical value, e.g., "true" or "false".
    """

    type: Literal["logical"]
    value: bool
    sql: str


class CellMapsOutput(TypedDict):
    """
    Represents the output of cell mapping.

    Attributes:
        type (Literal["cell"]): The type of the mapping, always "cell".
        cell (str): The cell reference (e.g., "A1").
        refType (Reftypes): The type of cell reference ("relative", "absolute" and "mixed").
        column (str): The column name corresponding to the cell reference (e.g., "A").
        error (Optional[str]): An error message if there was an issue with the mapping,
            otherwise None.
        sql (str): The SQL representation of the cell reference, typically the column name.
    """

    type: Literal["cell"]
    cell: str
    refType: RefTypes
    column: str
    error: Optional[str]
    sql: str


class CellRangeMapsOutput(TypedDict):
    """
    Represents the output of cell range mapping.

    Attributes:
        type (Literal["cell_range"]): The type of the mapping, always "cell_range".
        start (str): The starting cell reference of the range (e.g., "A1").
        end (str): The ending cell reference of the range (e.g., "B2").
        cells (list[str]): A list of cell references in the range (e.g., ["A1", "A2", ...]).
        columns (list[str]): A list of column names corresponding to the cells in the range.
        error (Optional[str]): An error message if there was an issue with the mapping,
            otherwise None.
    """

    type: Literal["cell_range"]
    start: str
    end: str
    cells: list[str]
    columns: list[str]
    error: Optional[str]


class BinaryExpressionMapsOutput(TypedDict):
    """
    Represents the output of binary expression mapping.

    Attributes:
        type (Literal["binary_expression"]): The type of the mapping, always "binary_expression".
        operator (str): The operator used in the binary expression (e.g., "+", "-", "*", "/").
        left (Any): The left operand of the binary expression.
        right (Any): The right operand of the binary expression.
        sql (str): The SQL representation of the binary expression, combining the left and right
            operands with the operator.
    """

    type: Literal["binary_expression"]
    operator: str
    left: Any
    right: Any
    sql: str


class FunctionMapsOutput(TypedDict):
    """
    Represents the output of function mapping.

    Attributes:
        type (Literal["function"]): The type of the mapping, always "function".
        name (str): The name of the function being called (e.g., "SUM", "IF").
        arguments (list[Any]): A list of AST nodes representing the arguments passed to the function.
        sql (str): The SQL representation of the function call, including its name and arguments.
    """

    type: Literal["function"]
    name: str
    arguments: list[Any]
    sql: str


class TextMapsOutput(TypedDict):
    """
    Represents the output of text mapping.

    Attributes:
        type (Literal["text"]): The type of the mapping, always "text".
        value (str): The text value represented by the AST node.
        sql (str): The SQL representation of the text value, typically enclosed in quotes.
    """

    type: Literal["text"]
    value: str
    sql: str


class UnaryExpressionMapsOutput(TypedDict):
    """
    Represents the output of unary expression mapping.

    Attributes:
        type (Literal["unary-expression"]): The type of the mapping, always "unary-expression".
        operator (str): The operator used in the unary expression (e.g., "-").
        operand (Any): The operand of the unary expression.
        sql (str): The SQL representation of the unary expression, typically applying the operator
            to the left operand.
    """

    type: Literal["unary-expression"]
    operator: str
    operand: Any
    sql: str


DDLResponse = Union[
    CellMapsOutput,
    CellRangeMapsOutput,
    NumberMapsOutput,
    BinaryExpressionMapsOutput,
    FunctionMapsOutput,
    LogicalMapsOutput,
    TextMapsOutput,
    UnaryExpressionMapsOutput,
]
"""Union type representing all possible output types from AST processing functions."""


class SQLExpressions(TypedDict):
    """
    SQl expressions for creating and altering tables.

    Attributes:
        content (Optional[Dict[int, list[str]]]): A dictionary mapping levels to SQL expressions.
            The keys are integers representing the level of the expression, and the values
            are strings containing the SQL expression for that level.
        error (Optional[str]): An error message if there was an issue generating the SQL expressions,
            otherwise None.
    """

    content: Optional[Dict[int, list[str]]] = {}
    error: Optional[str] = None
