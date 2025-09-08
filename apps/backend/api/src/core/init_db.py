import src.schemas as schemas

from src.controllers.users import ControllerUsers

from src.core.config import settings
from src.core.database_sql import SessionLocal

from sqlalchemy.orm import Session


def init_db(db: Session) -> None:
    superuser_search = schemas.users.SearchUser(
        username=settings.FIRST_SUPERUSER, rol="admin"
    )
    user_db = ControllerUsers.get_user_rol(superuser_search, db)

    if user_db is None:
        create_super_user = schemas.users.CreateUser(
            username=settings.FIRST_SUPERUSER,
            rol="admin",
            password=settings.FIRST_SUPERUSER_PASSWORD,
        )

        ControllerUsers.create_user(create_super_user, db, True)


if __name__ == "__main__":
    init_db(SessionLocal())
