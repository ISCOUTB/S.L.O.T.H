from typing import Dict
from services import dtypes
from sqlglot import transpile

from services.builder import build_sql
from services.utils import has_cyclic_dependencies
from services.create_graph import create_dependency_graph


def sql_builder(
    cols: Dict[str, dtypes.AllOutputs],
    dtypes: Dict[str, Dict[str, str]],
    table_name: str,
) -> dtypes.SQLExpressions:
    """
    Main function to build SQL expressions from column definitions and their dependencies.

    Args:
        cols (Dict[str, dtypes.AllOutputs]): Column definitions with their types and SQL expressions.
        dtypes (Dict[str, Dict[str, str]]): Data types for each column.
        table_name (str): Name of the table to create.

    Returns:
        dtypes.SQLExpressions: Dictionary mapping column names to their SQL expressions.
    """
    graph = create_dependency_graph(cols)
    if has_cyclic_dependencies(graph):
        return {"content": {}, "error": "The AST contains cyclic dependencies."}

    sql_expressions = build_sql(cols, graph, dtypes, table_name)

    # Just in case
    sql_expressions = {
        level: [transpile(expr, read="postgres")[0] for expr in expressions]
        for level, expressions in sql_expressions.items()
    }
    return {"content": sql_expressions, "error": None}


if __name__ == "__main__":
    import json

    cols: Dict[str, dtypes.AllOutputs] = {
        "col1": {"type": "number", "value": 10},
        "col2": {
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
                        "error": None,
                        "sql": "col1",
                    },
                    "right": {"type": "number", "value": 18.0, "sql": 18},
                    "sql": "(col1) > (18)",
                },
                {"type": "text", "value": "Adult", "sql": "'Adult'"},
                {"type": "text", "value": "Minor", "sql": "'Minor'"},
            ],
            "name": "IF",
            "sql": "CASE WHEN (col1) > (18) THEN 'Adult' ELSE 'Minor' END",
        },
        "col3": {
            "type": "cell",
            "cell": "B1",
            "refType": "relative",
            "column": "col2",
            "error": None,
            "sql": "col2",
        },
        "col4": {"type": "number", "value": 10},
    }

    content = sql_builder(
        cols,
        table_name="test_table",
        dtypes={
            "col1": {"type": "INTEGER"},
            "col2": {"type": "TEXT"},
            "col3": {"type": "TEXT"},
            "col4": {"type": "INTEGER"},
        },
    )

    print(json.dumps(content, indent=2))

    priorities = content["content"]
    sql_expression = ""
    for level, expressions in priorities.items():
        for expr in expressions:
            sql_expression += f"\n{expr}"

    print(sql_expression)
