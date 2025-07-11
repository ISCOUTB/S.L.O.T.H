"""
AST processing and SQL generation functions.

This module contains the core logic for processing Abstract Syntax Tree (AST) nodes
and converting them into SQL equivalents. It provides mapping functions for different
AST node types including binary expressions, functions, cell ranges, and literals.

The module defines a dispatcher pattern using the MAPS dictionary to route different
AST node types to their appropriate processing functions.
"""

from services.sql import get_sql_from_function
from services.utils import get_column_range, get_column_from_cell

from typing import Dict, Callable
from services.dtypes import (
    AST,
    AstTypes,
    CellMapsOutput,
    CellRangeMapsOutput,
    NumberMapsOutput,
    BinaryExpressionMapsOutput,
    FunctionMapsOutput,
    TextMapsOutput,
    AllOutputs
)


MAPS: Dict[AstTypes, Callable[[AST, Dict[str, str]], AllOutputs]] = {
    "binary-expression": lambda ast, columns: binary_maps(ast, columns),
    "cell-range": lambda ast, columns: cell_range_maps(ast, columns),
    "function": lambda ast, columns: function_maps(ast, columns),
    "cell": lambda ast, columns: cell_maps(ast, columns),
    "number": lambda ast, columns: number_maps(ast, columns),
    "logical": lambda ast, columns: logical_maps(ast, columns),
    "text": lambda ast, columns: text_maps(ast, columns),
    "unary-expression": lambda ast, columns: unary_maps(ast, columns),
}


def binary_maps(ast: AST, columns: Dict[str, str]) -> BinaryExpressionMapsOutput:
    """
    Process binary expression AST nodes into SQL equivalents.

    Handles mathematical and logical operations between two operands,
    recursively processing left and right sides and combining them
    with the appropriate operator.

    Args:
        ast (AST): AST node of type 'binary-expression' containing operator,
                  left operand, and right operand.
        columns (Dict[str, str]): Mapping of Excel column letters to SQL column names.

    Returns:
        BinaryExpressionMapsOutput: Processed binary expression with SQL representation.

    Raises:
        ValueError: If the AST type is not 'binary-expression'.

    Examples:
        >>> ast = {
        ...     "type": "binary-expression",
        ...     "operator": "+",
        ...     "left": {"type": "cell", "refType": "relative", "key": "A1"},
        ...     "right": {"type": "number", "value": 5}
        ... }
        >>> result = binary_maps(ast, {"A": "col1"})
        >>> result["sql"]
        '(col1) + (5)'
    """
    if ast["type"] != "binary-expression":
        raise ValueError("AST must be of type 'binary-expression'")

    left = MAPS[ast["left"]["type"]](ast["left"], columns)
    right = MAPS[ast["right"]["type"]](ast["right"], columns)

    return {
        "type": "binary-expression",
        "operator": ast["operator"],
        "left": left,
        "right": right,
        "sql": f"({left['sql']}) {ast['operator']} ({right['sql']})",
    }


def function_maps(ast: AST, columns: Dict[str, str]) -> FunctionMapsOutput:
    """
    Process function call AST nodes into SQL equivalents.

    Converts Excel functions (like SUM, IF, AND) into their SQL counterparts
    by processing function arguments and applying the appropriate SQL translation.

    Args:
        ast (AST): AST node of type 'function' containing function name and arguments.
        columns (Dict[str, str]): Mapping of Excel column letters to SQL column names.

    Returns:
        FunctionMapsOutput: Processed function with SQL representation.

    Raises:
        ValueError: If the AST type is not 'function'.

    Examples:
        >>> ast = {
        ...     "type": "function",
        ...     "name": "SUM",
        ...     "arguments": [{"type": "cell-range", ...}]
        ... }
        >>> result = function_maps(ast, {"A": "col1", "B": "col2"})
        >>> result["sql"]
        'col1 + col2'
    """
    if ast["type"] != "function":
        raise ValueError("AST must be of type 'function'")

    funtion_name = ast["name"]
    args_raw = ast.get("arguments", [])
    args = [MAPS[arg["type"]](arg, columns) for arg in args_raw]
    sql = get_sql_from_function(funtion_name, args)

    return {"type": "function", "arguments": args, "name": funtion_name, "sql": sql}


def cell_range_maps(ast: AST, columns: Dict[str, str]) -> CellRangeMapsOutput:
    """
    Process cell range AST nodes into SQL column lists.

    Converts Excel cell ranges (like A1:E1) into lists of SQL column names,
    handling both the individual cells and their corresponding column mappings.

    Args:
        ast (AST): AST node of type 'cell-range' with left and right cell boundaries.
        columns (Dict[str, str]): Mapping of Excel column letters to SQL column names.

    Returns:
        CellRangeMapsOutput: Processed cell range with column lists and error handling.

    Raises:
        ValueError: If the AST type is not 'cell-range'.

    Examples:
        >>> ast = {
        ...     "type": "cell-range",
        ...     "left": {"type": "cell", "refType": "relative", "key": "A1"},
        ...     "right": {"type": "cell", "refType": "relative", "key": "C1"}
        ... }
        >>> result = cell_range_maps(ast, {"A": "col1", "B": "col2", "C": "col3"})
        >>> result["columns"]
        ['col1', 'col2', 'col3']
    """
    if ast["type"] != "cell-range":
        raise ValueError("AST must be of type 'cell-range'")

    start_cell = cell_maps(ast["left"], columns)["cell"]
    end_cell = cell_maps(ast["right"], columns)["cell"]
    range_cell = get_column_range(
        get_column_from_cell(start_cell), get_column_from_cell(end_cell)
    )
    try:
        columns_range = [columns[col] for col in range_cell]
        error = None
    except KeyError as e:
        columns_range = []
        error = repr(e)

    return {
        "type": "cell-range",
        "start": start_cell,
        "end": end_cell,
        "cells": range_cell,
        "columns": columns_range,
        "error": error,
    }


