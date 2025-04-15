"""Add users table

Revision ID: 0002
Revises: 0001
Create Date: 2025-04-11 21:53:07.375338

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

create_trigger = """
    CREATE TRIGGER trig_{table}_updated BEFORE UPDATE ON {schema}.{table}
    FOR EACH ROW EXECUTE PROCEDURE {schema}.refresh_updated_at();
    """

drop_trigger = """
    DROP TRIGGER trig_{table}_updated ON {schema}.{table};
"""


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("email", sa.String(length=128), nullable=False),
        sa.Column("username", sa.String(length=256), nullable=False),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="auth",
    )
    op.create_index(
        op.f("ix_auth_users_created_at"),
        "users",
        ["created_at"],
        unique=False,
        schema="auth",
    )
    op.create_index(
        op.f("ix_auth_users_email"), "users", ["email"], unique=True, schema="auth"
    )
    op.create_index(
        op.f("ix_auth_users_is_admin"),
        "users",
        ["is_admin"],
        unique=False,
        schema="auth",
    )
    op.create_index(
        op.f("ix_auth_users_username"),
        "users",
        ["username"],
        unique=False,
        schema="auth",
    )
    op.execute(sa.text(create_trigger.format(schema="auth", table="users")))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(sa.text(drop_trigger.format(schema="auth", table="users")))
    op.drop_index(op.f("ix_auth_users_username"), table_name="users", schema="auth")
    op.drop_index(op.f("ix_auth_users_is_admin"), table_name="users", schema="auth")
    op.drop_index(op.f("ix_auth_users_email"), table_name="users", schema="auth")
    op.drop_index(op.f("ix_auth_users_created_at"), table_name="users", schema="auth")
    op.drop_table("users", schema="auth")
