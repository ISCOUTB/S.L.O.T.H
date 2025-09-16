import json

from fastapi import APIRouter, HTTPException
from src.api.deps import CurrentUser, Admin, SessionDep
from src.api.utils import is_superuser, invalidate_user_cache

from proto_utils.database import dtypes
from src.core.database_client import database_client
from src.controllers.users import ControllerUsers

import src.schemas as schemas

router = APIRouter()


@router.get("/info")
def get_user_info(current_user: CurrentUser, db: SessionDep) -> schemas.users.BaseUser:
    """
    Get current user information.

    Args:
        current_user (CurrentUser): Current user dependency.
        db (SessionDep): Database session dependency.

    Returns:
        BaseUser: Current user information.
    """
    cache_key = f"{current_user.username}:user_info"
    cached_response = database_client.redis_get(dtypes.RedisGetRequest(key=cache_key))
    if cached_response["found"]:
        return schemas.users.BaseUser(**json.loads(cached_response["value"]))

    user = ControllerUsers.get_user(current_user.username, db, active=True, rol=False)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    response = schemas.users.BaseUser.model_validate(user)
    database_client.redis_set(
        dtypes.RedisSetRequest(
            key=cache_key,
            value=json.dumps(response.model_dump()),
            expiration=None,
        )
    )
    return response


@router.get("/search/{username}")
def get_user(
    admin: Admin,
    db: SessionDep,
    username: str,
    all: bool = False,
    active: bool = True,
    use_cache: bool = True,
) -> schemas.users.AllUser | schemas.users.BaseUser:
    """
    Get user information by username and role.

    Args:
        admin (Admin): Admin dependency to check permissions.
        db (SessionDep): Database session dependency.
        username (str): Username of the user to retrieve.
        all (bool): If True, return all user information including roles.
        active (bool): If True, only return active users.

    Returns:
        BaseUser or AllUser: User information based on the request.
    """
    cache_key = f"{admin.username}:user_info:{username}:{active}:{all}"
    cached_response = database_client.redis_get(dtypes.RedisGetRequest(key=cache_key))
    model = schemas.users.AllUser if all else schemas.users.BaseUser
    if cached_response and use_cache:
        return model(**json.loads(cached_response))

    user = ControllerUsers.get_user(username, db, active=active, rol=all)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    response = model.model_validate(user)
    database_client.redis_set(
        dtypes.RedisSetRequest(
            key=cache_key,
            value=json.dumps(response.model_dump()),
            expiration=None,
        )
    )
    return response


@router.get("/search")
def get_all_users(
    _: Admin,
    db: SessionDep,
    active: bool = True,
    rol: bool = False,
    limit: int = 100,
    page: int = 1,
    use_cache: bool = True,
) -> schemas.api.Paginated[schemas.users.AllUser | schemas.users.BaseUser]:
    """
    Get all users with pagination and filtering options.

    Args:
        _: Admin: Admin dependency to check permissions.
        db (SessionDep): Database session dependency.
        active (bool): If True, only return active users.
        rol (bool): If True, include user roles in the response.
        limit (int): Number of users to return per page.
        page (int): Page number for pagination.
        use_cache (bool): If True, use cached response if available.

    Returns:
        schemas.api.Paginated[AllUser | BaseUser]: Paginated list of users.
    """
    cache_key = f"all_users:active={active}:rol={rol}:limit={limit}:page={page}"
    model = schemas.users.AllUser if rol else schemas.users.BaseUser
    cached_response = database_client.redis_get(dtypes.RedisGetRequest(key=cache_key))
    if use_cache and cached_response:
        return json.loads(cached_response)

    users = ControllerUsers.get_users(
        db, active=active, rol=rol, limit=limit, page=page
    )
    response = [model.model_validate(user) for user in users["items"]]
    database_client.redis_set(
        dtypes.RedisSetRequest(
            key=cache_key,
            value=json.dumps(response.model_dump()),
            expiration=None,
        )
    )
    return {**users, "items": response}


@router.post("/create")
def create_user(
    user: schemas.users.CreateUser,
    db: SessionDep,
    admin: Admin,
) -> dtypes.ApiResponse:
    """
    Create a new user.

    Args:
        user (CreateUser): User data to create.
        db (SessionDep): Database session dependency.
        admin (Admin): Admin dependency to check permissions.
    Returns:
        ApiResponse: Response indicating success or error.
    """
    admin_bool = is_superuser(admin)
    response = ControllerUsers.create_user(new_user=user, db=db, admin=admin_bool)

    if response["number"] != 0:
        raise HTTPException(
            status_code=response["status"],
            detail=response["message"],
        )

    invalidate_user_cache(invalidate_lists=True)
    return dtypes.ApiResponse(
        status="success",
        code=response["status"],
        message=response["message"],
        data=user.model_dump(),
    )


@router.patch("/update/{username}")
def update_user(
    username: str,
    user: schemas.users.UpdateUser,
    rol: schemas.users.Roles,
    db: SessionDep,
    admin: Admin,
) -> dtypes.ApiResponse:
    """
    Update user information.

    Args:
        username (str): Username of the user to update.
        user (UpdateUser): User data to update.
        rol (Roles): User roles to update.
        db (SessionDep): Database session dependency.
        admin (Admin): Current user dependency.

    Returns:
        ApiResponse: Response indicating success or error.
    """
    search_user = schemas.users.SearchUser(username=username, rol=rol)
    response = ControllerUsers.update_user(
        search_user=search_user,
        updated_info=user,
        db=db,
        admin=is_superuser(admin),
    )

    if response["number"] != 0:
        raise HTTPException(
            status_code=response["status"],
            detail=response["message"],
        )

    invalidate_user_cache(username=username, invalidate_lists=True)
    return dtypes.ApiResponse(
        status="success",
        code=response["status"],
        message=response["message"],
        data=user.model_dump(exclude_none=True, exclude_unset=True),
    )


@router.delete("/delete/{username}")
def delete_user(
    username: str,
    rol: schemas.users.Roles,
    db: SessionDep,
    admin: Admin,
    complete: bool = False,
) -> dtypes.ApiResponse:
    """
    Delete a user by username.

    Args:
        username (str): Username of the user to delete.
        rol (Roles): User roles to check permissions.
        db (SessionDep): Database session dependency.
        admin (Admin): Current user dependency.
        complete (bool): If True, delete user completely, otherwise just mark as inactive.

    Returns:
        ApiResponse: Response indicating success or error.
    """
    search_user = schemas.users.SearchUser(username=username, rol=rol)
    if complete:
        response = ControllerUsers.delete_completely_user(
            search_user=search_user, db=db, admin=is_superuser(admin)
        )
    else:
        response = ControllerUsers.delete_user(
            search_user=search_user, db=db, admin=is_superuser(admin)
        )

    if response["number"] != 0:
        raise HTTPException(
            status_code=response["status"],
            detail=response["message"],
        )

    invalidate_user_cache(username=username, invalidate_lists=True)
    return dtypes.ApiResponse(
        status="success",
        code=response["status"],
        message=response["message"],
        data={},
    )
