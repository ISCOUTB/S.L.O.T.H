"""Parser data types module.

This module contains TypedDict definitions and type aliases for Excel formula parsing,
Abstract Syntax Tree (AST) representation, DDL generation, and SQL building operations.
These types correspond to the Protocol Buffer message definitions for the parsers package.
"""

from typing import Any, TypedDict, Dict, Literal, Optional, List, Union


AstType = Literal[
    "unknown",
    "binary-expression",
    "cell-range",
    "cell",
    "function",
    "number",
    "logical",
    "text",
    "unary-expression",
    "reference-node",
]
"""Type alias for supported AST node types in Excel formula parsing.

Supported types:
    - unknown: Unknown or unrecognized node type
    - binary-expression: Binary operations like +, -, *, /
    - cell-range: Cell ranges like A1:B5
    - cell: Individual cell references like A1
    - function: Function calls like SUM(), AVERAGE()
    - number: Literal numeric values
    - logical: Boolean values (TRUE/FALSE)
    - text: Literal text strings
    - unary-expression: Unary operations like -1 (negation)
"""

RefType = Literal["unknown", "relative", "absolute", "mixed"]
"""Type alias for Excel cell reference types.

Supported types:
    - unknown: Unknown or unrecognized reference type
    - relative: Relative references like A1 (adjust when copied)
    - absolute: Absolute references like $A$1 (fixed when copied)
    - mixed: Mixed references like $A1 or A$1 (partially fixed)
"""


class AST(TypedDict):
    """Abstract Syntax Tree node for Excel formula expressions.

    Represents the hierarchical structure of a parsed Excel formula.
    Each node can represent different types of expressions including
    binary operations, function calls, cell references, and literal values.

    Attributes:
        type: The type of AST node indicating its structure and purpose
        operator: The operator for binary expressions (e.g., "+", "-", "*", "/")
        left: Left operand for binary expressions or first argument for functions
        right: Right operand for binary expressions or additional arguments
        arguments: List of AST nodes representing function arguments
        name: Function name identifier (e.g., "SUM", "AVERAGE", "COUNT")
        refType: Type of cell reference (relative, absolute, mixed)
        key: Specific cell reference key (e.g., "A1", "B2", "C3:D5")
        value: Literal value for number, text, or boolean nodes
        operand: Operand for unary expressions
    """

    type: AstType
    operator: Optional[str]
    left: Optional["AST"]
    right: Optional["AST"]
    arguments: Optional[list["AST"]]
    name: Optional[str]
    refType: Optional[RefType]
    key: Optional[str]
    value: Optional[float | str | bool]
    operand: Optional["AST"]
    sheet_name: Optional[str]


# ===================== Related to AST =====================


class NumberAST(TypedDict):
    """
    Represents a number AST node.

    Attributes:
        type (Literal["number"]): The type of the AST node, always "number".
        value (float): The numeric value represented by the AST node.
        sql (str): The string representation of the number, e.g., "42".
    """

    type: Literal["number"]
    value: float
    sql: str


class LogicalAST(TypedDict):
    """
    Represents a logical AST node.

    Attributes:
        type (Literal["logical"]): The type of the AST node, always "logical".
        value (bool): The boolean value represented by the AST node.
        sql (str): The string representation of the logical value, e.g., "true" or "false".
    """

    type: Literal["logical"]
    value: bool
    sql: str


class CellAST(TypedDict):
    """
    Represents a cell reference AST node.

    Attributes:
        type (Literal["cell"]): The type of the AST node, always "cell".
        cell (str): The cell reference (e.g., "A1").
        refType (RefType): The type of cell reference ("relative", "absolute" and "mixed").
        column (str): The column name corresponding to the cell reference (e.g., "A").
        error (Optional[str]): An error message if there was an issue with the cell reference,
            otherwise None.
        sql (str): The SQL representation of the cell reference, typically the column name.
    """

    type: Literal["cell"]
    cell: str
    refType: RefType
    column: str
    error: Optional[str]
    sql: str


class CellRangeAST(TypedDict):
    """
    Represents a cell range AST node.

    Attributes:
        type (Literal["cell-range"]): The type of the AST node, always "cell-range".
        start (str): The starting cell reference of the range (e.g., "A1").
        end (str): The ending cell reference of the range (e.g., "B2").
        cells (list[str]): A list of cell references in the range (e.g., ["A1", "A2", ...]).
        columns (list[str]): A list of column names corresponding to the cells in the range.
        error (Optional[str]): An error message if there was an issue with the range,
            otherwise None.
    """

    type: Literal["cell-range"]
    start: str
    end: str
    cells: list[str]
    columns: list[str]
    error: Optional[str]


