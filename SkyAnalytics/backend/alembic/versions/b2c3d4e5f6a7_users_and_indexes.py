"""users table and pasajeros analytics indexes

Revision ID: b2c3d4e5f6a7
Revises: 8a0b12b5709c
Create Date: 2026-05-11

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "8a0b12b5709c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = inspect(conn)
    if "users" not in insp.get_table_names():
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("hashed_password", sa.String(length=255), nullable=False),
            sa.Column("full_name", sa.String(length=255), nullable=True),
            sa.Column("role", sa.String(length=32), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email"),
        )
        op.create_index("ix_users_email", "users", ["email"], unique=False)

    # Índices para filtros típicos del dashboard (PostgreSQL)
    op.execute("CREATE INDEX IF NOT EXISTS ix_pasajeros_pais ON pasajeros (pais)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_pasajeros_fecha_registro ON pasajeros (fecha_registro)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_pasajeros_id_asc ON pasajeros (id)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_pasajeros_id_asc")
    op.execute("DROP INDEX IF EXISTS ix_pasajeros_fecha_registro")
    op.execute("DROP INDEX IF EXISTS ix_pasajeros_pais")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
