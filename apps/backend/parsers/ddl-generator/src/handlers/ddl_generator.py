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
    try:
        # Log input data info
        column_count = len(request.columns)
        ast_present = request.HasField("ast")
        logger.info(
            f"[HANDLER] Processing request - AST: {ast_present}, Columns: {column_count}"
        )

        # Deserialize input data
        input_data = DDLRequest(
            ast=DTypesSerde.deserialize_ast(request.ast),
            columns=dict(request.columns),
        )

        # Generate DDL
        output = ddl_generator.generate_ddl(input_data)

        # Log output info
        if settings.DDL_GENERATOR_DEBUG:
            logger.debug(f"[HANDLER] Generated DDL output: {output}")

        # Serialize response
        response = DDLGeneratorSerde.serialize_ddl_response(output)
        logger.info("[HANDLER] Request processed successfully")

        return response

    except Exception as e:
        logger.error(f"[HANDLER] DDL generation failed: {e}")
        raise
