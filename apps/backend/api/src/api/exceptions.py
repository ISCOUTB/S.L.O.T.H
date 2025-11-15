"""
Centralized exception handling for external service errors.
"""

import grpc
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pika.exceptions import (
    AMQPChannelError,
    AMQPConnectionError,
    AMQPError,
    StreamLostError,
)


async def grpc_exception_handler(request: Request, exc: grpc.RpcError) -> JSONResponse:
    """Handle gRPC errors with appropriate HTTP status codes."""

    # Map gRPC status codes to HTTP status codes
    status_code_mapping = {
        grpc.StatusCode.UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
        grpc.StatusCode.DEADLINE_EXCEEDED: status.HTTP_504_GATEWAY_TIMEOUT,
        grpc.StatusCode.CANCELLED: status.HTTP_503_SERVICE_UNAVAILABLE,
        grpc.StatusCode.INVALID_ARGUMENT: status.HTTP_400_BAD_REQUEST,
        grpc.StatusCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
        grpc.StatusCode.ALREADY_EXISTS: status.HTTP_409_CONFLICT,
        grpc.StatusCode.PERMISSION_DENIED: status.HTTP_403_FORBIDDEN,
        grpc.StatusCode.UNAUTHENTICATED: status.HTTP_401_UNAUTHORIZED,
    }

    grpc_code = exc.code()
    http_status = status_code_mapping.get(
        grpc_code, status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    return JSONResponse(
        status_code=http_status,
        content={
            "error": "Database service error",
            "code": grpc_code.name,
            "message": exc.details(),
            "path": str(request.url.path),
        },
    )


async def rabbitmq_exception_handler(request: Request, exc: AMQPError) -> JSONResponse:
    """Handle RabbitMQ errors."""
    status_code_mapping = {
        AMQPConnectionError: status.HTTP_503_SERVICE_UNAVAILABLE,
        StreamLostError: status.HTTP_504_GATEWAY_TIMEOUT,
        AMQPChannelError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }

    http_status = status_code_mapping.get(
        type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    return JSONResponse(
        status_code=http_status,
        content={
            "error": "Message broker service unavailable",
            "message": str(exc),
            "path": str(request.url.path),
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": str(request.url.path),
        },
    )
