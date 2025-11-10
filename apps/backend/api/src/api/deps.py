from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from messaging_utils.core.connection_params import messaging_params
from messaging_utils.messaging.publishers import Publisher
from proto_utils.database.base_client import DatabaseClient
from pydantic import ValidationError
from sqlalchemy.orm import Session

import src.schemas as schemas
from src.controllers.users import ControllerUsers
from src.core import security
from src.core.config import settings
from src.core.database_sql import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db_client() -> Generator[DatabaseClient, None, None]:
    db_client = DatabaseClient(
        settings.DATABASE_CONNECTION_CHANNEL,
        max_retries=settings.DATABASE_MAX_RETRIES,
        retry_delay=settings.DATABASE_RETRY_DELAY_SECONDS,
        backoff=settings.DATABASE_BACKOFF_MULTIPLIER,
    )
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


def get_publisher() -> Generator[Publisher, None, None]:
    params = messaging_params.copy()
    exchange_info = params.pop("exchange")

    publisher = Publisher(
        params=params,
        exchange_info=exchange_info,
        max_tries=settings.RABBITMQ_MAX_RETRIES,
        retry_delay=settings.RABBITMQ_RETRY_DELAY_SECONDS,
        backoff=settings.RABBITMQ_BACKOFF_MULTIPLIER,
    )

    try:
        yield publisher
    finally:
        publisher.close()


SessionDep = Annotated[Session, Depends(get_sql_db)]
DatabaseClientDep = Annotated[DatabaseClient, Depends(get_db_client)]
PublisherDep = Annotated[Publisher, Depends(get_publisher)]
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
