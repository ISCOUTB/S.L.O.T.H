"""
Main entry point for the DDL generator.

This module serves as the primary interface for converting Excel formula ASTs
into SQL expressions. It processes input data containing ASTs and column mappings
to generate corresponding SQL output.
"""

from services.generator import MAPS

from typing import Dict
from services.dtypes import InputData, AST, AllOutputs


def generate_ddl(data: InputData) -> AllOutputs:
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
        >>> result = generate_ddl(data)
        >>> result["sql"]
        'col1'
    """
    ast: AST = data["ast"]
    columns: Dict[str, str] = data["columns"]

    return MAPS[ast["type"]](ast, columns)
