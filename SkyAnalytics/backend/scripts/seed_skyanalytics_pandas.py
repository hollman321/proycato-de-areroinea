"""Carga datos demo de SkyAnalytics en PostgreSQL y aplica las vistas.

Uso desde SkyAnalytics/backend:
    python scripts/seed_skyanalytics_pandas.py

Tambien acepta DATABASE_URL, por ejemplo:
    set DATABASE_URL=postgresql://admin:password@localhost:5432/skyanalytics
"""

from __future__ import annotations

import os
import random
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker
from sqlalchemy import create_engine, text


SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
SQL_FILE = SCRIPT_DIR / "skyanalytics_views.sql"

sys.path.insert(0, str(BACKEND_DIR))

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://admin:password@localhost:5432/skyanalytics"
)
os.environ["DATABASE_URL"] = DATABASE_URL

from database import init_db  # noqa: E402

TARGET_CLIENTES = int(os.getenv("SKY_SEED_CLIENTES", "200"))
TARGET_OPERACIONES = int(os.getenv("SKY_SEED_OPERACIONES", "1200"))
TARGET_LOGS = int(os.getenv("SKY_SEED_LOGS", "250"))

fake = Faker("es_CO")
random.seed(42)
Faker.seed(42)


def utcnow_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def table_count(engine, table_name: str) -> int:
    query = text(f"SELECT COUNT(*) FROM {table_name}")
    with engine.connect() as conn:
        return int(conn.execute(query).scalar() or 0)


def ensure_tenant(engine) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO tenants (id, name, slug, region, is_active, created_at)
                VALUES (1, 'SkyAnalytics Global', 'skyanalytics-global', 'latam', true, NOW())
                ON CONFLICT (id) DO NOTHING
                """
            )
        )


def seed_pasajeros(engine) -> None:
    existentes = table_count(engine, "pasajeros")
    faltantes = max(TARGET_CLIENTES - existentes, 0)
    if faltantes == 0:
        print(f"pasajeros: {existentes} registros existentes")
        return

    ahora = utcnow_naive()
    paises = ["CO", "MX", "PE", "CL", "AR", "US", "ES"]
    rows = []
    for index in range(faltantes):
        seq = existentes + index + 1
        rows.append(
            {
                "nombre_completo": fake.name(),
                "correo": f"cliente.{seq:05d}@skyanalytics.local",
                "tarjeta_credito": f"411111******{random.randint(1000, 9999)}",
                "tarjeta_debito": f"555555******{random.randint(1000, 9999)}",
                "direccion": fake.address().replace("\n", ", "),
                "ciudad": fake.city(),
                "pais": random.choice(paises),
                "fecha_registro": (ahora - timedelta(days=random.randint(1, 730))).date(),
            }
        )

    pd.DataFrame(rows).to_sql("pasajeros", engine, if_exists="append", index=False)
    print(f"pasajeros: +{faltantes} registros")


def seed_operaciones(engine) -> None:
    existentes = table_count(engine, "operaciones")
    faltantes = max(TARGET_OPERACIONES - existentes, 0)
    if faltantes == 0:
        print(f"operaciones: {existentes} registros existentes")
        return

    clientes = pd.read_sql_query("SELECT id FROM pasajeros ORDER BY id", engine)
    if clientes.empty:
        raise RuntimeError("No hay pasajeros para asociar operaciones.")

    estados = ["COMPLETED", "IN_PROGRESS", "PENDING", "CANCELLED"]
    categorias = ["Ticketing", "Carga", "Equipaje", "Upgrade", "Servicios"]
    rows = []
    ahora = utcnow_naive()
    cliente_ids = clientes["id"].tolist()

    for index in range(faltantes):
        seq = existentes + index + 1
        status = random.choices(estados, weights=[58, 22, 14, 6], k=1)[0]
        tipo = random.choices(["INCOME", "EXPENSE"], weights=[88, 12], k=1)[0]
        fecha = ahora - timedelta(days=random.randint(0, 365), hours=random.randint(0, 23))
        rows.append(
            {
                "title": f"SKY-{200 + seq:05d}",
                "description": "Operacion generada para dashboard analitico",
                "client_id": random.choice(cliente_ids),
                "status": status,
                "category": random.choice(categorias),
                "type": tipo,
                "amount": round(random.uniform(120.0, 9200.0), 2),
                "created_at": fecha,
                "updated_at": fecha + timedelta(minutes=random.randint(5, 240)),
            }
        )

    pd.DataFrame(rows).to_sql("operaciones", engine, if_exists="append", index=False)
    print(f"operaciones: +{faltantes} registros")


def seed_audit_logs(engine) -> None:
    existentes = table_count(engine, "audit_logs")
    faltantes = max(TARGET_LOGS - existentes, 0)
    if faltantes == 0:
        print(f"audit_logs: {existentes} registros existentes")
        return

    modulos = ["API Gateway", "PostgreSQL DB", "Operations API", "Analytics Engine"]
    acciones = ["health_check_ok", "query_executed", "operation_synced", "cache_refreshed"]
    ahora = utcnow_naive()
    rows = []

    for index in range(faltantes):
        seq = existentes + index + 1
        rows.append(
            {
                "tenant_id": 1,
                "user_id": None,
                "module": random.choice(modulos),
                "action": random.choice(acciones),
                "metadata": f'{{"source":"pandas","sample_id":{seq}}}',
                "ip_address": "127.0.0.1",
                "session_id": f"pandas-seed-{seq}",
                "created_at": ahora - timedelta(minutes=random.randint(0, 2000)),
            }
        )

    pd.DataFrame(rows).to_sql("audit_logs", engine, if_exists="append", index=False)
    print(f"audit_logs: +{faltantes} registros")


def apply_views(engine) -> None:
    sql = SQL_FILE.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.execute(text(sql))
    print("vistas: vista_resumen_ejecutivo, vista_tendencia_y_operaciones, vista_actividad_reciente_y_sistema")


def main() -> None:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    print(f"Conectando a {DATABASE_URL}")
    init_db()
    ensure_tenant(engine)
    seed_pasajeros(engine)
    seed_operaciones(engine)
    seed_audit_logs(engine)
    apply_views(engine)
    print("Carga finalizada.")


if __name__ == "__main__":
    main()
