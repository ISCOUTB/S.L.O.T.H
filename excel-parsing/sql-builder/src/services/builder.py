from services import dtypes
from typing import Dict
from igraph import Graph
from services.utils import get_outgoing_connections


def has_primary_key(dtypes: Dict[str, Dict[str, str]]) -> bool:
    """
    Check if any column in the provided data types has a primary key defined.

    Args:
        dtypes (Dict[str, Dict[str, str]]): Dictionary mapping column names to their SQL data types.

    Returns:
        bool: True if any column has a primary key, False otherwise.
    """
    return any("primary key" in dtype.get("extra", "").lower() for dtype in dtypes.values())


def build_sql(
    cols: Dict[str, dtypes.AllOutputs],
    dependency_graph: Graph,
    dtypes: Dict[str, Dict[str, str]],
    table_name: str,
) -> Dict[int, list[str]]:
    """
    Build SQL expressions from the provided column definitions and their dependencies.

    Args:
        cols (Dict[str, dtypes.AllOutputs]): Dictionary mapping column names to their definitions.
        dependency_graph (Graph): Dependency graph representing relationships between columns.
        dtypes (Dict[str, Dict[str, str]]): Dictionary mapping column names to their SQL data types.
        table_name (str): Name of the table to create.

    Returns:
        Dict[int, list[str]]: Dictionary mapping column names to their SQL expressions.
    """
    primary_key_suffix = "id SERIAL PRIMARY KEY, " if not has_primary_key(dtypes) else ""
    priorities = {col: get_outgoing_connections(dependency_graph, col) for col in cols}
    level_0 = list(filter(lambda pair: pair[1] == 0, priorities.items()))
    sql_expressions = {0: f"CREATE TABLE IF NOT EXISTS {table_name} ({primary_key_suffix}"}
    for i, (col, _) in enumerate(level_0):
        # In 'extra' we can add things like 'NOT NULL', 'PRIMARY KEY', etc.
        base_sql = f"{col} {dtypes[col]['type']} {dtypes[col].get('extra', '')}".strip()
        if i == len(level_0) - 1:
            sql_expressions[0] += f"{base_sql});"
            continue
        sql_expressions[0] += f"{base_sql}, "

    sql_expressions[0] = [sql_expressions[0]]  # Convert to list for consistency

    # Sort based on the priority
    priorities_levels = list(set(priorities.values()))
    sql_expressions = {
        **sql_expressions,
        **{level: [] for level in priorities_levels if level > 0},
    }
    other_levels = sorted(
        list(filter(lambda pair: pair[1] != 0, priorities.items())), key=lambda x: x[1]
    )

    for col, level in other_levels:
        sql_expression = f"ALTER TABLE {table_name} ADD COLUMN {col} {dtypes[col]['type']}{dtypes[col].get('extra', '')} "
        sql_expression += f"GENERATED ALWAYS AS {cols[col]['sql']} STORED;"
        sql_expressions[level].append(sql_expression)

    return sql_expressions
