import uuid

from sqlalchemy import (
    UUID,
    CheckConstraint,
    Column,
    DateTime,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import relationship

from src.core.database_sql import BaseModel
from src.models.dtypes import Status, UserRole, status_enum, user_role_enum
from src.utils import utc_now


class User(BaseModel):
    __tablename__ = "user"
    __table_args__ = (
        Index("idx_user_name", "name"),
        Index("idx_user_email", "email"),
        Index("idx_user_role", "role"),
        Index("idx_user_status", "status"),
        UniqueConstraint("email", name="uq_user_email"),
        CheckConstraint(
            r"email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'",
            name="ck_user_email_format",
        ),
        {"schema": "public"},
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=lambda: uuid.uuid4(),
        nullable=False,
    )
    name = Column(String, default=None, nullable=False)
    email = Column(String, default=None, nullable=False)
    role = Column(user_role_enum, default=UserRole.USER, nullable=False)
    status = Column(status_enum, default=Status.ACTIVE, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=None,
        nullable=False,
        server_default=text("NOW()"),
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=None,
        nullable=False,
        server_default=text("NOW()"),
        onupdate=utc_now,
    )

    # When we implement oauth2, this field could be nullable
    # and, in that case, we should do the migration to make it nullable
    password = Column(String, default=None, nullable=False)

    # Relationships
    projects = relationship("UserProject", back_populates="user", uselist=True)

    # Uploaded tasks
    upload_tasks = relationship("UploadTask", back_populates="user", uselist=True)
