from typing import Callable, Dict, Iterable

from igraph import Graph
from proto_utils.parsers import dtypes

MAPS_DTYPES: Dict[
    dtypes.AstType, Callable[[dtypes.AllASTs], dtypes.ColReferences]
] = {
    "cell": lambda x: search_columns_cell(x),
    "cell_range": lambda x: search_columns_cell_range(x),
    "logical": lambda x: search_columns_constants(x),
    "text": lambda x: search_columns_constants(x),
    "number": lambda x: search_columns_constants(x),
    "function": lambda x: search_columns_function(x),
    "binary-expression": lambda x: search_columns_binary_expression(x),
    "unary-expression": lambda x: search_columns_unary_expression(x),
}


def is_constant(col_refs: dtypes.ColReferences, cols: Iterable[str]) -> bool:
    """
    Check if the column references are constants.

    Args:
        col_refs (dtypes.ColReferences): The column references to check.
        cols (Iterable[str]): The set of column names to check against.

    Returns:
        bool: True if the column references are constants, False otherwise.
    """
    return (
        col_refs["error"]
        or col_refs["constants"]
        or not col_refs["columns"]
        or (
            len(col_refs["columns"]) == 1 and col_refs["columns"][0] not in cols
        )
    )


def create_dependency_graph(cols: Dict[str, dtypes.AllASTs]) -> Graph:
    """
    Create a dependency graph from the provided columns.

    Args:
        cols (Dict[str, dtypes.AllASTs]): A dictionary where keys are column names and
                                            values are dtypes.AllASTs objects representing the columns.

    Returns:
        Graph: An igraph Graph object representing the dependencies.
    """
    g = Graph(directed=True)
    cols_name = list(cols.keys())
    g.add_vertices(cols_name)

    for col_name, col in cols.items():
        col_type = col["type"]
        cols_refs = MAPS_DTYPES[col_type](col)
        if is_constant(cols_refs, cols_name):
            continue

        for col_ref in cols_refs["columns"]:
            # Add an edge from the current column to each referenced column
            g.add_edge(col_name, col_ref)

    return g


def search_columns_cell(source_col: dtypes.CellAST) -> dtypes.ColReferences:
    """
    Search for the column name in a cell mapping output.

    Args:
        source_col (dtypes.CellAST): The cell mapping output containing the column information.

    Returns:
        dtypes.ColReferences: The column name if found, otherwise an empty string.
    """
    if source_col["type"] != "cell":
        return dtypes.ColReferences(
            columns=[],
            error="Invalid cell mapping type",
            constants=False,
        )
    return dtypes.ColReferences(
        columns=[source_col["column"]],
        error=None,
        constants=False,
    )


def search_columns_cell_range(
    source_col: dtypes.CellRangeAST,
) -> dtypes.ColReferences:
    """
    Search for the columns in a cell range mapping output.

    Args:
        source_col (dtypes.CellRangeAST): The cell range mapping output containing the columns

    Returns:
        List[str]: A list of column names if the type is "cell_range", otherwise an empty list.
    """
    if source_col["type"] != "cell_range":
        return dtypes.CellRangeAST(
            columns=[],
            error="Invalid cell range mapping type",
            constants=False,
        )
    return dtypes.CellRangeAST(
        columns=source_col["columns"],
        error=None,
        constants=False,
    )


def search_columns_constants(
    source_col: dtypes.ConstantsASTs,
) -> dtypes.ColReferences:
    """
    Search for the columns in a constants mapping output.

    Args:
        source_col (dtypes.ConstantsASTs): The constants mapping output containing logical, numeric, or text values.

    Returns:
        dtypes.ColReferences: An empty list since constant values do not map to columns.
    """
    if source_col["type"] not in {"logical", "text", "number"}:
        return dtypes.ColReferences(
            columns=[],
            error="Invalid logical mapping type",
            constants=False,
        )
    return dtypes.ColReferences(
        columns=[],
        error=None,
        constants=True,
    )


def search_columns_function(
    source_col: dtypes.FunctionAST,
) -> dtypes.ColReferences:
    """
    Search for the columns in a function mapping output.

    Args:
        source_col (dtypes.FunctionAST): The function mapping output containing the function name and arguments.

    Returns:
        dtypes.ColReferences: A list of column names referenced by the function.
    """
    if source_col["type"] != "function":
        return dtypes.FunctionAST(
            columns=[],
            error="Invalid function mapping type",
            constants=False,
        )

    cols = []
    for arg in source_col["arguments"]:
        arg_type = arg["type"]
        cols.extend(MAPS_DTYPES[arg_type](arg)["columns"])

    return dtypes.FunctionAST(
        columns=list(set(cols)),
        error=None,
        constants=False,
    )


def search_columns_binary_expression(
    source_col: dtypes.BinaryExpressionAST,
) -> dtypes.ColReferences:
    """
    Search for the columns in a binary expression mapping output.

    Args:
        source_col (dtypes.BinaryExpressionAST): The binary expression mapping output containing the left and right expressions.

    Returns:
        dtypes.ColReferences: A list of column names referenced by the binary expression.
    """
    if source_col["type"] != "binary-expression":
        return dtypes.ColReferences(
            columns=[],
            error="Invalid binary expression mapping type",
            constants=False,
        )

    cols_left = MAPS_DTYPES[source_col["left"]["type"]](source_col["left"])
    cols_right = MAPS_DTYPES[source_col["right"]["type"]](source_col["right"])

    return dtypes.ColReferences(
        columns=list(set(cols_left["columns"]) | set(cols_right["columns"])),
        error=None,
        constants=False,
    )


def search_columns_unary_expression(
    source_col: dtypes.UnaryExpressionAST,
) -> dtypes.ColReferences:
    """
    Search for the columns in a unary expression mapping output.

    Args:
        source_col (dtypes.UnaryExpressionAST): The unary expression mapping output containing the expression.

    Returns:
        dtypes.ColReferences: A list of column names referenced by the unary expression.
    """
    if source_col["type"] != "unary-expression":
        return dtypes.ColReferences(
            columns=[],
            error="Invalid unary expression mapping type",
            constants=False,
        )

    cols = MAPS_DTYPES[source_col["operand"]["type"]](source_col["operand"])
    return dtypes.ColReferences(
        columns=cols["columns"],
        error=None,
        constants=False,
    )
