"""Data types serialization and deserialization module.

This module provides serialization and deserialization utilities for converting
between Python dictionaries and Protocol Buffer messages for Excel formula parsing
data types, including AST nodes, tokens, and reference types used in the parsers package.
"""

from proto_utils.parsers import dtypes
from proto_utils.generated.parsers import dtypes_pb2

from typing import Dict


class DTypesSerde:
    """Serialization and deserialization utilities for parser data types.
    
    This class provides static methods for converting between Python TypedDict
    objects and their corresponding Protocol Buffer message representations for
    Excel formula parsing operations. Handles AST nodes, tokens, and reference types.
    """

    @staticmethod
    def serialize_ast_type(ast_type: dtypes.AstType) -> dtypes_pb2.AstType:
        """Serialize an AstType string to Protocol Buffer enum format.

        Args:
            ast_type: The AST type string to serialize.

        Returns:
            The corresponding Protocol Buffer AstType enum value.
        """
        values: Dict[dtypes.AstType, dtypes_pb2.AstType] = {
            "unknown": dtypes_pb2.AstType.AST_UNKNOWN,
            "binary-expression": dtypes_pb2.AstType.AST_BINARY_EXPRESSION,
            "unary-expression": dtypes_pb2.AstType.AST_UNARY_EXPRESSION,
            "cell-range": dtypes_pb2.AstType.AST_CELL_RANGE,
            "cell": dtypes_pb2.AstType.AST_CELL,
            "function": dtypes_pb2.AstType.AST_FUNCTION,
            "number": dtypes_pb2.AstType.AST_NUMBER,
            "logical": dtypes_pb2.AstType.AST_LOGICAL,
            "text": dtypes_pb2.AstType.AST_TEXT,
        }

        return values[ast_type]

    @staticmethod
    def deserialize_ast_type(proto: dtypes_pb2.AstType) -> dtypes.AstType:
        """Deserialize a Protocol Buffer AstType enum to string format.
        
        Args:
            proto: The Protocol Buffer AstType enum to deserialize.
            
        Returns:
            The corresponding AST type string.
        """
        values: Dict[dtypes_pb2.AstType, dtypes.AstType] = {
            dtypes_pb2.AstType.AST_UNKNOWN: "unknown",
            dtypes_pb2.AstType.AST_BINARY_EXPRESSION: "binary-expression",
            dtypes_pb2.AstType.AST_UNARY_EXPRESSION: "unary-expression",
            dtypes_pb2.AstType.AST_CELL_RANGE: "cell-range",
            dtypes_pb2.AstType.AST_CELL: "cell",
            dtypes_pb2.AstType.AST_FUNCTION: "function",
            dtypes_pb2.AstType.AST_NUMBER: "number",
            dtypes_pb2.AstType.AST_LOGICAL: "logical",
            dtypes_pb2.AstType.AST_TEXT: "text",
        }

        return values[proto]

    @staticmethod
    def serialize_ref_type(ref_type: dtypes.RefType) -> dtypes_pb2.RefType:
        """Serialize a RefType string to Protocol Buffer enum format.
        
        Args:
            ref_type: The reference type string to serialize.
            
        Returns:
            The corresponding Protocol Buffer RefType enum value.
        """
        values: Dict[dtypes.RefType, dtypes_pb2.RefType] = {
            "unknown": dtypes_pb2.RefType.REF_UNKNOWN,
            "relative": dtypes_pb2.RefType.REF_RELATIVE,
            "absolute": dtypes_pb2.RefType.REF_ABSOLUTE,
            "mixed": dtypes_pb2.RefType.REF_MIXED,
        }

        return values[ref_type]

    @staticmethod
    def deserialize_ref_type(proto: dtypes_pb2.RefType) -> dtypes.RefType:
        """Deserialize a Protocol Buffer RefType enum to string format.
        
        Args:
            proto: The Protocol Buffer RefType enum to deserialize.
            
        Returns:
            The corresponding reference type string.
        """
        values: Dict[dtypes_pb2.RefType, dtypes.RefType] = {
            dtypes_pb2.RefType.REF_UNKNOWN: "unknown",
            dtypes_pb2.RefType.REF_RELATIVE: "relative",
            dtypes_pb2.RefType.REF_ABSOLUTE: "absolute",
            dtypes_pb2.RefType.REF_MIXED: "mixed",
        }

        return values[proto]

    @staticmethod
    def serialize_ast(ast: dtypes.AST) -> dtypes_pb2.AST:
        """Serialize an AST dictionary to Protocol Buffer format.
        
        Args:
            ast: The AST dictionary to serialize.
            
        Returns:
            The serialized Protocol Buffer AST message.
        """
        proto = dtypes_pb2.AST(
            type=DTypesSerde.serialize_ast_type(ast["type"]),
            operator=ast["operator"],  # Could be None
            left=DTypesSerde.serialize_ast(ast["left"]) if ast["left"] else None,
            right=DTypesSerde.serialize_ast(ast["right"]) if ast["right"] else None,
            arguments=(
                list(map(DTypesSerde.serialize_ast, ast["arguments"]))
                if ast["arguments"]
                else None
            ),
            name=ast["name"],  # Could be None
            refType=(
                DTypesSerde.serialize_ref_type(ast["refType"])
                if ast["refType"]
                else None
            ),
            key=ast["key"],  # Could be None
            operand=(
                DTypesSerde.serialize_ast(ast["operand"]) if ast["operand"] else None
            ),
        )

        if ast["value"] is not None:
            if isinstance(ast["value"], float):
                proto.value.number_value = ast["value"]
            elif isinstance(ast["value"], str):
                proto.value.text_value = ast["value"]
            elif isinstance(ast["value"], bool):
                proto.value.logical_value = ast["value"]

        return proto

    @staticmethod
    def deserialize_ast(proto: dtypes_pb2.AST) -> dtypes.AST:
        """Deserialize a Protocol Buffer AST to dictionary format.
        
        Args:
            proto: The Protocol Buffer AST message to deserialize.
            
        Returns:
            The deserialized AST dictionary.
        """
        response = dtypes.AST(
            type=DTypesSerde.deserialize_ast_type(proto.type),
            operator=proto.operator if proto.HasField("operator") else None,
            left=(
                DTypesSerde.deserialize_ast(proto.left)
                if proto.HasField("left")
                else None
            ),
            right=(
                DTypesSerde.deserialize_ast(proto.right)
                if proto.HasField("right")
                else None
            ),
            arguments=(
                list(map(DTypesSerde.deserialize_ast, proto.arguments))
                if proto.HasField("arguments")
                else None
            ),
            name=proto.name if proto.HasField("name") else None,
            refType=(
                DTypesSerde.deserialize_ref_type(proto.refType)
                if proto.HasField("refType")
                else None
            ),
            key=proto.key if proto.HasField("key") else None,
            operand=(
                DTypesSerde.deserialize_ast(proto.operand)
                if proto.HasField("operand")
                else None
            ),
        )

        if proto.HasField("number_value"):
            response["value"] = proto.number_value
        elif proto.HasField("text_value"):
            response["value"] = proto.text_value
        elif proto.HasField("logical_value"):
            response["value"] = proto.logical_value
        else:
            response["value"] = None

        return response

    @staticmethod
    def serialize_token(token: dtypes.Token) -> dtypes_pb2.Tokens.Token:
        """Serialize a Token dictionary to Protocol Buffer format.
        
        Args:
            token: The token dictionary to serialize.
            
        Returns:
            The serialized Protocol Buffer Token message.
        """
        return dtypes_pb2.Tokens.Token(
            value=token["value"],
            type=token["type"],
            subtype=token["subtype"],
        )

    @staticmethod
    def deserialize_token(proto: dtypes_pb2.Tokens.Token) -> dtypes.Token:
        """Deserialize a Protocol Buffer Token to dictionary format.
        
        Args:
            proto: The Protocol Buffer Token message to deserialize.
            
        Returns:
            The deserialized token dictionary.
        """
        return dtypes.Token(
            value=proto.value,
            type=proto.type,
            subtype=proto.subtype,
        )

    @staticmethod
    def serialize_tokens(tokens: dtypes.Tokens) -> dtypes_pb2.Tokens:
        """Serialize a Tokens dictionary to Protocol Buffer format.
        
        Args:
            tokens: The tokens dictionary to serialize.
            
        Returns:
            The serialized Protocol Buffer Tokens message.
        """
        return dtypes_pb2.Tokens(
            tokens=list(map(DTypesSerde.serialize_token, tokens["tokens"]))
        )

    @staticmethod
    def deserialize_tokens(proto: dtypes_pb2.Tokens) -> dtypes.Tokens:
        """Deserialize a Protocol Buffer Tokens to dictionary format.
        
        Args:
            proto: The Protocol Buffer Tokens message to deserialize.
            
        Returns:
            The deserialized tokens dictionary.
        """
        return dtypes.Tokens(
            tokens=list(map(DTypesSerde.deserialize_token, proto.tokens))
        )
