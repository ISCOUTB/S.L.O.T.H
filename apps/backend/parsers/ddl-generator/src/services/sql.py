"""
SQL generation utilities for Excel formula translation.

This module provides functions to convert Excel formula functions into their
SQL equivalents. It includes a mapping of Excel functions to SQL expressions
and utilities to generate SQL code from parsed formula ASTs.
"""

from typing import List

from src.services.dtypes import AllOutputs

FUNCTION_SQL_MAP = {
    "SUM": lambda args: " + ".join(args[0]["columns"]),
    "IF": lambda args: f"CASE WHEN {args[0]['sql']} THEN {args[1]['sql']} ELSE {args[2]['sql']} END",
    "AND": lambda args: " AND ".join(arg["sql"] for arg in args),
    # Add more functions here
}


def get_sql_from_function(func_name: str, args: List[AllOutputs]) -> str:
    """
    Convert an Excel function to its SQL equivalent.

    Takes a function name and its arguments, then generates the corresponding
    SQL expression using the predefined function mappings.

    Args:
        func_name (str): The name of the Excel function (e.g., "SUM", "IF", "AND").
        args (List[AllOutputs]): List of processed arguments for the function.

    Returns:
        str: The SQL equivalent of the Excel function, or an error message
             if the function is not supported.

    Examples:
        >>> args = [{"columns": ["col1", "col2"]}]
        >>> get_sql_from_function("SUM", args)
        'col1 + col2'

        >>> get_sql_from_function("UNKNOWN", [])
        'UNSUPPORTED_FUNCTION(UNKNOWN)'
    """
    func = FUNCTION_SQL_MAP.get(func_name.upper())
    if not func:
        return f"UNSUPPORTED_FUNCTION({func_name})"
    return func(args)
