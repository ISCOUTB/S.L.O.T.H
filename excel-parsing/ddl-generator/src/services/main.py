"""
Main entry point for the DDL generator.

This module serves as the primary interface for converting Excel formula ASTs
into SQL expressions. It processes input data containing ASTs and column mappings
to generate corresponding SQL output.
"""

from services.generator import MAPS

from typing import Dict
from services.dtypes import InputData, AST, AllOutputs


def main(data: InputData) -> AllOutputs:
    """
    Process input data and generate SQL output from Excel formula AST.

    Takes structured input data containing an Abstract Syntax Tree (AST) and
    column mappings, then processes it through the appropriate generator functions
    to produce SQL equivalent expressions.

    Args:
        data (InputData): Dictionary containing:
            - ast: The Abstract Syntax Tree representing the Excel formula
            - columns: Mapping of Excel column letters to SQL column names

    Returns:
        AllOutputs: Processed output containing the original AST structure
                   enhanced with SQL equivalents and column mappings.

    Examples:
        >>> data = {
        ...     "ast": {"type": "cell", "refType": "relative", "key": "A1"},
        ...     "columns": {"A": "col1"}
        ... }
        >>> result = main(data)
        >>> result["sql"]
        'col1'
    """
    ast: AST = data["ast"]
    columns: Dict[str, str] = data["columns"]

    return MAPS[ast["type"]](ast, columns)


if __name__ == "__main__":
    import json

    # Formula: "=SUM(A1:$E$1) + IF(AND(A1 > 5, B1 < 20), TRUE, FALSE) - E1 / 2.1"
    ast: AST = {
        "type": "binary-expression",
        "operator": "-",
        "left": {
            "type": "binary-expression",
            "operator": "+",
            "left": {
                "type": "function",
                "name": "SUM",
                "arguments": [
                    {
                        "type": "cell-range",
                        "left": {"type": "cell", "refType": "relative", "key": "A1"},
                        "right": {"type": "cell", "refType": "absolute", "key": "$E$1"},
                    }
                ],
            },
            "right": {
                "type": "function",
                "name": "IF",
                "arguments": [
                    {
                        "type": "function",
                        "name": "AND",
                        "arguments": [
                            {
                                "type": "binary-expression",
                                "operator": ">",
                                "left": {
                                    "type": "cell",
                                    "refType": "relative",
                                    "key": "A1",
                                },
                                "right": {"type": "number", "value": 5},
                            },
                            {
                                "type": "binary-expression",
                                "operator": "<",
                                "left": {
                                    "type": "cell",
                                    "refType": "relative",
                                    "key": "B1",
                                },
                                "right": {"type": "number", "value": 20},
                            },
                        ],
                    },
                    {"type": "text", "value": "True"},
                    {"type": "text", "value": "False"},
                ],
            },
        },
        "right": {
            "type": "binary-expression",
            "operator": "/",
            "left": {"type": "cell", "refType": "relative", "key": "E1"},
            "right": {"type": "number", "value": 2.1},
        },
    }
    columns = {"A": "col1", "B": "col2", "C": "col3", "D": "col4", "E": "col5"}
    data: InputData = {"ast": ast, "columns": columns}

    result = main(data)
    print(json.dumps(result, indent=4))

    """
    Seems to work as expected, here is the output:

    Formula: "=SUM(A1:$E$1) + IF(AND(A1 > 5, B1 < 20), TRUE, FALSE) - E1 / 2.1"
    Expected sql: (col1 + col2 + col3 + col4 + col5 + CASE WHEN col1 > 5 AND col2 < 20 THEN TRUE ELSE FALSE END) - (col5 / 2.1)

    Output:
    {
        "type": "binary-expression",
        "operator": "-",
        "left": {
            "type": "binary-expression",
            "operator": "+",
            "left": {
                "type": "function",
                "arguments": [
                    {
                        "type": "cell-range",
                        "start": "A1",
                        "end": "E1",
                        "cells": [
                            "A",
                            "B",
                            "C",
                            "D",
                            "E"
                        ],
                        "columns": [
                            "col1",
                            "col2",
                            "col3",
                            "col4",
                            "col5"
                        ],
                        "error": null
                    }
                ],
                "name": "SUM",
                "sql": "col1 + col2 + col3 + col4 + col5"
            },
            "right": {
                "type": "function",
                "arguments": [
                    {
                        "type": "function",
                        "arguments": [
                            {
                                "type": "binary-expression",
                                "operator": ">",
                                "left": {
                                    "type": "cell",
                                    "cell": "A1",
                                    "refType": "relative",
                                    "column": "col1",
                                    "error": null,
                                    "sql": "col1"
                                },
                                "right": {
                                    "type": "number",
                                    "value": 5.0,
                                    "sql": 5
                                },
                                "sql": "(col1) > (5)"
                            },
                            {
                                "type": "binary-expression",
                                "operator": "<",
                                "left": {
                                    "type": "cell",
                                    "cell": "B1",
                                    "refType": "relative",
                                    "column": "col2",
                                    "error": null,
                                    "sql": "col2"
                                },
                                "right": {
                                    "type": "number",
                                    "value": 20.0,
                                    "sql": 20
                                },
                                "sql": "(col2) < (20)"
                            }
                        ],
                        "name": "AND",
                        "sql": "(col1) > (5) AND (col2) < (20)"
                    },
                    {
                        "type": "logical",
                        "value": true,
                        "sql": "TRUE"
                    },
                    {
                        "type": "logical",
                        "value": false,
                        "sql": "FALSE"
                    }
                ],
                "name": "IF",
                "sql": "CASE WHEN (col1) > (5) AND (col2) < (20) THEN TRUE ELSE FALSE END"
            },
            "sql": "(col1 + col2 + col3 + col4 + col5) + (CASE WHEN (col1) > (5) AND (col2) < (20) THEN TRUE ELSE FALSE END)"
        },
        "right": {
            "type": "binary-expression",
            "operator": "/",
            "left": {
                "type": "cell",
                "cell": "E1",
                "refType": "relative",
                "column": "col5",
                "error": null,
                "sql": "col5"
            },
            "right": {
                "type": "number",
                "value": 2.1,
                "sql": 2.1
            },
            "sql": "(col5) / (2.1)"
        },
        "sql": "((col1 + col2 + col3 + col4 + col5) + (CASE WHEN (col1) > (5) AND (col2) < (20) THEN TRUE ELSE FALSE END)) - ((col5) / (2.1))"
    }
    """

