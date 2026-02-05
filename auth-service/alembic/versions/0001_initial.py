"""Initial

Revision ID: 0001
Revises:
Create Date: 2025-04-01 19:54:02.051160

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

create_refresh_updated_at_func = """
    CREATE FUNCTION {schema}.refresh_updated_at()
    RETURNS TRIGGER
    LANGUAGE plpgsql AS
    $func$
    BEGIN
       NEW.updated_at := now();
       RETURN NEW;
    END
    $func$;
    """


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute("CREATE SCHEMA IF NOT EXISTS auth;")
    op.execute(sa.text(create_refresh_updated_at_func.format(schema="auth")))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(sa.text("DROP FUNCTION auth.refresh_updated_at() CASCADE"))
    op.execute("DROP SCHEMA IF EXISTS auth;")
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp";')
