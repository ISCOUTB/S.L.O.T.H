import grpc
from proto_utils.generated.parsers import (
    ddl_generator_pb2,
    ddl_generator_pb2_grpc,
    dtypes_pb2,
)

from src.core.config import settings

DDL_GENERATOR_CHANNEL = grpc.insecure_channel(settings.DDL_GENERATOR_CHANNEL)
DDL_GENERATOR_STUB = ddl_generator_pb2_grpc.DDLGeneratorStub(
    DDL_GENERATOR_CHANNEL
)


ast = dtypes_pb2.AST(type=dtypes_pb2.AstType.AST_TEXT, text_value='"Alice"')
request = ddl_generator_pb2.DDLRequest(ast=ast)
request.columns.update({"A": "COL1"})

response: ddl_generator_pb2.DDLResponse = DDL_GENERATOR_STUB.GenerateDDL(
    request
)
print(response)