"""
More examples to test:
    example_ast_and: AST = {
        "type": "function",
        "name": "AND",
        "arguments": [
            {
                "type": "binary-expression",
                "operator": ">",
                "left": {"type": "cell", "refType": "relative", "key": "A1"},
                "right": {"type": "number", "value": 5},
            },
            {
                "type": "binary-expression",
                "operator": "<",
                "left": {"type": "cell", "refType": "relative", "key": "B1"},
                "right": {"type": "number", "value": 20},
            },
        ],
    }

    example_ast_sum: AST = {
        "type": "function",
        "name": "SUM",
        "arguments": [
            {
                "type": "cell-range",
                "left": {"type": "cell", "refType": "relative", "key": "A1"},
                "right": {"type": "cell", "refType": "absolute", "key": "E1"},
            }
        ],
    }

    example_ast_if: AST = {
        "type": "function",
        "name": "IF",
        "arguments": [
            {
                "type": "binary-expression",
                "operator": ">",
                "left": {"type": "cell", "refType": "relative", "key": "B1"},
                "right": {"type": "number", "value": 10},
            },
            {"type": "cell", "refType": "relative", "key": "C1"},
            {"type": "cell", "refType": "relative", "key": "D1"},
        ],
    }

    example_ast_functions_nested = {
        "type": "function",
        "name": "IF",
        "arguments": [
            {
                "type": "function",
                "name": "AND",
                "arguments": [
                    {
                        "type": "binary-expression",
                        "operator": ">",
                        "left": {"type": "cell", "refType": "relative", "key": "A1"},
                        "right": {"type": "number", "value": 5},
                    },
                    {
                        "type": "binary-expression",
                        "operator": "<",
                        "left": {"type": "cell", "refType": "relative", "key": "B1"},
                        "right": {"type": "number", "value": 20},
                    },
                ],
            },
            {"type": "logical", "value": True},
            {"type": "logical", "value": False},
        ],
    }

    example_ast_nested = {
        "type": "binary-expression",
        "operator": "-",
        "left": {
            "type": "binary-expression",
            "operator": "+",
            "left": example_ast_sum,
            "right": example_ast_if,
        },
        "right": {
            "type": "binary-expression",
            "operator": "/",
            "left": {"type": "cell", "refType": "relative", "key": "E1"},
            "right": {"type": "cell", "refType": "relative", "key": "E1"},
        },
    }

    example_ast = example_ast_nested
    example_columns = {"A": "col1", "B": "col2", "C": "col3", "D": "col4", "E": "col5"}
    data: InputData = {"ast": example_ast, "columns": example_columns}

    result = main(data)
    print(json.dumps(result, indent=4))
"""
