"""
Utilities for Excel column and cell reference manipulation.

This module provides helper functions for working with Excel column references,
converting between column letters and indices, and generating column ranges.
"""

from typing import List
from functools import lru_cache


def get_row_from_cell(cell: str) -> int:
    """
    Extract the row part from a cell reference.

    Args:
        cell (str): The cell reference (e.g., "A1", "BC25").

    Returns:
        int: The row part of the cell reference (e.g., 1, 25).

    Examples:
        >>> get_row_from_cell("A1")
        1
        >>> get_row_from_cell("BC25")
        25
    """
    return int("".join(filter(str.isdigit, cell)))


def get_rows_range(start: str, end: str) -> List[int]:
    """
    Generate a list of row numbers within a specified range.

    Args:
        start (str): The starting cell reference (e.g., "A1").
        end (str): The ending cell reference (e.g., "A10").

    Returns:
        List[int]: A list of row numbers from start to end (inclusive).

    Examples:
        >>> get_rows_range("A1", "A3")
        [1, 2, 3]
        >>> get_rows_range("B5", "B7")
        [5, 6, 7]
    """
    start_row = get_row_from_cell(start)
    end_row = get_row_from_cell(end)
    return list(range(start_row, end_row + 1))


def get_column_from_cell(cell: str) -> str:
    """
    Extract the column part from a cell reference.

    Args:
        cell (str): The cell reference (e.g., "A1", "BC25").

    Returns:
        str: The column part of the cell reference (e.g., "A", "BC").

    Examples:
        >>> get_column_from_cell("A1")
        'A'
        >>> get_column_from_cell("BC25")
        'BC'
    """
    return "".join(filter(str.isalpha, cell))


def excel_col_to_index(col: str) -> int:
    """
    Convert Excel column letters to a 1-based index.

    Args:
        col (str): The column letters (e.g., "A", "Z", "AA").

    Returns:
        int: The 1-based column index (A=1, B=2, ..., Z=26, AA=27).

    Examples:
        >>> excel_col_to_index("A")
        1
        >>> excel_col_to_index("Z")
        26
        >>> excel_col_to_index("AA")
        27
    """
    col = col.upper()
    index = 0
    for char in col:
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index


@lru_cache(maxsize=2048)
def index_to_excel_col(index: int) -> str:
    """
    Convert a 1-based index to Excel column letters (optimized with caching).
    """
    if index <= 26:
        return chr(ord('A') + index - 1)
    
    quotient, remainder = divmod(index - 1, 26)
    return index_to_excel_col(quotient) + chr(ord('A') + remainder)


def get_column_range(start: str, end: str) -> List[str]:
    """
    Generate a list of Excel column letters within a specified range.

    Args:
        start (str): The starting column letter(s) (e.g., "A").
        end (str): The ending column letter(s) (e.g., "Z").

    Returns:
        List[str]: A list of column letters from start to end (inclusive).

    Examples:
        >>> get_column_range("A", "C")
        ['A', 'B', 'C']
        >>> get_column_range("Y", "AA")
        ['Y', 'Z', 'AA']
    """
    start_idx = excel_col_to_index(start)
    end_idx = excel_col_to_index(end)
    return [index_to_excel_col(i) for i in range(start_idx, end_idx + 1)]


def get_all_cells_from_range(start: str, end: str) -> List[str]:
    """
    Generate a list of all cell references in a specified range.

    Args:
        start (str): The starting cell reference (e.g., "A1").
        end (str): The ending cell reference (e.g., "B2").

    Returns:
        List[str]: A list of cell references from start to end (inclusive).

    Examples:
        >>> get_all_cells_from_range("A1", "B2")
        ['A1', 'A2', 'B1', 'B2']
    """
    start_col = get_column_from_cell(start)
    end_col = get_column_from_cell(end)
    columns = get_column_range(start_col, end_col)
    rows = get_rows_range(start, end)

    return [f"{col}{row}" for col in columns for row in rows]