class BinaryExpressionAST(TypedDict):
    """
    Represents a binary expression AST node.

    Attributes:
        type (Literal["binary-expression"]): The type of the AST node, always "binary-expression".
        operator (str): The operator used in the binary expression (e.g., "+", "-", "*", "/").
        left (Any): The left operand of the binary expression.
        right (Any): The right operand of the binary expression.
        sql (str): The SQL representation of the binary expression, combining the left and right
            operands with the operator.
    """

    type: Literal["binary-expression"]
    operator: str
    left: Any
    right: Any
    sql: str


class FunctionAST(TypedDict):
    """
    Represents a function call AST node.

    Attributes:
        type (Literal["function"]): The type of the AST node, always "function".
        name (str): The name of the function being called (e.g., "SUM", "IF").
        arguments (list[Any]): A list of AST nodes representing the arguments passed to the function.
        sql (str): The SQL representation of the function call, including its name and arguments.
    """

    type: Literal["function"]
    name: str
    arguments: list[Any]
    sql: str


class TextAST(TypedDict):
    """
    Represents a text literal AST node.

    Attributes:
        type (Literal["text"]): The type of the AST node, always "text".
        value (str): The text value represented by the AST node.
        sql (str): The SQL representation of the text value, typically enclosed in quotes.
    """

    type: Literal["text"]
    value: str
    sql: str


class ReferenceAST(TypedDict):
    type: Literal["reference-node"]
    sheetName: str
    key: str
    refType: Optional[RefType]
    error: Optional[str]
    sql: str


class ColReferences(TypedDict):
    """
    Represents a collection of column references.

    Attributes:
        columns (list[str]): A list of column names that are referenced.
        error (Optional[str]): An error message if there was an issue with the references,
            otherwise None.
        constants (bool): Indicates if the references are constants
    """

    columns: list[str]
    error: Optional[str]
    constants: bool


class UnaryExpressionAST(TypedDict):
    """
    Represents a unary expression AST node.

    Attributes:
        type (Literal["unary-expression"]): The type of the AST node, always "unary-expression".
        operator (str): The operator used in the unary expression (e.g., "-").
        operand (Any): The operand of the unary expression.
        sql (str): The SQL representation of the unary expression, typically applying the operator
            to the operand.
    """

    type: Literal["unary-expression"]
    operator: str
    operand: Any
    sql: str


AllASTs = Union[
    CellAST,
    CellRangeAST,
    NumberAST,
    BinaryExpressionAST,
    FunctionAST,
    LogicalAST,
    TextAST,
    UnaryExpressionAST,
    ReferenceAST,
]
"""Union type representing all possible AST node types."""

SingleASTs = Union[
    CellAST,
    NumberAST,
    LogicalAST,
    TextAST,
]
"""Union type for simple, single-value AST nodes (cells, numbers, logical values and text)."""

ConstantsASTs = Union[TextAST, NumberAST, LogicalAST]
"""Union type representing AST nodes that are constant values."""

ComplexASTs = Union[
    FunctionAST,
    BinaryExpressionAST,
    UnaryExpressionAST,
]
"""Union type for complex AST nodes that contain nested structures (functions, expressions)."""


# ===================== Formula Parser =====================


class Token(TypedDict):
    """Individual token in an Excel formula.

    Represents a single element of a parsed formula such as
    numbers, operators, functions, and cell references.

    Attributes:
        value: Token value (e.g., "SUM", "+", "A1", "123")
        type: Token type (e.g., "function", "operator", "operand")
        subtype: Token subtype (e.g., "math", "logical", "reference")
    """

    value: str
    type: str
    subtype: str


class Tokens(TypedDict):
    """Collection of tokens generated during Excel formula parsing.

    Contains the ordered list of tokens that make up a parsed formula.

    Attributes:
        tokens: Ordered list of Token objects representing the formula elements
    """

    tokens: list[Token]


class FormulaParserRequest(TypedDict):
    """Request message for Excel formula parsing operations.

    Contains the Excel formula string to be parsed into tokens and AST.

    Attributes:
        formula: The Excel formula to parse (e.g., "=SUM(A1:A5)", "=IF(B1>0,B1*2,0)")
    """

    formula: str