def cell_maps(ast: AST, columns: Dict[str, str]) -> CellMapsOutput:
    """
    Process individual cell AST nodes into SQL column references.

    Converts Excel cell references (like A1, $B$2) into SQL column names,
    handling different reference types and providing error information.

    Args:
        ast (AST): AST node of type 'cell' containing cell key and reference type.
        columns (Dict[str, str]): Mapping of Excel column letters to SQL column names.

    Returns:
        CellMapsOutput: Processed cell with SQL column name and error handling.

    Raises:
        ValueError: If the AST type is not 'cell'.

    Examples:
        >>> ast = {"type": "cell", "refType": "relative", "key": "A1"}
        >>> result = cell_maps(ast, {"A": "col1"})
        >>> result["sql"]
        'col1'
    """
    if ast["type"] != "cell":
        raise ValueError("AST must be of type 'cell'")

    cell = ast["key"].replace("$", "")
    try:
        column = get_column_from_cell(cell)
        column = columns[column]
        error = None
    except KeyError as e:
        column = ""
        error = repr(e)

    return {
        "type": "cell",
        "cell": cell,
        "refType": ast.get("refType", ""),
        "column": column,
        "error": error,
        "sql": column,
    }


def number_maps(ast: AST, _) -> NumberMapsOutput:
    """
    Process numeric literal AST nodes into SQL numeric values.

    Converts numeric values from the AST into their SQL representation,
    ensuring proper type conversion and formatting.

    Args:
        ast (AST): AST node of type 'number' containing a numeric value.
        _ : Unused columns parameter (kept for consistency with other map functions).

    Returns:
        NumberMapsOutput: Processed number with SQL representation.

    Raises:
        ValueError: If the AST type is not 'number'.

    Examples:
        >>> ast = {"type": "number", "value": 42.5}
        >>> result = number_maps(ast, {})
        >>> result["sql"]
        42.5
    """
    if ast["type"] != "number":
        raise ValueError("AST must be of type 'number'")

    return {"type": "number", "value": float(ast["value"]), "sql": ast["value"]}


def logical_maps(ast: AST, _) -> CellMapsOutput:
    """
    Process logical literal AST nodes into SQL boolean values.

    Converts boolean values from the AST into their SQL representation,
    handling different input formats and ensuring proper boolean conversion.

    Args:
        ast (AST): AST node of type 'logical' containing a boolean value.
        _ : Unused columns parameter (kept for consistency with other map functions).

    Returns:
        CellMapsOutput: Processed logical value with SQL representation.

    Raises:
        ValueError: If the AST type is not 'logical'.

    Examples:
        >>> ast = {"type": "logical", "value": True}
        >>> result = logical_maps(ast, {})
        >>> result["sql"]
        'TRUE'
    """
    if ast["type"] != "logical":
        raise ValueError("AST must be of type 'logical'")

    value = (
        str(ast["value"]).lower() == "true"
    )  # Adjust depending on its received value
    return {
        "type": "logical",
        "value": value,
        "sql": str(value).upper(),
    }


def text_maps(ast: AST, _) -> TextMapsOutput:
    """
    Process text literal AST nodes into SQL string values.

    Converts string values from the AST into their SQL representation,
    ensuring proper formatting and escaping of special characters.

    Args:
        ast (AST): AST node of type 'text' containing a string value.
        _ : Unused columns parameter (kept for consistency with other map functions).

    Returns:
        TextMapsOutput: Processed text with SQL representation.

    Raises:
        ValueError: If the AST type is not 'text'.

    Examples:
        >>> ast = {"type": "text", "value": "Hello, World!"}
        >>> result = text_maps(ast, {})
        >>> result["sql"]
        "'Hello, World!'"
    """
    if ast["type"] != "text":
        raise ValueError("AST must be of type 'text'")

    return {
        "type": "text",
        "value": ast["value"],
        "sql": f"'{ast['value'].replace('"', "'")}'",  # From "" to ''
    }


def unary_maps(ast: AST, columns: Dict[str, str]) -> AllOutputs:
    """
    Process unary expression AST nodes into SQL equivalents.

    Converts unary operations (like negation) into their SQL representation,
    handling the operand and ensuring proper SQL syntax.

    Args:
        ast (AST): AST node of type 'unary-expression' containing the operand.
        columns (Dict[str, str]): Mapping of Excel column letters to SQL column names.

    Returns:
        AllOutputs: Processed unary expression with SQL representation.

    Raises:
        ValueError: If the AST type is not 'unary-expression'.

    Examples:
        >>> ast = {"type": "unary-expression", "operand": {"type": "number", "value": 5}}
        >>> result = unary_maps(ast, {})
        >>> result["sql"]
        '-(5)'
    """
    if ast["type"] != "unary-expression":
        raise ValueError("AST must be of type 'unary-expression'")

    operand = MAPS[ast["operand"]["type"]](ast["operand"], columns)

    return {
        "type": "unary-expression",
        "operator": ast["operator"],
        "operand": operand,
        "sql": f"-({operand['sql']})",
    }
