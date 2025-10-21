import json

from proto_utils.generated.parsers import sql_builder_pb2
from proto_utils.parsers import DDLGeneratorSerde, SQLBuilderSerde

from src.core.config import settings
from src.services.sql_builder import sql_builder
from src.utils.logger import logger


def sql_builder_handler(
    request: sql_builder_pb2.BuildSQLRequest,
) -> sql_builder_pb2.BuildSQLResponse:
    """Handle SQL building request by processing DDL responses and generating SQL.

    Args:
        request: The gRPC request containing DDL responses and column type info.

    Returns:
        The gRPC response containing generated SQL statements.
    """
    try:
        # Log request processing start
        table_name = request.table_name
        column_count = len(request.cols)

        logger.info(
            f"[HANDLER] Processing SQL request - "
            f"Table: {table_name}, Columns: {column_count}"
        )

        # Deserialize request data
        logger.debug("[HANDLER] Deserializing DDL responses...")
        columns = {
            col: DDLGeneratorSerde.deserialize_ddl_response(col_data)
            for col, col_data in request.cols.items()
        }

        dtypes_map = {
            col_name: {"type": col_info.type, "extra": col_info.extra}
            for col_name, col_info in request.dtypes.items()
        }

        if settings.SQL_BUILDER_DEBUG:
            logger.debug(f"[HANDLER] Column types: {list(dtypes_map.keys())}")

        # Generate SQL
        logger.debug("[HANDLER] Invoking core SQL building service...")
        output = sql_builder(
            cols=columns, dtypes=dtypes_map, table_name=table_name
        )

        # Log generation results
        if output.get("error"):
            logger.warning(f"[HANDLER] SQL building failed: {output['error']}")
        else:
            content_levels = len(output.get("content", {}))
            logger.info(
                f"[HANDLER] SQL building successful - Levels: {content_levels}"
            )

        # Serialize response
        logger.debug("[HANDLER] Serializing response...")
        logger.debug(json.dumps(output, indent=2))
        response = SQLBuilderSerde.serialize_build_sql_response(output)

        logger.info("[HANDLER] Request processed successfully")
        return response

    except Exception as e:
        logger.error(f"[HANDLER] SQL building handler failed: {e}")
        logger.error(
            f"[HANDLER] Request details - Table: {request.table_name}, Columns: {len(request.cols)}"
        )
        raise
