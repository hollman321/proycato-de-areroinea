"""Tabla airports (referencia IATA/OurAirports) e índice compuesto pasajeros.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "airports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_row_id", sa.String(length=32), nullable=True),
        sa.Column("iata_code", sa.String(length=3), nullable=True),
        sa.Column("icao_code", sa.String(length=4), nullable=True),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("city", sa.String(length=200), nullable=True),
        sa.Column("country_iso", sa.String(length=2), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("airport_type", sa.String(length=50), nullable=True),
        sa.Column("data_source", sa.String(length=64), nullable=False, server_default="ourairports"),
        sa.Column("raw_keywords", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_row_id"),
    )
    op.create_index("ix_airports_iata_code", "airports", ["iata_code"])
    op.create_index("ix_airports_icao_code", "airports", ["icao_code"])
    op.create_index("ix_airports_country_iso", "airports", ["country_iso"])
    op.create_index("ix_airports_city", "airports", ["city"])
    op.execute(
        """
        CREATE UNIQUE INDEX uq_airports_iata_when_present ON airports (iata_code)
        WHERE iata_code IS NOT NULL AND btrim(iata_code) <> '';
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_pasajeros_pais_fecha ON pasajeros (pais, fecha_registro);"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_pasajeros_pais_fecha;")
    op.execute("DROP INDEX IF EXISTS uq_airports_iata_when_present;")
    op.drop_index("ix_airports_city", table_name="airports")
    op.drop_index("ix_airports_country_iso", table_name="airports")
    op.drop_index("ix_airports_icao_code", table_name="airports")
    op.drop_index("ix_airports_iata_code", table_name="airports")
    op.drop_table("airports")
