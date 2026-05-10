"""
Script de Carga de Datos (Seed) - 10 Millones de Registros

Este script:
1. Genera datos realistas con Faker
2. Usa Pandas para procesamiento eficiente
3. Carga con PostgreSQL COPY FROM (máxima velocidad)
4. Procesa en lotes de 50,000 para no sobrecargar RAM

Uso:
    python seed_data.py --rows 1000000 --test

Flags:
    --rows N     : Cantidad de registros a generar (default: 10000000)
    --test       : Modo test con solo 1000 registros
    --truncate   : Borra datos existentes antes de insertar
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timedelta
from io import StringIO
import random

import pandas as pd
from faker import Faker
import psycopg2
from psycopg2 import sql
import dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
dotenv.load_dotenv()

# Configuración de BD
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "skyanalytics")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASS", "secretpassword")

# Configuración de Faker
FAKE = Faker(['es_ES', 'es_MX', 'es_AR', 'en_US'])

# Constantes
PAISES_FRECUENTES = [
    "Colombia", "Mexico", "Argentina", "Peru", "Chile",
    "España", "Estados Unidos", "Brasil", "Ecuador", "Venezuela",
    "Bolivia", "Paraguay", "Uruguay", "Costa Rica", "Guatemala",
    "Alemania", "Francia", "Italia", "Reino Unido", "Canada",
]
PAISES_WEIGHTS = [
    30, 25, 15, 10, 8,
    5, 3, 1, 1, 1,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
]

CHUNK_SIZE = 50_000  # Procesar 50,000 registros por lote
BATCH_INSERT_SIZE = 10_000  # Insertar en lotes de 10,000


def generar_numero_tarjeta():
    """
    Genera un número de tarjeta válido usando el algoritmo de Luhn.
    Crea tarjetas VISA (comienzan con 4).
    """
    def luhn_checksum(card_number):
        """Calcula el checksum de Luhn"""
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        
        return checksum % 10
    
    # Generar número base (15 dígitos: 4 + 14 dígitos aleatorios)
    numero_base = "4" + "".join([str(random.randint(0, 9)) for _ in range(14)])
    numero_base_int = int(numero_base)
    
    # Calcular dígito de checksum
    checksum = luhn_checksum(numero_base_int * 10)
    digito_checksum = (10 - checksum) % 10
    
    tarjeta_valida = numero_base + str(digito_checksum)
    return tarjeta_valida


def generar_lote_pasajeros(cantidad: int, inicio_global: int = 0) -> pd.DataFrame:
    """
    Genera un lote de registros de pasajeros con datos realistas.
    
    Args:
        cantidad: Número de registros a generar
        
    Returns:
        DataFrame con columnas: nombre_completo, correo, tarjeta_credito,
                                 tarjeta_debito, direccion, ciudad, pais,
                                 fecha_registro
    """
    datos = {
        "nombre_completo": [],
        "correo": [],
        "tarjeta_credito": [],
        "tarjeta_debito": [],
        "direccion": [],
        "ciudad": [],
        "pais": [],
        "fecha_registro": [],
    }
    
    logger.info(f"Generando {cantidad:,} registros con Faker...")
    
    for i in range(cantidad):
        # Mostrar progreso cada 10,000 registros
        if (i + 1) % 10_000 == 0:
            logger.info(f"  Generados {i + 1:,} registros...")
        
        # Nombre
        nombre = FAKE.name()
        
        # Correo unico global por batch+indice para evitar colisiones entre lotes.
        indice_global = inicio_global + i
        correo = f"user{indice_global}_{random.randint(1000, 9999)}@example.com"
        
        # Tarjetas de crédito y débito válidas
        tarjeta_credito = generar_numero_tarjeta()
        tarjeta_debito = generar_numero_tarjeta()
        
        # Dirección
        direccion = FAKE.address().replace("\n", " ")[:200]
        
        # Ciudad
        ciudad = FAKE.city()
        
        # País (con peso en países del corpus)
        pais = random.choices(PAISES_FRECUENTES, weights=PAISES_WEIGHTS, k=1)[0]
        
        # Fecha de registro (últimos 2 años)
        fecha_registro = FAKE.date_between(start_date="-2y", end_date="today")
        
        # Agregar a datos
        datos["nombre_completo"].append(nombre)
        datos["correo"].append(correo)
        datos["tarjeta_credito"].append(tarjeta_credito)
        datos["tarjeta_debito"].append(tarjeta_debito)
        datos["direccion"].append(direccion)
        datos["ciudad"].append(ciudad)
        datos["pais"].append(pais)
        datos["fecha_registro"].append(fecha_registro)
    
    df = pd.DataFrame(datos)
    logger.info(f"✓ {cantidad:,} registros generados en memoria")
    
    return df


def conectar_bd() -> psycopg2.extensions.connection:
    """Conecta a la base de datos PostgreSQL"""
    try:
        conexion = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=10
        )
        logger.info(f"✓ Conectado a PostgreSQL: {DB_NAME}@{DB_HOST}:{DB_PORT}")
        return conexion
    except psycopg2.OperationalError as e:
        logger.error(f"✗ Error conectando a BD: {e}")
        logger.error("Asegúrate de que Docker esté corriendo: docker-compose up")
        sys.exit(1)


def truncar_tabla(conexion: psycopg2.extensions.connection):
    """Trunca la tabla de pasajeros"""
    try:
        with conexion.cursor() as cur:
            cur.execute("TRUNCATE TABLE pasajeros CASCADE;")
            conexion.commit()
            logger.info("✓ Tabla pasajeros truncada")
    except psycopg2.Error as e:
        logger.error(f"✗ Error truncando tabla: {e}")
        conexion.rollback()


def insertar_con_copy_from(
    conexion: psycopg2.extensions.connection,
    df: pd.DataFrame,
    batch_num: int
):
    """
    Inserta datos usando COPY FROM de PostgreSQL (máxima velocidad).
    
    COPY FROM es 10-100x más rápido que INSERT individual.
    """
    try:
        # Convertir DataFrame a CSV en memoria
        buffer = StringIO()
        df.to_csv(buffer, index=False, header=False, sep="|")
        buffer.seek(0)
        
        # Usar COPY FROM
        with conexion.cursor() as cur:
            cur.copy_from(
                buffer,
                "pasajeros",
                columns=df.columns,
                sep="|"
            )
        
        conexion.commit()
        logger.info(f"  Batch {batch_num}: {len(df):,} registros insertados con COPY FROM")
        
    except psycopg2.Error as e:
        logger.error(f"✗ Error en batch {batch_num}: {e}")
        conexion.rollback()
        raise


def cargar_datos(total_registros: int, truncate: bool = False):
    """
    Carga datos masivos en la BD en lotes de CHUNK_SIZE.
    
    Proceso:
    1. Conecta a BD
    2. Trunca si es necesario
    3. Genera y carga lotes iterativamente
    4. Usa COPY FROM para máxima velocidad
    """
    conexion = conectar_bd()
    
    if truncate:
        truncar_tabla(conexion)
    
    registros_insertados = 0
    batch_num = 0
    tiempo_inicio = datetime.now()
    
    try:
        while registros_insertados < total_registros:
            batch_num += 1
            
            # Calcular cuántos registros faltan
            registros_faltantes = total_registros - registros_insertados
            cantidad_batch = min(CHUNK_SIZE, registros_faltantes)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Batch {batch_num}: Generando {cantidad_batch:,} registros...")
            logger.info(f"Progreso: {registros_insertados:,} / {total_registros:,}")
            
            # Generar lote
            df = generar_lote_pasajeros(cantidad_batch, inicio_global=registros_insertados)
            
            # Insertar lote
            insertar_con_copy_from(conexion, df, batch_num)
            
            registros_insertados += cantidad_batch
            
            # Mostrar velocidad
            tiempo_transcurrido = (datetime.now() - tiempo_inicio).total_seconds()
            velocidad = registros_insertados / tiempo_transcurrido if tiempo_transcurrido > 0 else 0
            logger.info(f"  Velocidad: {velocidad:.0f} registros/segundo")
    
    finally:
        # Estadísticas finales
        tiempo_total = (datetime.now() - tiempo_inicio).total_seconds()
        velocidad_promedio = registros_insertados / tiempo_total if tiempo_total > 0 else 0
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✓ CARGA COMPLETADA")
        logger.info(f"  Registros insertados: {registros_insertados:,}")
        logger.info(f"  Tiempo total: {tiempo_total:.2f}s")
        logger.info(f"  Velocidad promedio: {velocidad_promedio:.0f} registros/segundo")
        if velocidad_promedio > 0:
            logger.info(f"  Tiempo estimado para 10M: {10_000_000 / velocidad_promedio / 60:.1f} minutos")
        else:
            logger.info("  Tiempo estimado para 10M: no disponible (sin registros insertados)")
        logger.info(f"{'='*60}\n")
        
        # Verificar conteo final
        with conexion.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM pasajeros;")
            total_bd = cur.fetchone()[0]
            logger.info(f"Total en BD: {total_bd:,} registros")
        
        conexion.close()


def main():
    """Punto de entrada del script"""
    parser = argparse.ArgumentParser(
        description="Carga 10 millones de registros de pasajeros en PostgreSQL"
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=10_000_000,
        help="Cantidad de registros a generar (default: 10,000,000)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Modo test: solo genera 1,000 registros"
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Trunca tabla antes de insertar"
    )
    
    args = parser.parse_args()
    
    # Determinar cantidad
    cantidad = 1_000 if args.test else args.rows
    
    logger.info(f"{'='*60}")
    logger.info(f"SEED DATA - Carga Masiva de Pasajeros")
    logger.info(f"{'='*60}")
    logger.info(f"Registros a generar: {cantidad:,}")
    logger.info(f"Base de datos: {DB_NAME}@{DB_HOST}")
    logger.info(f"Chunk size: {CHUNK_SIZE:,}")
    logger.info(f"{'='*60}\n")
    
    try:
        cargar_datos(cantidad, truncate=args.truncate)
    except KeyboardInterrupt:
        logger.warning("\n✗ Carga interrumpida por usuario")
    except Exception as e:
        logger.error(f"\n✗ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
