"""Initial migration

Revision ID: 8a0b12b5709c
Revises: 
Create Date: 2026-05-08 13:55:13.051150

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a0b12b5709c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('pasajeros',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nombre_completo', sa.String(), nullable=False),
        sa.Column('correo', sa.String(), nullable=False),
        sa.Column('tarjeta_credito', sa.String(), nullable=False),
        sa.Column('tarjeta_debito', sa.String(), nullable=False),
        sa.Column('direccion', sa.String(), nullable=False),
        sa.Column('ciudad', sa.String(), nullable=False),
        sa.Column('pais', sa.String(), nullable=False),
        sa.Column('fecha_registro', sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('correo')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('pasajeros')
