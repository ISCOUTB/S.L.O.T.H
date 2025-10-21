from collections.abc import Generator

import grpc
from proto_utils.generated.parsers import (
    ddl_generator_pb2_grpc,
    formula_parser_pb2_grpc,
    sql_builder_pb2_grpc,
)

from src.core.config import settings


def get_formula_parser_stub() -> Generator[
    formula_parser_pb2_grpc.FormulaParserStub,
    None,
    None,
]:
    """Create and yield a gRPC stub for the Formula Parser service."""
    channel = grpc.insecure_channel(settings.FORMULA_PARSER_CHANNEL)
    stub = formula_parser_pb2_grpc.FormulaParserStub(channel)
    try:
        yield stub
    finally:
        channel.close()


def get_ddl_generator_stub() -> Generator[
    ddl_generator_pb2_grpc.DDLGeneratorStub,
    None,
    None,
]:
    """Create and yield a gRPC stub for the DDL Generator service."""
    channel = grpc.insecure_channel(settings.DDL_GENERATOR_CHANNEL)
    stub = ddl_generator_pb2_grpc.DDLGeneratorStub(channel)
    try:
        yield stub
    finally:
        channel.close()


def get_sql_builder_stub() -> Generator[
    sql_builder_pb2_grpc.SQLBuilderStub,
    None,
    None,
]:
    """Create and yield a gRPC stub for the SQL Builder service."""
    channel = grpc.insecure_channel(settings.SQL_BUILDER_CHANNEL)
    stub = sql_builder_pb2_grpc.SQLBuilderStub(channel)
    try:
        yield stub
    finally:
        channel.close()
