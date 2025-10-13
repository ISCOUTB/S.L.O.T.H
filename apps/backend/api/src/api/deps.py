from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.orm import Session

from proto_utils.database.base_client import DatabaseClient

from src.core import security
from src.core.config import settings
from src.core.database_sql import SessionLocal

import src.schemas as schemas
from src.controllers.users import ControllerUsers

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db_client() -> Generator[DatabaseClient, None, None]:
    db_client = DatabaseClient(settings.DATABASE_CONNECTION_CHANNEL)
    try:
        yield db_client
    finally:
        db_client.close()


def get_sql_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_sql_db)]
TokenDep = Annotated[Session, Depends(reusable_oauth2)]


def get_current_user(db: SessionDep, token: TokenDep) -> schemas.models.UserRoles:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.token.TokenPayload(
            username=payload.get("username"), rol=payload.get("rol")
        )
    except ValidationError:
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_search = schemas.users.SearchUser(
        username=token_data.username, rol=token_data.rol
    )

    user = ControllerUsers.get_user_rol(user_search, db)
    if user is None:
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "bearer"},
        )

    return schemas.models.UserRoles.model_validate(user)


CurrentUser = Annotated[schemas.models.UserRoles, Depends(get_current_user)]


def get_current_admin(current_user: CurrentUser) -> schemas.models.UserRoles | None:
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized access, admin role required.",
        )

    return current_user


Admin = Annotated[schemas.models.UserRoles, Depends(get_current_admin)]
