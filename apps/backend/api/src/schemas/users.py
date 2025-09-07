"""User schemas module.

This module contains Pydantic models and type definitions for user-related
data structures used throughout the application. It defines various user
schemas for different operations like creation, updates, authentication,
and search functionality.

The module includes:
- Type definitions for user roles and sex
- Base user model with common fields
- Specialized user models for different operations
- Output schema for API responses
"""

from pydantic import BaseModel
from typing import Literal, Optional, TypedDict

# Type definitions
Roles = Literal["admin", "user"]
"""
User role types.

Defines the available roles in the system:
- admin: Administrative user with elevated privileges
- user: Regular user with standard permissions
"""

Sex = Literal["M", "F", "O", "N", "U", "X"]
"""
Sex/Gender type definition.

Defines the available sex/gender options:
- M: Male
- F: Female
- O: Other
- N: Not specified
- U: Unknown
- X: Prefer not to say
"""


class RolesInfo(TypedDict):
    """
    Role information structure.

    TypedDict defining the structure for role information including
    the role type and its active status.

    Attributes:
        rol: The user's role (admin or user)
        is_active: Whether the role is currently active
    """

    rol: Roles
    is_active: bool


class BaseUser(BaseModel):
    """
    Base user model with common fields.

    Contains the fundamental user information fields that are shared
    across different user schemas. This serves as the foundation for
    other user-related models.

    Attributes:
        username: Unique identifier for the user
        name: User's first name (optional)
        surname: User's last name (optional)
        sex: User's sex/gender (optional)
        phone: User's phone number (optional)
        email: User's email address (optional)
    """

    username: str
    name: Optional[str] = None
    surname: Optional[str] = None
    sex: Optional[Sex] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class User(BaseUser):
    """
    Standard user model.

    Extends BaseUser with role information. This represents a complete
    user entity with all basic information plus their assigned role.

    Attributes:
        rol: The user's role in the system

    Inherits all attributes from BaseUser:
        username, name, surname, sex, phone, email
    """

    rol: Roles


class LoginUser(BaseModel):
    """
    User login credentials model.

    Schema for user authentication requests. Contains the minimum
    required information for user login validation.

    Attributes:
        username: User's unique identifier
        password: User's password for authentication
        rol: User's role to validate permissions
    """

    username: str
    password: str
    rol: Roles


class SearchUser(BaseModel):
    """
    User search criteria model.

    Schema for searching users in the system. Contains the key
    identifiers used for user lookup operations.

    Attributes:
        username: User's unique identifier to search for
        rol: User's role to filter search results
    """

    username: str
    rol: Roles


class CreateUser(User):
    """
    User creation model.

    Extends the User model with password field for user creation.
    Contains all necessary information to create a new user account.

    Attributes:
        password: Plain text password for the new user account

    Inherits all attributes from User and BaseUser:
        username, name, surname, sex, phone, email, rol
    """

    password: str


class UpdateUser(BaseUser):
    """
    User update model.

    Schema for updating existing user information. All fields are
    optional to allow partial updates of user data.

    Attributes:
        username: Unique identifier for the user (optional)
        password: New password for the user (optional)
        rol: New role for the user (optional)

    Inherits all attributes from BaseUser (all optional):
        name, surname, sex, phone, email
    """

    username: Optional[str] = None
    password: Optional[str] = None
    rol: Optional[Roles] = None


class AllUser(BaseUser):
    """
    Complete user model with multiple roles.

    Extends BaseUser with a list of role information. This model
    represents users who may have multiple roles with different
    active states.

    Attributes:
        roles: List of role information including role type and status

    Inherits all attributes from BaseUser:
        username, name, surname, sex, phone, email
    """

    roles: list[RolesInfo]


class Output(TypedDict):
    """
    API response output structure.

    Standard structure for API responses containing operation results
    and status information.

    Attributes:
        number: Numeric result or count from the operation
        message: Descriptive message about the operation result
        status: HTTP status code or operation status indicator
    """

    number: int
    message: str
    status: int
