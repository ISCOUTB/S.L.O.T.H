import logging

from core.config import settings
from services import sql_builder
from clients import sql_builder_pb2, utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sql_builder_handler(
    request: sql_builder_pb2.BuildSQLRequest,
) -> sql_builder_pb2.BuildSQLResponse:
    columns = {
        col: utils.parse_ddlresponse(col_data) for col, col_data in request.cols.items()
    }
    dtypes_map = {
        col_name: {"type": col_info.type, "extra": col_info.extra}
        for col_name, col_info in request.dtypes.items()
    }
    table_name = request.table_name

    if settings.SQL_BUILDER_DEBUG:
        logger.info(
            f"Received SQL building request for table '{table_name}' with columns: {columns}"
        )

    output = sql_builder.sql_builder(
        cols=columns, dtypes=dtypes_map, table_name=table_name
    )
    return utils.parse_to_sql_response(output)
