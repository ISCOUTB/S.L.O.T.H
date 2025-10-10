"""Model schemas module.

This module contains Pydantic models that correspond to database entities.
These models are used for data validation and serialization when interacting
with the database layer, providing a clean interface between the application
logic and data persistence.

The module includes:
- UserInfo: User personal information model
- UserRoles: User authentication and role management model
"""

from typing import Optional
from pydantic import BaseModel
from src.schemas.users import Sex, Roles


class UserInfo(BaseModel):
    """User personal information model.

    Database model for storing user personal information. This model
    corresponds to the user_info table and contains all personal data
    associated with a user account.

    Attributes:
        username: Unique identifier for the user
        name: User's first name (optional)
        surname: User's last name (optional)
        sex: User's sex/gender designation (optional)
        phone: User's contact phone number (optional)
        email: User's email address (optional)

    Config:
        from_attributes: Enables creation from ORM model attributes
    """

    username: str
    name: Optional[str] = None
    surname: Optional[str] = None
    sex: Optional[Sex] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


class UserRoles(BaseModel):
    """User roles and authentication model.

    Database model for storing user authentication information and role
    assignments. This model corresponds to the user_roles table and handles
    user credentials, permissions, and account status.

    Attributes:
        username: Unique identifier for the user
        rol: User's assigned role in the system (admin or user)
        password: Hashed password for user authentication
        is_active: Whether the user account is currently active
        inactivity: Reason for account inactivity (optional)

    Config:
        from_attributes: Enables creation from ORM model attributes
    """

    username: str
    rol: Roles  # type: ignore
    password: str
    is_active: bool = True
    inactivity: str | None = None

    class Config:
        from_attributes = True
