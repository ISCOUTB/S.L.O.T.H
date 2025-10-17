"""
Type definitions for Excel formula AST processing and SQL generation.

This module defines all the TypedDict classes and type aliases used throughout
the DDL generator. It provides comprehensive type definitions for AST nodes,
input data structures, and output mappings to ensure type safety and clear
interfaces between components.

The types are organized into:
- Basic type aliases for AST and reference types
- Input data structures
- Output type definitions for different AST node processing results
- Union types for flexible type handling
"""

from typing import Any, Literal, Optional, TypedDict, Union

from proto_utils.parsers.dtypes import RefType


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
    refType: RefType
    column: str
    error: Optional[str]
    sql: str


class CellRangeMapsOutput(TypedDict):
    """
    Represents the output of cell range mapping.

    Attributes:
        type (Literal["cell-range"]): The type of the mapping, always "cell-range".
        start (str): The starting cell reference of the range (e.g., "A1").
        end (str): The ending cell reference of the range (e.g., "B2").
        cells (list[str]): A list of cell references in the range (e.g., ["A1", "A2", ...]).
        columns (list[str]): A list of column names corresponding to the cells in the range.
        error (Optional[str]): An error message if there was an issue with the mapping,
            otherwise None.
    """

    type: Literal["cell-range"]
    start: str
    end: str
    cells: list[str]
    columns: list[str]
    error: Optional[str]


class BinaryExpressionMapsOutput(TypedDict):
    """
    Represents the output of binary expression mapping.

    Attributes:
        type (Literal["binary-expression"]): The type of the mapping, always "binary-expression".
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


AllOutputs = Union[
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

SingleOutput = Union[
    CellMapsOutput,
    NumberMapsOutput,
    LogicalMapsOutput,
    TextMapsOutput,
]
"""Union type for simple, single-value outputs (cells, numbers, logical values and text)."""

ComplexOutput = Union[
    FunctionMapsOutput,
    BinaryExpressionMapsOutput,
    UnaryExpressionMapsOutput,
]
"""Union type for complex outputs that contain nested structures (functions, expressions)."""
