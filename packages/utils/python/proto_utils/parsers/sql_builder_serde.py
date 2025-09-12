"""SQL builder serialization and deserialization module.

This module provides serialization and deserialization utilities for SQL builder
operations including SQL statement construction, column information handling,
and response management. Contains the SQLBuilderSerde class with methods for
converting between Python dictionaries and Protocol Buffer messages for SQL operations.
"""

from proto_utils.parsers import dtypes
from proto_utils.parsers.ddl_generator_serde import DDLGeneratorSerde
from proto_utils.generated.parsers import sql_builder_pb2


class SQLBuilderSerde:
    """Serialization and deserialization utilities for SQL builder operations.

    This class provides static methods for converting between Python TypedDict
    objects and their corresponding Protocol Buffer message representations for
    SQL builder operations. Includes methods for SQL request handling, response
    processing, and column information management.
    """
    @staticmethod
    def serialize_request_column_info(
        info: dtypes.SQLRequestColumnInfo,
    ) -> sql_builder_pb2.BuildSQLRequest.ColumnInfo:
        """Serialize a SQLRequestColumnInfo dictionary to Protocol Buffer format.

        Args:
            info: The SQL request column info dictionary to serialize.

        Returns:
            The serialized Protocol Buffer ColumnInfo message.
        """
        return sql_builder_pb2.BuildSQLRequest.ColumnInfo(
            type=info["type"], extra=info["extra"]
        )

    @staticmethod
    def deserialize_request_column_info(
        proto: sql_builder_pb2.BuildSQLRequest.ColumnInfo,
    ) -> dtypes.SQLRequestColumnInfo:
        """Deserialize a Protocol Buffer ColumnInfo to dictionary format.

        Args:
            proto: The Protocol Buffer ColumnInfo message to deserialize.

        Returns:
            The deserialized SQL request column info dictionary.
        """
        return dtypes.SQLRequestColumnInfo(type=proto.type, extra=proto.extra)

    @staticmethod
    def serialize_build_sql_request(
        request: dtypes.BuildSQLRequest,
    ) -> sql_builder_pb2.BuildSQLRequest:
        """Serialize a BuildSQLRequest dictionary to Protocol Buffer format.

        Args:
            request: The build SQL request dictionary to serialize.

        Returns:
            The serialized Protocol Buffer BuildSQLRequest message.
        """
        return sql_builder_pb2.BuildSQLRequest(
            table_name=request["table_name"],
            cols=dict(
                map(
                    lambda item: (
                        item[0],
                        DDLGeneratorSerde.serialize_ddl_response(item[1]),
                    ),
                    request["cols"].items(),
                )
            ),
            dtypes=dict(
                map(
                    lambda item: (
                        item[0],
                        SQLBuilderSerde.serialize_request_column_info(item[1]),
                    ),
                    request["dtypes"].items(),
                )
            ),
        )

    @staticmethod
    def deserialize_build_sql_request(
        proto: sql_builder_pb2.BuildSQLRequest,
    ) -> dtypes.BuildSQLRequest:
        """Deserialize a Protocol Buffer BuildSQLRequest to dictionary format.

        Args:
            proto: The Protocol Buffer BuildSQLRequest message to deserialize.

        Returns:
            The deserialized build SQL request dictionary.
        """
        return dtypes.BuildSQLRequest(
            table_name=proto.table_name,
            cols=dict(
                map(
                    lambda item: (
                        item[0],
                        DDLGeneratorSerde.deserialize_ddl_response(item[1]),
                    ),
                    proto.cols.items(),
                )
            ),
            dtypes=dict(
                map(
                    lambda item: (
                        item[0],
                        SQLBuilderSerde.deserialize_request_column_info(item[1]),
                    ),
                    proto.dtypes.items(),
                )
            ),
        )

    @staticmethod
    def serialize_sql_response_sql_content(
        content: dtypes.SQLResponseSQLContent,
    ) -> sql_builder_pb2.BuildSQLResponse.SQLContent:
        """Serialize a SQLResponseSQLContent dictionary to Protocol Buffer format.

        Args:
            content: The SQL response content dictionary to serialize.

        Returns:
            The serialized Protocol Buffer SQLContent message.
        """
        return sql_builder_pb2.BuildSQLResponse.SQLContent(
            sql=content["sql"], columns=list(content["columns"])
        )

    @staticmethod
    def deserialize_sql_response_sql_content(
        proto: sql_builder_pb2.BuildSQLResponse.SQLContent,
    ) -> dtypes.SQLResponseSQLContent:
        """Deserialize a Protocol Buffer SQLContent to dictionary format.

        Args:
            proto: The Protocol Buffer SQLContent message to deserialize.

        Returns:
            The deserialized SQL response content dictionary.
        """
        return dtypes.SQLResponseSQLContent(sql=proto.sql, columns=list(proto.columns))

    @staticmethod
    def serialize_build_sql_response_content(
        content: dtypes.BuildSQLResponseContent,
    ) -> sql_builder_pb2.BuildSQLResponse.Content:
        """Serialize a BuildSQLResponseContent dictionary to Protocol Buffer format.

        Args:
            content: The build SQL response content dictionary to serialize.

        Returns:
            The serialized Protocol Buffer Content message.
        """
        return sql_builder_pb2.BuildSQLResponse.Content(
            sql_content=list(
                map(
                    SQLBuilderSerde.serialize_sql_response_sql_content,
                    content["sql_content"],
                )
            )
        )

    @staticmethod
    def deserialize_build_sql_response_content(
        proto: sql_builder_pb2.BuildSQLResponse.Content,
    ) -> dtypes.BuildSQLResponseContent:
        """Deserialize a Protocol Buffer Content to dictionary format.

        Args:
            proto: The Protocol Buffer Content message to deserialize.

        Returns:
            The deserialized build SQL response content dictionary.
        """
        return dtypes.BuildSQLResponseContent(
            sql_content=list(
                map(
                    SQLBuilderSerde.deserialize_sql_response_sql_content,
                    proto.sql_content,
                )
            )
        )

    @staticmethod
    def serialize_build_sql_response(
        response: dtypes.BuildSQLResponse,
    ) -> sql_builder_pb2.BuildSQLResponse:
        """Serialize a BuildSQLResponse dictionary to Protocol Buffer format.

        Args:
            response: The build SQL response dictionary to serialize.

        Returns:
            The serialized Protocol Buffer BuildSQLResponse message.
        """
        return sql_builder_pb2.BuildSQLResponse(
            content=dict(
                map(
                    lambda item: (
                        item[0],
                        SQLBuilderSerde.serialize_build_sql_response_content(item[1]),
                    ),
                    response["content"].items(),
                )
            ),
            error=response["error"],
        )

    @staticmethod
    def deserialize_build_sql_response(
        proto: sql_builder_pb2.BuildSQLResponse,
    ) -> dtypes.BuildSQLResponse:
        """Deserialize a Protocol Buffer BuildSQLResponse to dictionary format.

        Args:
            proto: The Protocol Buffer BuildSQLResponse message to deserialize.

        Returns:
            The deserialized build SQL response dictionary.
        """
        return dtypes.BuildSQLResponse(
            content=dict(
                map(
                    lambda item: (
                        item[0],
                        SQLBuilderSerde.deserialize_build_sql_response_content(item[1]),
                    ),
                    proto.content.items(),
                )
            ),
            error=proto.error,
        )
