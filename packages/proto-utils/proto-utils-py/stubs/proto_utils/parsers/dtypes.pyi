from _typeshed import Incomplete
from typing import Any, Literal, TypedDict

AstType: Incomplete
RefType: Incomplete

class AST(TypedDict):
    type: AstType
    operator: str | None
    left: AST | None
    right: AST | None
    arguments: list['AST'] | None
    name: str | None
    refType: RefType | None
    key: str | None
    value: float | str | bool | None
    operand: AST | None

class NumberAST(TypedDict):
    type: Literal['number']
    value: float
    sql: str

class LogicalAST(TypedDict):
    type: Literal['logical']
    value: bool
    sql: str

class CellAST(TypedDict):
    type: Literal['cell']
    cell: str
    refType: RefType
    column: str
    error: str | None
    sql: str

class CellRangeAST(TypedDict):
    type: Literal['cell-range']
    start: str
    end: str
    cells: list[str]
    columns: list[str]
    error: str | None

class BinaryExpressionAST(TypedDict):
    type: Literal['binary-expression']
    operator: str
    left: Any
    right: Any
    sql: str

class FunctionAST(TypedDict):
    type: Literal['function']
    name: str
    arguments: list[Any]
    sql: str

class TextAST(TypedDict):
    type: Literal['text']
    value: str
    sql: str

class ColReferences(TypedDict):
    columns: list[str]
    error: str | None
    constants: bool

class UnaryExpressionAST(TypedDict):
    type: Literal['unary-expression']
    operator: str
    operand: Any
    sql: str
AllASTs = CellAST | CellRangeAST | NumberAST | BinaryExpressionAST | FunctionAST | LogicalAST | TextAST | UnaryExpressionAST
SingleASTs = CellAST | NumberAST | LogicalAST | TextAST
ConstantsASTs = TextAST | NumberAST | LogicalAST
ComplexASTs = FunctionAST | BinaryExpressionAST | UnaryExpressionAST

class Token(TypedDict):
    value: str
    type: str
    subtype: str

class Tokens(TypedDict):
    tokens: list[Token]

class FormulaParserRequest(TypedDict):
    formula: str

class FormulaParserResponse(TypedDict):
    formula: str
    tokens: Tokens | None
    ast: AST | None
    error: str

class DDLRequest(TypedDict):
    ast: AST
    columns: dict[str, str]

class DDLResponse(TypedDict):
    type: AstType
    sql: str
    value: float | str | bool | None
    cell: str | None
    refType: RefType | None
    column: str | None
    error_cell: str | None
    start: str | None
    end: str | None
    cells: list[str]
    columns: list[str]
    error_cell_range: str | None
    operator: str | None
    left: DDLResponse | None
    right: DDLResponse | None
    name: str | None
    arguments: list['DDLResponse']
    operand: DDLResponse | None

class SQLRequestColumnInfo(TypedDict):
    type: str
    extra: str

class BuildSQLRequest(TypedDict):
    cols: dict[str, DDLResponse]
    dtypes: dict[str, SQLRequestColumnInfo]
    table_name: str

class SQLResponseSQLContent(TypedDict):
    sql: str
    columns: list[str]

class BuildSQLResponseContent(TypedDict):
    sql_content: list[SQLResponseSQLContent]

class BuildSQLResponse(TypedDict):
    content: dict[str, BuildSQLResponseContent]
    error: str | None
