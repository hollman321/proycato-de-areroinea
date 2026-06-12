"""
Script para cargar datos de prueba pequeño rápidamente.
"""

from sqlalchemy import create_engine, text
from faker import Faker
import random
from datetime import datetime, timedelta
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:password@localhost:5432/skyanalytics")

engine = create_engine(DATABASE_URL)
fake = Faker()

# Países para seleccionar aleatoriamente
PAISES = ['CO', 'MX', 'BR', 'AR', 'CL', 'PE', 'EC', 'VE', 'US', 'ES', 'FR', 'DE', 'IT', 'JP', 'CN', 'IN']
AEROPUERTOS_IATA = ['BOG', 'MDE', 'MEX', 'GIG', 'EZE', 'SCL', 'LIM', 'UIO', 'CCS', 'IAD', 'MAD', 'CDG', 'BER', 'FCO', 'HND', 'PEK', 'DEL']

print("Cargando datos de prueba...")

with engine.connect() as conn:
    conn.autocommit = True
    
    # Cargar aeropuertos
    print("Cargando aeropuertos...")
    for iata in AEROPUERTOS_IATA:
        conn.execute(text(f"""
            INSERT INTO airports (iata_code, icao_code, name, city, country_iso, latitude, longitude)
            VALUES ('{iata}', '{iata}{fake.random_int()}', '{fake.city()} Airport', '{fake.city()}', '{random.choice(PAISES)}', {fake.latitude()}, {fake.longitude()})
            ON CONFLICT DO NOTHING
        """))
    print(f"✓ {len(AEROPUERTOS_IATA)} aeropuertos cargados")
    
    # Cargar pasajeros
    print("Cargando pasajeros...")
    base_date = datetime(2024, 1, 1)
    for i in range(1000):
        fecha = base_date + timedelta(days=random.randint(0, 500))
        conn.execute(text(f"""
            INSERT INTO pasajeros (nombre, apellido, email, pais_origen, fecha_registro, viajes_totales)
            VALUES ('{fake.first_name()}', '{fake.last_name()}', '{fake.email()}', '{random.choice(PAISES)}', '{fecha.isoformat()}', {random.randint(1, 50)})
        """))
    print("✓ 1,000 pasajeros cargados")
    
    # Cargar transacciones
    print("Cargando transacciones...")
    for i in range(500):
        fecha = base_date + timedelta(days=random.randint(0, 500))
        conn.execute(text(f"""
            INSERT INTO transacciones (pasajero_id, monto, moneda, descripcion, fecha_transaccion)
            VALUES ({random.randint(1, 1000)}, {random.randint(100, 5000)}, 'USD', '{fake.text(max_nb_chars=50)}', '{fecha.isoformat()}')
        """))
    print("✓ 500 transacciones cargadas")
    
    # Cargar millas
    print("Cargando millas acumuladas...")
    for i in range(1000):
        conn.execute(text(f"""
            INSERT INTO millas_acumuladas (pasajero_id, millas, fecha_acumulacion)
            VALUES ({random.randint(1, 1000)}, {random.randint(100, 50000)}, NOW())
            ON CONFLICT (pasajero_id) DO UPDATE SET millas = millas_acumuladas.millas + {random.randint(100, 50000)}
        """))
    print("✓ 1,000 registros de millas cargados")

print("\n✅ Datos de prueba cargados exitosamente")
