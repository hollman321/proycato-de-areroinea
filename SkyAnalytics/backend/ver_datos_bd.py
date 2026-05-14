#!/usr/bin/env python3
"""Script para visualizar datos de la base de datos SkyAnalytics"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Conexión a PostgreSQL
conn = psycopg2.connect(
    dbname='skyanalytics',
    user='admin',
    password='secretpassword',
    host='localhost',
    port='5432'
)

cur = conn.cursor(cursor_factory=RealDictCursor)

# Obtener todas las tablas
cur.execute("""
    SELECT tablename FROM pg_tables 
    WHERE schemaname='public' 
    ORDER BY tablename
""")
tablas = [row['tablename'] for row in cur.fetchall()]

print("\n" + "="*60)
print("📊 BASE DE DATOS SKYANALYTICS - CONTENIDO")
print("="*60 + "\n")

for tabla in tablas:
    if tabla == 'alembic_version':
        continue
    
    # Contar registros
    cur.execute(f"SELECT COUNT(*) as total FROM {tabla}")
    count = cur.fetchone()['total']
    
    # Obtener estructura
    cur.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{tabla}'
        ORDER BY ordinal_position
    """)
    columnas = cur.fetchall()
    
    print(f"📋 TABLA: {tabla.upper()}")
    print(f"   Registros: {count}")
    print(f"   Columnas:")
    for col in columnas:
        print(f"      • {col['column_name']}: {col['data_type']}")
    
    # Mostrar datos si hay
    if count > 0 and count <= 10:
        print(f"   Datos:")
        cur.execute(f"SELECT * FROM {tabla} LIMIT 5")
        for row in cur.fetchall():
            print(f"      {dict(row)}")
    elif count > 10:
        print(f"   (Mostrando primeros 5 registros de {count} totales)")
        cur.execute(f"SELECT * FROM {tabla} LIMIT 5")
        for row in cur.fetchall():
            print(f"      {dict(row)}")
    
    print()

conn.close()
print("="*60)
