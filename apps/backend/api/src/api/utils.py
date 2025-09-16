import src.schemas as schemas
from src.core.config import settings

from proto_utils.database import dtypes
from src.core.database_client import database_client


# TODO: Improve this function to use a more robust method of checking superuser status
def is_superuser(username: schemas.models.UserRoles) -> bool:
    """
    Check if the user is a superuser.

    Args:
        username (schemas.models.UserRoles): User roles object containing username and role.

    Returns:
        bool: True if the user is a superuser, False otherwise.
    """
    return username.username == settings.FIRST_SUPERUSER


def invalidate_user_cache(username: str = "", invalidate_lists: bool = False) -> None:
    """
    Invalidate user cache based on the username and whether to invalidate lists.

    Args:
        username (str): The username of the user.
        invalidate_lists (bool): Whether to invalidate all user lists.
    """
    patterns_to_delete = []

    if username:
        patterns_to_delete.append(f"{username}:user_info")
        patterns_to_delete.append(f"*:user_info:{username}:*")
        patterns_to_delete.append(f"{username}:user_info:*")

    if invalidate_lists:
        patterns_to_delete.append("all_users:*")

    for pattern in patterns_to_delete:
        keys = database_client.redis_get_keys(
            dtypes.RedisGetKeysRequest(pattern=pattern)
        )["keys"]
        database_client.redis_delete(dtypes.RedisDeleteRequest(keys=keys))
