import src.models as models

import re
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from typing import Dict, Optional


def valid_email_format(email: str) -> bool:
    """
    Validates email format without database query.

    Args:
        email (str): Email to validate format.

    Returns:
        bool: True if email format is valid, False otherwise.
    """
    return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email))


def valid_phone_format(phone: str) -> bool:
    """
    Validates phone format without database query.

    Args:
        phone (str): Phone to validate format.

    Returns:
        bool: True if phone format is valid, False otherwise.
    """
    return bool(re.match(r"^\d{3}[-\s]?\d{3}[-\s]?\d{4}$", phone))


def validate_unique_fields(
    db: Session,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    exclude_username: Optional[str] = None,
) -> Dict[str, bool]:
    """
    Validates multiple unique fields in a single database query.

    Args:
        db (Session): Database session.
        email (Optional[str]): Email to validate uniqueness.
        phone (Optional[str]): Phone to validate uniqueness.
        exclude_username (Optional[str]): Username to exclude from validation (for updates).

    Returns:
        Dict[str, bool]: Dictionary with validation results:
            - email_valid: True if email is available
            - phone_valid: True if phone is available
    """
    result = {"email_valid": True, "phone_valid": True}

    if not email and not phone:
        return result

    # Build conditions for the query
    conditions = []

    if email:
        conditions.append(models.user_info.UserInfo.email == email)

    if phone:
        conditions.append(models.user_info.UserInfo.phone == phone)

    # Single query to check all unique fields
    stmt = select(
        models.user_info.UserInfo.username,
        models.user_info.UserInfo.email,
        models.user_info.UserInfo.phone,
    ).where(or_(*conditions))

    # Exclude current user if updating
    if exclude_username:
        stmt = stmt.where(models.user_info.UserInfo.username != exclude_username)

    existing_records = db.execute(stmt).all()

    # Check which fields are taken
    for record in existing_records:
        if email and record.email == email:
            result["email_valid"] = False
        if phone and record.phone == phone:
            result["phone_valid"] = False

    return result


def parse_integrity_error(error: Exception) -> Dict[str, str]:
    """
    Parses SQLAlchemy IntegrityError to identify which constraint was violated.

    Args:
        error (Exception): The IntegrityError exception.

    Returns:
        Dict[str, str]: Dictionary with error details:
            - field: The field that caused the error
            - message: Human-readable error message
    """
    error_str = str(error).lower()

    if "email" in error_str or "user_info_email_key" in error_str:
        return {"field": "email", "message": "Email already exists.", "number": 4}

    if "phone" in error_str or "user_info_phone_key" in error_str:
        return {
            "field": "phone",
            "message": "Phone number already exists.",
            "number": 5,
        }

    if "username" in error_str or "user_info_pkey" in error_str:
        return {"field": "username", "message": "Username already exists.", "number": 3}

    if "unique_user_rol" in error_str:
        return {
            "field": "user_role",
            "message": "User with this role already exists.",
            "number": 2,
        }
    return {
        "field": "unknown",
        "message": "Database constraint violation.",
        "number": 409,
    }
