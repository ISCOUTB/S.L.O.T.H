"""Create User Tables

Revision ID: 7dbcdd48ec01
Revises:
Create Date: 2025-09-07 21:15:21.627063

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7dbcdd48ec01"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_info",
        sa.Column("username", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("surname", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("sex", sa.VARCHAR(length=1), autoincrement=False, nullable=True),
        sa.Column("phone", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("email", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("username", name="user_info_pkey"),
        sa.UniqueConstraint(
            "email",
            name="user_info_email_key",
            postgresql_include=[],
            postgresql_nulls_not_distinct=False,
        ),
        sa.UniqueConstraint(
            "phone",
            name="user_info_phone_key",
            postgresql_include=[],
            postgresql_nulls_not_distinct=False,
        ),
        postgresql_ignore_search_path=False,
    )
    op.create_table(
        "user_roles",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("username", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("rol", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("password", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column("inactivity", sa.DATE(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["username"], ["user_info.username"], name=op.f("user_roles_username_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("user_roles_pkey")),
        sa.UniqueConstraint(
            "username",
            "rol",
            name=op.f("unique_user_rol"),
            postgresql_include=[],
            postgresql_nulls_not_distinct=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user_roles")
    op.drop_table("user_info")
