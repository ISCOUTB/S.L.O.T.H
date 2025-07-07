import grpc
from clients import sql_builder_pb2, sql_builder_pb2_grpc

from core.config import settings

SQL_BUILDER_CHANNEL = grpc.insecure_channel(settings.SQL_BUILDER_CHANNEL)
SQL_BUILDER_STUB = sql_builder_pb2_grpc.SQLBuilderStub(SQL_BUILDER_CHANNEL)

# TODO: Replace with actual request parameters
request = sql_builder_pb2.BuildSQLRequest(...)
response = SQL_BUILDER_STUB.BuildSQL(request)
print(response)
