import pandas as pd
from faker import Faker
import numpy as np
from sqlalchemy import create_engine
import time

# Configuración
num_registros = 10_000_000
batch_size = 100_000  # Insertar de 100k en 100k para no saturar la RAM
fake = Faker()

# Conexión a Postgres (Ajusta con tus credenciales de Docker)
engine = create_engine('postgresql://admin:secretpassword@localhost:5432/skyanalytics')

def generar_datos(n):
    data = {
        'nombre_completo': [fake.name() for _ in range(n)],
        'correo': [fake.unique.email() for _ in range(n)],
        'tarjeta_credito': [fake.credit_card_number(card_type='visa') for _ in range(n)],
        'tarjeta_debito': [fake.credit_card_number(card_type='mastercard') for _ in range(n)],
        'direccion': [fake.street_address() for _ in range(n)],
        'ciudad': [fake.city() for _ in range(n)],
        'pais': [fake.country() for _ in range(n)],
        'fecha_registro': [fake.date_this_century() for _ in range(n)]
    }
    return pd.DataFrame(data)

print(f"Iniciando generación de {num_registros} registros...")
inicio_total = time.time()

# Bucle para insertar por lotes
for i in range(0, num_registros, batch_size):
    start_time = time.time()
    
    # Generar lote
    df_batch = generar_datos(batch_size)
    
    # Insertar en Postgres
    # 'if_exists=append' es clave para no borrar lo anterior
    df_batch.to_sql('pasajeros', engine, if_exists='append', index=False, method='multi', chunksize=10000)
    
    end_time = time.time()
    print(f"Lote {i // batch_size + 1} completado en {end_time - start_time:.2f} segundos.")

print(f"--- Proceso finalizado en {time.time() - inicio_total:.2f} segundos ---")