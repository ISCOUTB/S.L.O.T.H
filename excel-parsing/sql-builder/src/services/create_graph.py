from services import dtypes
from typing import Dict, Callable
from igraph import Graph


MAPS_DTYPES: Dict[
    dtypes.AstTypes, Callable[[dtypes.AllOutputs], dtypes.ColReferences]
] = {
    "cell": lambda x: search_columns_cell(x),
    "cell_range": lambda x: search_columns_cell_range(x),
    "logical": lambda x: search_columns_constants(x),
    "text": lambda x: search_columns_constants(x),
    "number": lambda x: search_columns_constants(x),
    "function": lambda x: search_columns_function(x),
    "binary-expression": lambda x: search_columns_binary_expression(x),
}


def create_dependency_graph(cols: Dict[str, dtypes.AllOutputs]) -> Graph:
    """
    Create a dependency graph from the provided columns.

    Args:
        cols (Dict[str, dtypes.AllOutputs]): A dictionary where keys are column names and
                                            values are dtypes.AllOutputs objects representing the columns.

    Returns:
        Graph: An igraph Graph object representing the dependencies.
    """
    g = Graph(directed=True)
    g.add_vertices(list(cols.keys()))

    for col_name, col in cols.items():
        col_type = col["type"]
        cols_refs = MAPS_DTYPES[col_type](col)
        if cols_refs["error"] or cols_refs["constants"]:
            continue

        for col_ref in cols_refs["columns"]:
            # Add an edge from the current column to each referenced column
            g.add_edge(col_name, col_ref)

    return g


def search_columns_cell(source_col: dtypes.CellMapsOutput) -> dtypes.ColReferences:
    """
    Search for the column name in a cell mapping output.

    Args:
        source_col (dtypes.CellMapsOutput): The cell mapping output containing the column information.

    Returns:
        dtypes.ColReferences: The column name if found, otherwise an empty string.
    """
    if source_col["type"] != "cell":
        return {"columns": [], "error": "Invalid cell mapping type", "constants": False}
    return {"columns": [source_col["column"]], "error": None, "constants": False}


def search_columns_cell_range(
    source_col: dtypes.CellRangeMapsOutput,
) -> dtypes.ColReferences:
    """
    Search for the columns in a cell range mapping output.

    Args:
        source_col (dtypes.CellRangeMapsOutput): The cell range mapping output containing the columns

    Returns:
        List[str]: A list of column names if the type is "cell_range", otherwise an empty list.
    """
    if source_col["type"] != "cell_range":
        return {
            "columns": [],
            "error": "Invalid cell range mapping type",
            "constants": False,
        }
    return {"columns": source_col["columns"], "error": None, "constants": False}


def search_columns_constants(
    source_col: dtypes.ConstantsOutputs,
) -> dtypes.ColReferences:
    """
    Search for the columns in a logical mapping output.

    Args:
        source_col (dtypes.LogicalMapsOutput): The logical mapping output containing the logical value.

    Returns:
        dtypes.ColReferences: An empty list since logical values do not map to columns.
    """
    if source_col["type"] not in {"logical", "text", "number"}:
        return {
            "columns": [],
            "error": "Invalid logical mapping type",
            "constants": False,
        }
    return {"columns": [], "error": None, "constants": True}


def search_columns_function(
    source_col: dtypes.FunctionMapsOutput,
) -> dtypes.ColReferences:
    """
    Search for the columns in a function mapping output.

    Args:
        source_col (dtypes.FunctionMapsOutput): The function mapping output containing the function name and arguments.

    Returns:
        dtypes.ColReferences: A list of column names referenced by the function.
    """
    if source_col["type"] != "function":
        return {
            "columns": [],
            "error": "Invalid function mapping type",
            "constants": False,
        }

    cols = []
    for arg in source_col["arguments"]:
        arg_type = arg["type"]
        cols.extend(MAPS_DTYPES[arg_type](arg)["columns"])

    return {"columns": list(set(cols)), "error": None, "constants": False}


def search_columns_binary_expression(
    source_col: dtypes.BinaryExpressionMapsOutput,
) -> dtypes.ColReferences:
    """
    Search for the columns in a binary expression mapping output.

    Args:
        source_col (dtypes.BinaryExpressionMapsOutput): The binary expression mapping output containing the left and right expressions.

    Returns:
        dtypes.ColReferences: A list of column names referenced by the binary expression.
    """
    if source_col["type"] != "binary-expression":
        return {
            "columns": [],
            "error": "Invalid binary expression mapping type",
            "constants": False,
        }

    cols_left = MAPS_DTYPES[source_col["left"]["type"]](source_col["left"])
    cols_right = MAPS_DTYPES[source_col["right"]["type"]](source_col["right"])

    return {
        "columns": list(set(cols_left["columns"]) | set(cols_right["columns"])),
        "error": None,
        "constants": False,
    }
