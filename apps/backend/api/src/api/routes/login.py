from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm

from src.api.deps import CurrentUser, SessionDep
from src.core.config import settings
from src.core.security import create_access_token

from src import schemas
from src.controllers.users import ControllerUsers

router = APIRouter()


@router.post("/access-token")
async def login_access_token(
    db: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    rol: Annotated[schemas.users.Roles, Body()],
) -> schemas.token.Token:
    user_login = schemas.users.LoginUser(
        username=form_data.username, password=form_data.password, rol=rol
    )

    user = ControllerUsers.authenticate_user(user_login, db)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Username or password is incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        username=user.username,
        rol=user.rol,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return schemas.token.Token(access_token=access_token, token_type="bearer")


@router.get("/test-token")
async def test_token(current_user: CurrentUser) -> schemas.models.UserRoles:
    return current_user