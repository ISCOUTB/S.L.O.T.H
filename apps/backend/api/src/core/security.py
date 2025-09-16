from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from src.core.config import settings
from src.schemas.users import Roles

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def create_access_token(username: str, rol: Roles, expires_delta: timedelta) -> str:
    """
    Generates an access token (JWT) for a user.

    Args:
        username (str): User's document number.
        rol (str): User's role (e.g. administrator, doctor).
        expires_delta (datetime.timedelta): Token duration before it expires.

    Returns:
        str: Generated JWT token.
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "username": username, "rol": rol}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if a plain text password matches its hash.

    Args:
        plain_password (str): Plain text password to verify.
        hashed_password (str): Encrypted password (hash) to compare against.

    Returns:
        bool: True if passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generates an encrypted hash of a plain text password.

    Args:
        password (str): Plain text password to encrypt.

    Returns:
        str: Encrypted hash of the password.
    """
    return pwd_context.hash(password)
