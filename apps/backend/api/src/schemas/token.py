"""Token schemas module.

This module contains Pydantic models for JWT token handling and authentication.
It defines the structure for token payloads and token responses used in the
authentication system.

The module includes:
- TokenPayload: JWT token payload structure
- Token: Authentication token response model
"""

from pydantic import BaseModel

from src.schemas.users import Roles


class TokenPayload(BaseModel):
    """JWT token payload model.

    Defines the structure of data contained within JWT tokens.
    This payload is encoded into the token and used for user
    identification and authorization.

    Attributes:
        username: User's unique identifier
        rol: User's role for permission validation
    """

    username: str
    rol: Roles


class Token(BaseModel):
    """Authentication token response model.

    Standard structure for token responses returned after successful
    authentication. Contains the JWT access token and token type
    information for API client usage.

    Attributes:
        access_token: JWT access token string
        token_type: Type of token (defaults to "bearer")
    """

    access_token: str
    token_type: str = "bearer"
