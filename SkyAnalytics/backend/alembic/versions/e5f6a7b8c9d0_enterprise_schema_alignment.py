"""align enterprise schema with current models

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-05-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _tables() -> set[str]:
    return set(inspect(op.get_bind()).get_table_names())


def _columns(table_name: str) -> set[str]:
    return {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def _foreign_keys(table_name: str) -> set[str]:
    return {fk["name"] for fk in inspect(op.get_bind()).get_foreign_keys(table_name)}


def upgrade() -> None:
    tables = _tables()

    if "tenants" not in tables:
        op.create_table(
            "tenants",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.String(length=150), nullable=False),
            sa.Column("slug", sa.String(length=80), nullable=False),
            sa.Column("region", sa.String(length=32), nullable=False, server_default="global"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name"),
            sa.UniqueConstraint("slug"),
        )
        op.create_index("ix_tenants_slug", "tenants", ["slug"])

    op.execute(
        """
        INSERT INTO tenants (id, name, slug, region, is_active, created_at)
        VALUES (1, 'Global Tenant', 'global', 'global', true, NOW())
        ON CONFLICT (id) DO NOTHING
        """
    )

    if "users" in _tables() and "tenant_id" not in _columns("users"):
        op.add_column(
            "users",
            sa.Column("tenant_id", sa.Integer(), nullable=False, server_default="1"),
        )
        op.execute("UPDATE users SET tenant_id = 1 WHERE tenant_id IS NULL")
        if "fk_users_tenant_id_tenants" not in _foreign_keys("users"):
            op.create_foreign_key(
                "fk_users_tenant_id_tenants",
                "users",
                "tenants",
                ["tenant_id"],
                ["id"],
            )
        op.alter_column("users", "tenant_id", server_default=None)

    tables = _tables()
    if "transacciones" not in tables:
        op.create_table(
            "transacciones",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("pasajero_id", sa.Integer(), nullable=False),
            sa.Column("monto", sa.Float(), nullable=False),
            sa.Column("millas_ganadas", sa.Integer(), nullable=True),
            sa.Column("descripcion", sa.String(), nullable=True),
            sa.Column("fecha_transaccion", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["pasajero_id"], ["pasajeros.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_transacciones_pasajero_id", "transacciones", ["pasajero_id"])

    if "millas_acumuladas" not in tables:
        op.create_table(
            "millas_acumuladas",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("pasajero_id", sa.Integer(), nullable=False),
            sa.Column("millas_totales", sa.Integer(), nullable=True),
            sa.Column("dinero_gastado", sa.Float(), nullable=True),
            sa.Column("fecha_actualizado", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["pasajero_id"], ["pasajeros.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("pasajero_id"),
        )

    if "alerts" not in tables:
        op.create_table(
            "alerts",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("tenant_id", sa.Integer(), nullable=False),
            sa.Column("module", sa.String(length=64), nullable=False),
            sa.Column("severity", sa.String(length=16), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("description", sa.String(length=500), nullable=True),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("source", sa.String(length=64), nullable=True),
            sa.Column("metadata", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("resolved_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if "audit_logs" not in tables:
        op.create_table(
            "audit_logs",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("tenant_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("module", sa.String(length=64), nullable=False),
            sa.Column("action", sa.String(length=128), nullable=False),
            sa.Column("metadata", sa.JSON(), nullable=True),
            sa.Column("ip_address", sa.String(length=45), nullable=True),
            sa.Column("session_id", sa.String(length=128), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if "ai_recommendations" not in tables:
        op.create_table(
            "ai_recommendations",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("tenant_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("module", sa.String(length=64), nullable=False),
            sa.Column("confidence", sa.String(length=16), nullable=False),
            sa.Column("impact_score", sa.Integer(), nullable=False),
            sa.Column("payload", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("applied_at", sa.DateTime(), nullable=True),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if "workflow_templates" not in tables:
        op.create_table(
            "workflow_templates",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("tenant_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("trigger", sa.String(length=80), nullable=False),
            sa.Column("actions", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if "workflow_executions" not in tables:
        op.create_table(
            "workflow_executions",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("workflow_id", sa.String(length=64), nullable=False),
            sa.Column("tenant_id", sa.Integer(), nullable=False),
            sa.Column("trigger_source", sa.String(length=80), nullable=False),
            sa.Column("executed_by", sa.Integer(), nullable=True),
            sa.Column("context", sa.JSON(), nullable=True),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("result", sa.JSON(), nullable=True),
            sa.Column("started_at", sa.DateTime(), nullable=False),
            sa.Column("finished_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["workflow_id"], ["workflow_templates.id"]),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.ForeignKeyConstraint(["executed_by"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    for table_name in (
        "workflow_executions",
        "workflow_templates",
        "ai_recommendations",
        "audit_logs",
        "alerts",
        "millas_acumuladas",
        "transacciones",
    ):
        if table_name in _tables():
            op.drop_table(table_name)

    if "users" in _tables() and "tenant_id" in _columns("users"):
        if "fk_users_tenant_id_tenants" in _foreign_keys("users"):
            op.drop_constraint("fk_users_tenant_id_tenants", "users", type_="foreignkey")
        op.drop_column("users", "tenant_id")

    if "tenants" in _tables():
        op.drop_index("ix_tenants_slug", table_name="tenants")
        op.drop_table("tenants")
