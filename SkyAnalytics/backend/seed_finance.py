"""Script para generar transacciones financieras realistas."""

import os
import sys
from datetime import datetime, timedelta
from random import randint, choice, uniform
from io import StringIO

import pandas as pd
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de BD
DATABASE_URL = os.getenv("DATABASE_URL")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "skyanalytics")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASS", "secretpassword")

# Categorías de finanzas
INCOME_CATEGORIES = ["Ventas", "Servicios", "Comisiones", "Otros Ingresos"]
EXPENSE_CATEGORIES = ["Sueldos", "Mantenimiento", "Marketing", "Infraestructura", "Viajes", "Otros Gastos"]


def conectar_bd():
    """Conecta a PostgreSQL."""
    try:
        if DATABASE_URL:
            conexion = psycopg2.connect(DATABASE_URL, connect_timeout=10)
            print("✓ Conectado a BD via DATABASE_URL")
        else:
            conexion = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                connect_timeout=10,
            )
            print(f"✓ Conectado a {DB_NAME}@{DB_HOST}")
        return conexion
    except psycopg2.OperationalError as e:
        print(f"✗ Error conectando: {e}")
        sys.exit(1)


def generar_transacciones(cantidad: int = 1000, months_back: int = 12) -> pd.DataFrame:
    """Genera transacciones financieras realistas para los últimos N meses."""
    print(f"Generando {cantidad:,} transacciones...")
    
    datos = {
        "type": [],
        "amount": [],
        "category": [],
        "description": [],
        "date": [],
        "created_at": [],
        "updated_at": [],
    }
    
    today = datetime.now()
    start_date = today - timedelta(days=30 * months_back)
    
    for i in range(cantidad):
        # 60% ingresos, 40% gastos
        is_income = choice([True, True, True, False, False])
        
        if is_income:
            amount = round(uniform(500, 5000), 2)
            category = choice(INCOME_CATEGORIES)
            description = f"Ingreso - {category}"
        else:
            amount = round(uniform(100, 2000), 2)
            category = choice(EXPENSE_CATEGORIES)
            description = f"Gasto - {category}"
        
        # Fecha aleatoria en el rango
        days_offset = randint(0, (today - start_date).days)
        fecha = start_date + timedelta(days=days_offset)
        
        datos["type"].append("INCOME" if is_income else "EXPENSE")
        datos["amount"].append(amount)
        datos["category"].append(category)
        datos["description"].append(description)
        datos["date"].append(fecha.date())
        datos["created_at"].append(datetime.now())
        datos["updated_at"].append(datetime.now())
        
        if (i + 1) % 100 == 0:
            print(f"  {i + 1:,} transacciones generadas...")
    
    df = pd.DataFrame(datos)
    print(f"✓ {cantidad:,} transacciones generadas")
    return df


def truncar_tabla(conexion):
    """Trunca la tabla de transacciones financieras."""
    try:
        with conexion.cursor() as cur:
            cur.execute("TRUNCATE TABLE financial_transactions CASCADE;")
            conexion.commit()
            print("✓ Tabla truncada")
    except psycopg2.Error as e:
        print(f"✗ Error truncando: {e}")
        conexion.rollback()


def insertar_con_copy_from(conexion, df: pd.DataFrame):
    """Inserta datos usando COPY FROM."""
    try:
        buffer = StringIO()
        df.to_csv(buffer, index=False, header=False, sep="|")
        buffer.seek(0)
        
        with conexion.cursor() as cur:
            cur.copy_from(buffer, "financial_transactions", columns=df.columns, sep="|")
        
        conexion.commit()
        print(f"✓ {len(df):,} registros insertados")
    except psycopg2.Error as e:
        print(f"✗ Error insertando: {e}")
        conexion.rollback()


def main():
    """Punto de entrada."""
    conexion = conectar_bd()
    
    # Generar y cargar datos
    print("\n" + "="*60)
    print("SEED FINANCIERO - Generando transacciones")
    print("="*60 + "\n")
    
    df = generar_transacciones(cantidad=2000, months_back=12)
    
    truncar_tabla(conexion)
    insertar_con_copy_from(conexion, df)
    
    # Verificar conteo
    with conexion.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM financial_transactions;")
        total = cur.fetchone()[0]
        print(f"\nTotal en BD: {total:,} transacciones")
        
        cur.execute("SELECT SUM(amount) FROM financial_transactions WHERE type='INCOME';")
        total_income = cur.fetchone()[0] or 0
        
        cur.execute("SELECT SUM(amount) FROM financial_transactions WHERE type='EXPENSE';")
        total_expense = cur.fetchone()[0] or 0
        
        print(f"Total Ingresos: ${total_income:,.2f}")
        print(f"Total Gastos: ${total_expense:,.2f}")
        print(f"Balance: ${total_income - total_expense:,.2f}")
    
    conexion.close()
    print("\n✓ Seed completado exitosamente")


if __name__ == "__main__":
    main()
