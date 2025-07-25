"""add_initial_roles_and_admin

Revision ID: 916f32c12b51
Revises: 42c1c159fae2
Create Date: 2025-07-24 11:51:25.405958

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from datetime import datetime
from app.auth import get_password_hash


# revision identifiers, used by Alembic.
revision: str = "916f32c12b51"
down_revision: Union[str, Sequence[str], None] = "42c1c159fae2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    roles_table = sa.table(
        "roles",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
    )
    op.bulk_insert(
        roles_table,
        [
            {"id": 1, "name": "admin"},
            {"id": 2, "name": "user"},
        ],
    )

    permissions_table = sa.table(
        "permissions",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("role_id", sa.Integer),
    )
    op.bulk_insert(
        permissions_table,
        [
            {"id": 1, "name": "manage_users", "role_id": 1},
            {"id": 2, "name": "view_dashboard", "role_id": 2},
        ],
    )

    users_table = sa.table(
        "users",
        sa.column("email", sa.String),
        sa.column("hashed_password", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("first_name", sa.String),
        sa.column("last_name", sa.String),
        sa.column("created_at", sa.String),
        sa.column("role_id", sa.Integer),
    )
    op.bulk_insert(
        users_table,
        [
            {
                "email": "admin@example.com",
                "hashed_password": get_password_hash("AdminPass123!"),
                "is_active": True,
                "first_name": "Admin",
                "last_name": "Super",
                "role_id": 1,
            }
        ],
    )


def downgrade():
    op.execute("DELETE FROM users")
    op.execute("DELETE FROM permissions")
    op.execute("DELETE FROM roles")
