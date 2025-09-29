"""gRPC Messaging Proxy Server Package.

This package implements a lightweight gRPC server that acts as a proxy between
RabbitMQ message queues and the Typechecking microservice in the ETL Design system.

Modules:
    server: Main gRPC server implementation with streaming endpoints
    core: Configuration management and connection parameters
    handlers: gRPC request handlers and business logic coordination
    services: Business logic services for parameter and routing management
    utils: Logging and utility functions

The package provides a complete messaging proxy solution that abstracts
RabbitMQ complexity behind a clean gRPC interface, enabling real-time
message streaming and configuration management for distributed services.

Key Features:
    - Real-time message streaming from RabbitMQ queues
    - Connection parameter distribution to client services
    - Routing key management for different message types
    - Comprehensive logging and error handling
    - Configurable via environment variables

Architecture:
    API Service → RabbitMQ → Messaging Server (this) → Typechecking Service

Usage:
    Run the server directly:
        python -m src.server

    Or import for testing:
        from src.server import MessagingServicer
"""