class FormulaParserResponse(TypedDict):
    """Response message containing Excel formula parsing results.

    Provides the original formula, generated tokens, AST, and error information.

    Attributes:
        formula: The original Excel formula that was parsed
        tokens: Tokens generated during the parsing process (optional)
        ast: The resulting Abstract Syntax Tree structure (optional)
        error: Error message if there was a problem during parsing
    """

    formula: str
    tokens: Optional[Tokens]
    ast: Optional[AST]
    error: str


# ===================== DDL Generator =====================


class DDLRequest(TypedDict):
    """Request message for DDL generation from Excel formula AST.

    Contains the parsed Excel formula AST and column mapping information
    needed to generate SQL DDL statements.

    Attributes:
        ast: The Abstract Syntax Tree representing the parsed Excel formula
        columns: Mapping of Excel column letters to database column names
    """

    ast: AST
    columns: Dict[str, str]


class DDLResponse(TypedDict):
    """Response message containing generated DDL and associated metadata.

    Provides comprehensive information about the generated SQL DDL
    including literal values, cell references, ranges, and expressions.

    Attributes:
        type: Type of the AST node this response represents
        sql: Generated SQL statement or expression
        value: Literal value for number, text, or boolean nodes (optional)
        cell: Original cell reference (e.g., "A1", "$B$2") (optional)
        refType: Type of cell reference (relative, absolute, mixed) (optional)
        column: Mapped database column name for this cell (optional)
        error_cell: Error message if cell reference is invalid (optional)
        start: Starting cell of a range (e.g., "A1") (optional)
        end: Ending cell of a range (e.g., "B5") (optional)
        cells: List of all individual cells in the range
        columns: List of all database columns affected by this range
        error_cell_range: Error message if range is invalid (optional)
        operator: The binary operator for binary expressions (optional)
        left: Left operand of binary expressions (optional)
        right: Right operand of binary expressions (optional)
        name: Function name for function calls (optional)
        arguments: List of function arguments as DDLResponse objects
        operand: Operand for unary expressions (optional)
    """

    type: AstType
    sql: str
    value: Optional[float | str | bool]

    # Cell Reference Information
    cell: Optional[str]
    refType: Optional[RefType]
    column: Optional[str]
    error_cell: Optional[str]

    # Cell Range Information
    start: Optional[str]
    end: Optional[str]
    cells: List[str]
    columns: List[str]
    error_cell_range: Optional[str]

    # Binary Expression Information
    operator: Optional[str]
    left: Optional["DDLResponse"]
    right: Optional["DDLResponse"]

    # Function Information
    name: Optional[str]
    arguments: List["DDLResponse"]

    # Unary Expression Information
    operand: Optional["DDLResponse"]


# ===================== SQL Builder =====================


class SQLRequestColumnInfo(TypedDict):
    """Column information for SQL building operations.

    Contains data type and constraint information for database columns.

    Attributes:
        type: Data type of the column (e.g., "INTEGER", "VARCHAR(255)")
        extra: Additional SQL constraints (e.g., "NOT NULL", "PRIMARY KEY")
    """

    type: str
    extra: str


class BuildSQLRequest(TypedDict):
    """Request message for SQL building operations.

    Contains all necessary information to construct SQL statements
    from processed Excel formula data.

    Attributes:
        cols: Map of column names to their DDL responses from formula processing
        dtypes: Map of column names to their data type information
        table_name: Name of the target database table
    """

    cols: Dict[str, DDLResponse]
    dtypes: Dict[str, SQLRequestColumnInfo]
    table_name: str


class SQLResponseSQLContent(TypedDict):
    """SQL content containing a statement and its affected columns.

    Represents a single SQL operation with its metadata.

    Attributes:
        sql: The complete SQL statement (e.g., CREATE TABLE, INSERT, SELECT)
        columns: List of column names involved in this SQL statement
    """

    sql: str
    columns: List[str]


class BuildSQLResponseContent(TypedDict):
    """Content container for grouping related SQL statements.

    Allows for organizing multiple related SQL operations together.

    Attributes:
        sql_content: List of SQL statements that belong together logically
    """

    sql_content: List[SQLResponseSQLContent]


class BuildSQLResponse(TypedDict):
    """Response message containing the constructed SQL statements.

    Provides organized SQL content and any error information.

    Attributes:
        content: Map of operation IDs to their SQL content groups
        error: Error message if there was a problem building the SQL (optional)
    """

    content: Dict[str, BuildSQLResponseContent]
    error: Optional[str]
