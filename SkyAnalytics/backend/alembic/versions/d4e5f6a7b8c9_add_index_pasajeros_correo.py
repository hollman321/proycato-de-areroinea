"""add index on pasajeros correo

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-14

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_pasajeros_correo", "pasajeros", ["correo"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_pasajeros_correo", table_name="pasajeros")
