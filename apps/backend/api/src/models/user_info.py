from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from src.core.database_sql import BaseModel


class UserInfo(BaseModel):
    __tablename__ = "user_info"

    username = Column(String, primary_key=True, nullable=False)
    name = Column(String, default=None, nullable=True)
    surname = Column(String, default=None, nullable=True)
    sex = Column(String(1), default=None, nullable=True)
    phone = Column(String, default=None, nullable=True, unique=True)
    email = Column(String, default=None, nullable=True, unique=True)

    user_roles = relationship(
        "UserRoles",
        uselist=True,
        back_populates="user_info",
        passive_deletes=True,
        passive_updates=True,
    )
