"""Formula parser serialization and deserialization module.

This module provides serialization and deserialization utilities for Excel formula
parsing operations. Contains the FormulaParserSerde class with methods for converting
between Python dictionaries and Protocol Buffer messages for formula parsing requests
and responses.
"""

from proto_utils.parsers import dtypes
from proto_utils.parsers.dtypes_serde import DTypesSerde
from proto_utils.generated.parsers import formula_parser_pb2


class FormulaParserSerde:
    """Serialization and deserialization utilities for formula parser operations.
    
    This class provides static methods for converting between Python TypedDict
    objects and their corresponding Protocol Buffer message representations for
    Excel formula parsing operations. Handles parsing requests and responses
    including tokens and Abstract Syntax Trees.
    """

    @staticmethod
    def serialize_formula_parser_request(
        request: dtypes.FormulaParserRequest,
    ) -> formula_parser_pb2.FormulaParserRequest:
        """Serialize a FormulaParserRequest dictionary to Protocol Buffer format.
        
        Args:
            request: The formula parser request dictionary to serialize.
            
        Returns:
            The serialized Protocol Buffer FormulaParserRequest message.
        """
        return formula_parser_pb2.FormulaParserRequest(formula=request["formula"])

    @staticmethod
    def deserialize_formula_parser_request(
        proto: formula_parser_pb2.FormulaParserRequest,
    ) -> dtypes.FormulaParserRequest:
        """Deserialize a Protocol Buffer FormulaParserRequest to dictionary format.
        
        Args:
            proto: The Protocol Buffer FormulaParserRequest message to deserialize.
            
        Returns:
            The deserialized formula parser request dictionary.
        """
        return dtypes.FormulaParserRequest(formula=proto.formula)

    @staticmethod
    def serialize_formula_parser_response(
        response: dtypes.FormulaParserResponse,
    ) -> formula_parser_pb2.FormulaParserResponse:
        """Serialize a FormulaParserResponse dictionary to Protocol Buffer format.
        
        Args:
            response: The formula parser response dictionary to serialize.
            
        Returns:
            The serialized Protocol Buffer FormulaParserResponse message.
        """
        return formula_parser_pb2.FormulaParserResponse(
            formula=response["formula"],
            tokens=(
                DTypesSerde.serialize_tokens(response["tokens"])
                if response["tokens"]
                else None
            ),
            ast=(
                DTypesSerde.serialize_ast(response["ast"]) if response["ast"] else None
            ),
            error=response["error"],
        )

    @staticmethod
    def deserialize_formula_parser_response(
        proto: formula_parser_pb2.FormulaParserResponse,
    ) -> dtypes.FormulaParserResponse:
        """Deserialize a Protocol Buffer FormulaParserResponse to dictionary format.
        
        Args:
            proto: The Protocol Buffer FormulaParserResponse message to deserialize.
            
        Returns:
            The deserialized formula parser response dictionary.
        """
        return dtypes.FormulaParserResponse(
            formula=proto.formula,
            tokens=(
                DTypesSerde.deserialize_tokens(proto.tokens)
                if proto.HasField("tokens")
                else None
            ),
            ast=(
                DTypesSerde.deserialize_ast(proto.ast)
                if proto.HasField("ast")
                else None
            ),
            error=proto.error,
        )
