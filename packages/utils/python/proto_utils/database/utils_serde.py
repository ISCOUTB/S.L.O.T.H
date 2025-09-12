"""Database utilities serialization module.

This module provides serialization and deserialization utilities for converting
between Python dictionaries and Protocol Buffer messages for database operations.
Contains the DatabaseUtilsSerde class with methods for handling API responses,
property types, and JSON schema structures.
"""

from typing import Dict
from proto_utils.database import dtypes
from proto_utils.generated.database import utils_pb2


class DatabaseUtilsSerde:
    """Serialization and deserialization utilities for database operations.

    This class provides static methods for converting between Python TypedDict
    objects and their corresponding Protocol Buffer message representations.
    All methods are static and can be called without instantiating the class.
    """

    @staticmethod
    def serialize_api_response(
        api_response: dtypes.ApiResponse,
    ) -> utils_pb2.ApiResponse:
        """Serialize an ApiResponse dictionary to Protocol Buffer format.

        Args:
            api_response: The API response dictionary to serialize.

        Returns:
            The serialized Protocol Buffer ApiResponse message.
        """
        return utils_pb2.ApiResponse(
            status=api_response["status"],
            code=api_response["code"],
            message=api_response["message"],
            data=api_response["data"],
        )

    @staticmethod
    def deserialize_api_response(proto: utils_pb2.ApiResponse) -> dtypes.ApiResponse:
        """Deserialize a Protocol Buffer ApiResponse to dictionary format.

        Args:
            proto: The Protocol Buffer ApiResponse message to deserialize.

        Returns:
            The deserialized API response dictionary.
        """
        return {
            "status": proto.status,
            "code": proto.code,
            "message": proto.message,
            "data": dict(proto.data),
        }

    @staticmethod
    def serialize_property_type(
        property_type: dtypes.PropertyType,
    ) -> utils_pb2.PropertyType:
        """Serialize a PropertyType string to Protocol Buffer enum format.

        Args:
            property_type: The property type string to serialize.

        Returns:
            The corresponding Protocol Buffer PropertyType enum value.
        """
        values: Dict[dtypes.PropertyType, utils_pb2.PropertyType] = {
            "string": utils_pb2.PropertyType.STRING,
            "integer": utils_pb2.PropertyType.INTEGER,
            "float": utils_pb2.PropertyType.NUMBER,
            "boolean": utils_pb2.PropertyType.BOOLEAN,
        }

        return values[property_type]

    @staticmethod
    def deserialize_property_type(proto: utils_pb2.PropertyType) -> dtypes.PropertyType:
        """Deserialize a Protocol Buffer PropertyType enum to string format.

        Args:
            proto: The Protocol Buffer PropertyType enum to deserialize.

        Returns:
            The corresponding property type string.
        """
        values: Dict[utils_pb2.PropertyType, dtypes.PropertyType] = {
            utils_pb2.PropertyType.STRING: "string",
            utils_pb2.PropertyType.INTEGER: "integer",
            utils_pb2.PropertyType.NUMBER: "float",
            utils_pb2.PropertyType.BOOLEAN: "boolean",
        }

        return values[proto]

    @staticmethod
    def serialize_properties(properties: dtypes.Properties) -> utils_pb2.Properties:
        """Serialize a Properties dictionary to Protocol Buffer format.

        Args:
            properties: The properties dictionary to serialize.

        Returns:
            The serialized Protocol Buffer Properties message.
        """
        return utils_pb2.Properties(
            type=DatabaseUtilsSerde.serialize_property_type(properties["type"]),
            extra=properties["extra"],
        )

    @staticmethod
    def deserialize_properties(proto: utils_pb2.Properties) -> dtypes.Properties:
        """Deserialize a Protocol Buffer Properties to dictionary format.

        Args:
            proto: The Protocol Buffer Properties message to deserialize.

        Returns:
            The deserialized properties dictionary.
        """
        return {
            "type": DatabaseUtilsSerde.deserialize_property_type(proto.type),
            "extra": dict(proto.extra),
        }

    @staticmethod
    def serialize_jsonschema(jsonschema: dtypes.JsonSchema) -> utils_pb2.JsonSchema:
        """Serialize a JsonSchema dictionary to Protocol Buffer format.

        Args:
            jsonschema: The JSON schema dictionary to serialize.

        Returns:
            The serialized Protocol Buffer JsonSchema message.
        """
        return utils_pb2.JsonSchema(
            schema=jsonschema["schema"],
            type=jsonschema["type"],
            required=jsonschema["required"],
            properties=dict(
                map(
                    lambda item: (
                        item[0],
                        DatabaseUtilsSerde.serialize_properties(item[1]),
                    ),
                    jsonschema["properties"].items(),
                )
            ),
        )

    @staticmethod
    def deserialize_jsonschema(proto: utils_pb2.JsonSchema) -> dtypes.JsonSchema:
        """Deserialize a Protocol Buffer JsonSchema to dictionary format.

        Args:
            proto: The Protocol Buffer JsonSchema message to deserialize.

        Returns:
            The deserialized JSON schema dictionary.
        """
        return {
            "schema": proto.schema,
            "type": proto.type,
            "required": list(proto.required),
            "properties": dict(
                map(
                    lambda item: (
                        item[0],
                        DatabaseUtilsSerde.deserialize_properties(item[1]),
                    ),
                    proto.properties.items(),
                )
            ),
        }
