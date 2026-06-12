"""
Script para generar 100,000 usuarios de plataforma con correos únicos y activos.
Ejecutar: python generate_platform_users.py
"""

import pandas as pd
from faker import Faker
from sqlalchemy import create_engine, text
import time
import hashlib

# ============== CONFIGURACIÓN ==============
NUM_USERS = 10_000_000
BATCH_SIZE = 50_000
DB_URL = "postgresql://admin:password@db:5432/skyanalytics"
# ===========================================

fake = Faker(["es_ES", "en_US", "pt_BR", "fr_FR"])  # Diversidad de nombres

engine = create_engine(DB_URL)

def generate_hashed_password(password: str = "SkyAnalytics2024!") -> str:
    """Genera hash simple para la contraseña default."""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_username(first_name: str, last_name: str, index: int) -> str:
    """Genera nombre de usuario único."""
    base = f"{first_name.lower()}.{last_name.lower()}"
    return f"{base}{index}"

def generate_email(
    first_name: str, last_name: str, index: int, domain: str = None
) -> str:
    """Genera email único."""
    if domain is None:
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
        domain = fake.random_element(domains)

    username = generate_username(first_name, last_name, index)
    return f"{username}@{domain}"

def get_existing_emails() -> set:
    """Obtiene emails ya existentes en la tabla users."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT email FROM users"))
        return {row[0] for row in result}

def generate_users_batch(n: int, existing_emails: set, start_id: int) -> pd.DataFrame:
    """Genera un lote de usuarios."""
    data = {
        "email": [],
        "hashed_password": [],
        "full_name": [],
        "role": [],
        "tenant_id": [],
        "is_active": [],
    }

    hashed_pw = generate_hashed_password()
    roles = ["analyst", "viewer", "support", "finance_manager", "marketing_manager"]

    used_emails = set(existing_emails)
    count = 0
    attempts = 0
    max_attempts = n * 2

    while count < n and attempts < max_attempts:
        attempts += 1
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = generate_email(first_name, last_name, start_id + count)

        if email not in used_emails:
            used_emails.add(email)
            data["email"].append(email)
            data["hashed_password"].append(hashed_pw)
            data["full_name"].append(f"{first_name} {last_name}")
            data["role"].append(fake.random_element(roles))
            data["tenant_id"].append(fake.random_int(min=1, max=10))
            data["is_active"].append(True)
            count += 1

    return pd.DataFrame(data)

def get_max_user_id() -> int:
    """Obtiene el máximo ID de usuario actual."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COALESCE(MAX(id), 0) FROM users"))
        return result.scalar()

def main():
    print(f"🚀 Iniciando generación de {NUM_USERS:,} usuarios de plataforma...")

    # Verificar usuarios existentes
    existing_count = 0
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        existing_count = result.scalar()

    print(f"📊 Usuarios existentes: {existing_count:,}")

    # Si ya hay 100k+, no hacer nada
    if existing_count >= NUM_USERS:
        print(f"✅ Ya existen {existing_count:,} usuarios. No se requiere generar más.")
        return

    users_to_generate = NUM_USERS - existing_count
    print(f"📝 Generando {users_to_generate:,} nuevos usuarios...")

    existing_emails = get_existing_emails()
    print(f"📧 Emails existentes en BD: {len(existing_emails):,}")

    start_id = get_max_user_id()
    hashed_pw = generate_hashed_password()

    start_time = time.time()

    for batch_num in range(0, users_to_generate, BATCH_SIZE):
        batch_start = time.time()
        current_batch_size = min(BATCH_SIZE, users_to_generate - batch_num)

        # Generar lote
        df_batch = generate_users_batch(
            current_batch_size, existing_emails, start_id + batch_num + 1
        )

        # Insertar en la base de datos
        df_batch.to_sql(
            "users",
            engine,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=5000,
        )

        batch_time = time.time() - batch_start
        total_time = time.time() - start_time
        progress = (batch_num + current_batch_size) / users_to_generate * 100

        print(
            f"  Lote {batch_num // BATCH_SIZE + 1}: {current_batch_size:,} usuarios "
            f"({progress:.1f}%) - {batch_time:.1f}s - Total: {total_time:.1f}s"
        )

    # Verificar resultado
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM users WHERE is_active = true"))
        active_count = result.scalar()

        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        total_count = result.scalar()

    print(f"\n✅ Proceso completado!")
    print(f"   Total usuarios en BD: {total_count:,}")
    print(f"   Usuarios activos: {active_count:,}")
    print(f"   Tiempo total: {time.time() - start_time:.1f} segundos")

if __name__ == "__main__":
    main()
