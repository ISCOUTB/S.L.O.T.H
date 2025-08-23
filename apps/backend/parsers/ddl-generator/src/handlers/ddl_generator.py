import logging

from services import dtypes, ddl_generator
from clients import ddl_generator_pb2, utils
from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_ddl_handler(
    request: ddl_generator_pb2.DDLRequest,
) -> ddl_generator_pb2.DDLResponse:
    """
    Handles the DDL generation request by parsing the input data and generating the DDL response.

    Args:
        request (ddl_generator_pb2.DDLRequest): The request containing the input data for DDL generation.

    Returns:
        ddl_generator_pb2.DDLResponse: The response containing the generated DDL.
    """
    input_data = dtypes.InputData(
        ast=utils.parse_ast(request.ast),
        columns=dict(request.columns),
    )

    output = ddl_generator.generate_ddl(input_data)
    if settings.DDL_GENERATOR_DEBUG:
        logger.info(f"Generated DDL: {output}")

    return utils.parse_output_to_proto(output)
