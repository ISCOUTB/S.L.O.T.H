from services import dtypes
from clients.sql_builder import sql_builder_pb2


def parse_sql_builder_response(
    response: sql_builder_pb2.BuildSQLResponse,
) -> dtypes.SQLExpressions:
    """
    Parse the SQL builder response into a structured format.

    Args:
        response (sql_builder_pb2.BuildSQLResponse): The response from the SQL builder service.

    Returns:
        dtypes.SQLExpressions: A dictionary mapping column names to their SQL expressions.
    """
    if response.error:
        raise ValueError(f"SQL Builder Error: {response.error}")

    sql_expressions = {
        level: [expr for expr in response.content[level].sql]
        for level in response.content
    }
    return {"content": sql_expressions, "error": response.error or None}
