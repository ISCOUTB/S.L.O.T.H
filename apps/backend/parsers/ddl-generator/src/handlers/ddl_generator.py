# from clients import ddl_generator_pb2, utils
from proto_utils.generated.parsers import ddl_generator_pb2
from proto_utils.parsers.ddl_generator_serde import DDLGeneratorSerde
from proto_utils.parsers.dtypes import DDLRequest
from proto_utils.parsers.dtypes_serde import DTypesSerde

from src.core.config import settings
from src.services import ddl_generator
from src.utils.logger import logger


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
    input_data = DDLRequest(
        ast=DTypesSerde.deserialize_ast(request.ast),
        columns=dict(request.columns),
    )

    output = ddl_generator.generate_ddl(input_data)
    if settings.DDL_GENERATOR_DEBUG:
        logger.debug(f"Generated DDL: {output}")

    return DDLGeneratorSerde.serialize_ddl_response(output)
