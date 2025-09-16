from sqlalchemy import (
    Column,
    Date,
    Integer,
    String,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from src.core.database_sql import BaseModel


class UserRoles(BaseModel):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, ForeignKey("user_info.username"), nullable=False)
    rol = Column(String, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    inactivity = Column(Date, default=None, nullable=True)

    __table_args__ = (UniqueConstraint("username", "rol", name="unique_user_rol"),)

    user_info = relationship(
        "UserInfo",
        uselist=False,
        back_populates="user_roles",
        passive_deletes=True,
        passive_updates=True,
    )
