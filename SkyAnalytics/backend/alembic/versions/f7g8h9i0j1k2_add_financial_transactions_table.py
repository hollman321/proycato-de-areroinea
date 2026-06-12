"""Add financial_transactions table

Revision ID: f7g8h9i0j1k2
Revises: e5f6a7b8c9d0
Create Date: 2026-06-01 17:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7g8h9i0j1k2'
down_revision: Union[str, Sequence[str], None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - create financial_transactions table."""
    op.create_table(
        'financial_transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_financial_transactions_date'), 'financial_transactions', ['date'], unique=False)
    op.create_index(op.f('ix_financial_transactions_created_at'), 'financial_transactions', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema - drop financial_transactions table."""
    op.drop_index(op.f('ix_financial_transactions_created_at'), table_name='financial_transactions')
    op.drop_index(op.f('ix_financial_transactions_date'), table_name='financial_transactions')
    op.drop_table('financial_transactions')
