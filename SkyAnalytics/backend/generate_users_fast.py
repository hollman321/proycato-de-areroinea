"""
Script para generar 10,000,000 de usuarios usando COPY para máxima velocidad.
"""

import io
import time
import hashlib
from datetime import datetime
from faker import Faker
import psycopg2

# ============== CONFIGURACIÓN ==============
NUM_USERS = 10_000_000
BATCH_SIZE = 100_000
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "skyanalytics",
    "user": "admin",
    "password": "secretpassword",
}
# ===========================================

fake = Faker(["es_ES", "en_US", "pt_BR", "fr_FR"])


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def generate_hashed_password(password: str = "SkyAnalytics2024!") -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_email(index: int) -> str:
    first = fake.first_name().lower()
    last = fake.last_name().lower()
    domains = [
        "skyair.com",
        "aerolineas.net",
        "flytravel.com",
        "skymiles.org",
        "aviator.com",
        "cloudfly.com",
        "jetstream.net",
        "airpilot.org",
        "wingspan.com",
        "horizonair.net",
        "pacificaero.com",
        "globalfly.net",
    ]
    return f"{first}.{last}{index}@{fake.random_element(domains)}"


def get_max_user_id() -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(MAX(id), 0) FROM users")
            return cur.fetchone()[0]


def generate_batch_csv(start_id: int, count: int) -> io.StringIO:
    hashed_pw = generate_hashed_password()
    roles = ["analyst", "viewer", "support", "finance_manager", "marketing_manager"]
    output = io.StringIO()

    for i in range(count):
        user_id = start_id + i
        email = generate_email(user_id)
        first_name = fake.first_name()
        last_name = fake.last_name()
        full_name = f"{first_name} {last_name}"
        role = fake.random_element(roles)
        tenant_id = 1  # Solo existe el tenant Default Tenant (id=1)
        is_active = "true"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        output.write(
            f"{user_id}\t{email}\t{hashed_pw}\t{full_name}\t{role}\t{tenant_id}\t{is_active}\t{now}\t{now}\n"
        )

    output.seek(0)
    return output


def main():
    print(f"🚀 Iniciando generación de {NUM_USERS:,} usuarios...")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users")
            existing = cur.fetchone()[0]
    print(f"📊 Usuarios existentes: {existing:,}")

    if existing >= NUM_USERS:
        print(f"✅ Ya existen {existing:,} usuarios.")
        return

    users_to_generate = NUM_USERS - existing
    start_id = get_max_user_id() + 1
    hashed_pw = generate_hashed_password()

    print(f"📝 Generando {users_to_generate:,} usuarios...")
    print(f"📝 Usando método COPY (máxima velocidad)")

    start_time = time.time()
    total_inserted = 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            for batch_num in range(0, users_to_generate, BATCH_SIZE):
                batch_start = time.time()
                current_batch = min(BATCH_SIZE, users_to_generate - batch_num)

                csv_file = generate_batch_csv(start_id + batch_num, current_batch)

                cur.copy_from(
                    csv_file,
                    "users",
                    columns=(
                        "id",
                        "email",
                        "hashed_password",
                        "full_name",
                        "role",
                        "tenant_id",
                        "is_active",
                        "created_at",
                        "updated_at",
                    ),
                    sep="\t",
                )
                conn.commit()

                total_inserted += current_batch
                batch_time = time.time() - batch_start
                total_time = time.time() - start_time
                progress = total_inserted / users_to_generate * 100
                rate = current_batch / batch_time if batch_time > 0 else 0

                print(
                    f"  Lote {batch_num // BATCH_SIZE + 1}: {current_batch:,} usuarios "
                    f"({progress:.1f}%) - {batch_time:.1f}s - Rate: {rate:,.0f}/s - Total: {total_time:.1f}s"
                )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users")
            total = cur.fetchone()[0]

    print(f"\n✅ ¡Proceso completado!")
    print(f"   Total usuarios en BD: {total:,}")
    print(f"   Tiempo total: {time.time() - start_time:.1f} segundos")


if __name__ == "__main__":
    main()
