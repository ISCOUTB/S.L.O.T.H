"""DDL generator serialization and deserialization module.

This module provides serialization and deserialization utilities for DDL generation
operations that convert Excel formula ASTs into SQL DDL statements. Contains the
DDLGeneratorSerde class with methods for converting between Python dictionaries
and Protocol Buffer messages for DDL generation requests and responses.
"""

from proto_utils.parsers import dtypes
from proto_utils.parsers.dtypes_serde import DTypesSerde
from proto_utils.generated.parsers import ddl_generator_pb2


class DDLGeneratorSerde:
    """Serialization and deserialization utilities for DDL generator operations.

    This class provides static methods for converting between Python TypedDict
    objects and their corresponding Protocol Buffer message representations for
    DDL generation operations. Handles requests and responses for generating
    SQL DDL statements from Excel formula ASTs.
    """

    @staticmethod
    def serialize_ddl_request(
        request: dtypes.DDLRequest,
    ) -> ddl_generator_pb2.DDLRequest:
        """Serialize a DDLRequest dictionary to Protocol Buffer format.

        Args:
            request: The DDL request dictionary to serialize.

        Returns:
            The serialized Protocol Buffer DDLRequest message.
        """
        return ddl_generator_pb2.DDLRequest(
            ast=DTypesSerde.serialize_ast(request["ast"]),
            columns=request["columns"],
        )

    @staticmethod
    def deserialize_ddl_request(
        proto: ddl_generator_pb2.DDLRequest,
    ) -> dtypes.DDLRequest:
        """Deserialize a Protocol Buffer DDLRequest to dictionary format.

        Args:
            proto: The Protocol Buffer DDLRequest message to deserialize.

        Returns:
            The deserialized DDL request dictionary.
        """
        return dtypes.DDLRequest(
            ast=DTypesSerde.deserialize_ast(proto.ast),
            columns=dict(proto.columns),
        )

    @staticmethod
    def serialize_ddl_response(
        response: dtypes.DDLResponse,
    ) -> ddl_generator_pb2.DDLResponse:
        """Serialize a DDLResponse dictionary to Protocol Buffer format.

        Args:
            response: The DDL response dictionary to serialize.

        Returns:
            The serialized Protocol Buffer DDLResponse message.
        """
        proto = ddl_generator_pb2.DDLResponse(
            type=DTypesSerde.serialize_ast_type(response["type"]),
            sql=response["sql"],
            # Cell Reference Information
            cell=response["cell"] if "cell" in response else None,
            refType=(
                DTypesSerde.serialize_ref_type(response["refType"])
                if "refType" in response and response["refType"]
                else None
            ),
            column=response["column"] if "column" in response else None,
            error_cell=response["error_cell"] if "error_cell" in response else None,
            # Cell Range Information
            start=response["start"] if "start" in response else None,
            end=response["end"] if "end" in response else None,
            cells=(
                list(response["cells"])
                if "cells" in response and response["cells"]
                else None
            ),
            columns=(
                list(response["columns"])
                if "columns" in response and response["columns"]
                else None
            ),
            error_cell_range=(
                response["error_cell_range"] if "error_cell_range" in response else None
            ),
            # Binary Expression Information
            operator=response["operator"] if "operator" in response else None,
            left=(
                DDLGeneratorSerde.serialize_ddl_response(response["left"])
                if "left" in response and response["left"]
                else None
            ),
            right=(
                DDLGeneratorSerde.serialize_ddl_response(response["right"])
                if "right" in response and response["right"]
                else None
            ),
            # Function Information
            name=response["name"] if "name" in response else None,
            arguments=(
                list(
                    map(DDLGeneratorSerde.serialize_ddl_response, response["arguments"])
                )
                if "arguments" in response and response["arguments"]
                else None
            ),
            # Unary Expression Information
            operand=(
                DDLGeneratorSerde.serialize_ddl_response(response["operand"])
                if "operand" in response and response["operand"]
                else None
            ),
        )

        # Handle literal values
        if "value" in response and response["value"] is not None:
            if isinstance(response["value"], float):
                proto.number_value = response["value"]
            elif isinstance(response["value"], str):
                proto.text_value = response["value"]
            elif isinstance(response["value"], bool):
                proto.logical_value = response["value"]

        return proto

    @staticmethod
    def deserialize_ddl_response(
        proto: ddl_generator_pb2.DDLResponse,
    ) -> dtypes.DDLResponse:
        """Deserialize a Protocol Buffer DDLResponse to dictionary format.

        Args:
            proto: The Protocol Buffer DDLResponse message to deserialize.

        Returns:
            The deserialized DDL response dictionary.
        """
        response = dtypes.DDLResponse(
            type=DTypesSerde.deserialize_ast_type(proto.type),
            sql=proto.sql,
            # Cell Reference Information
            cell=proto.cell if proto.HasField("cell") else None,
            refType=(
                DTypesSerde.deserialize_ref_type(proto.refType)
                if proto.HasField("refType")
                else None
            ),
            column=proto.column if proto.HasField("column") else None,
            error_cell=proto.error_cell if proto.HasField("error_cell") else None,
            # Cell Range Information
            start=proto.start if proto.HasField("start") else None,
            end=proto.end if proto.HasField("end") else None,
            cells=list(proto.cells) if proto.cells else [],
            columns=list(proto.columns) if proto.columns else [],
            error_cell_range=(
                proto.error_cell_range if proto.HasField("error_cell_range") else None
            ),
            # Binary Expression Information
            operator=proto.operator if proto.HasField("operator") else None,
            left=(
                DDLGeneratorSerde.deserialize_ddl_response(proto.left)
                if proto.HasField("left")
                else None
            ),
            right=(
                DDLGeneratorSerde.deserialize_ddl_response(proto.right)
                if proto.HasField("right")
                else None
            ),
            # Function Information
            name=proto.name if proto.HasField("name") else None,
            arguments=(
                list(map(DDLGeneratorSerde.deserialize_ddl_response, proto.arguments))
                if proto.arguments
                else []
            ),
            # Unary Expression Information
            operand=(
                DDLGeneratorSerde.deserialize_ddl_response(proto.operand)
                if proto.HasField("operand")
                else None
            ),
        )

        # Handle literal values
        if proto.HasField("number_value"):
            response["value"] = proto.number_value
        elif proto.HasField("text_value"):
            response["value"] = proto.text_value
        elif proto.HasField("logical_value"):
            response["value"] = proto.logical_value
        else:
            response["value"] = None

        return response
