"""gRPC request handlers and business logic coordination module.

This module provides handler classes that process gRPC requests for the
messaging service. Handlers act as intermediaries between the gRPC server
layer and the business logic layer, managing serialization/deserialization
and request delegation.

Modules:
    services: Main handler class for all messaging-related gRPC requests

The handlers follow a consistent pattern of deserialization, service delegation,
and response serialization, ensuring clean separation between transport,
serialization, and business logic concerns.
"""
