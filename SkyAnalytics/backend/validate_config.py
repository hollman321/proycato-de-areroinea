#!/usr/bin/env python
"""
Script de Validación de Conexión a BD

Verifica que:
1. Las variables de entorno están correctas
2. PostgreSQL es accesible
3. La BD y tabla existen
4. Las validaciones de Pydantic funcionan
"""

import os
import sys
import logging
from datetime import date

import psycopg2
import dotenv

# Cargar .env
dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def verificar_entorno():
    """Verifica variables de entorno"""
    logger.info("🔍 Verificando variables de entorno...")
    
    variables = [
        ("DB_HOST", os.getenv("DB_HOST")),
        ("DB_PORT", os.getenv("DB_PORT")),
        ("DB_USER", os.getenv("DB_USER")),
        ("DB_PASS", "***" if os.getenv("DB_PASS") else "NO DEFINIDA"),
        ("POSTGRES_DB", os.getenv("POSTGRES_DB")),
    ]
    
    for nombre, valor in variables:
        estado = "✓" if valor else "✗"
        logger.info(f"  {estado} {nombre}: {valor}")
    
    return all(valor for nombre, valor in variables[:-1])  # Excluir pass


def verificar_conexion():
    """Verifica conexión a PostgreSQL"""
    logger.info("\n🔌 Verificando conexión a PostgreSQL...")
    
    try:
        conexion = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
        )
        logger.info("  ✓ Conexión exitosa")
        return conexion
    except psycopg2.OperationalError as e:
        logger.error(f"  ✗ Error de conexión: {e}")
        logger.error("\n💡 Soluciones:")
        logger.error("  1. Verifica que Docker está corriendo: docker ps")
        logger.error("  2. Verifica que el contenedor está activo: docker-compose ps")
        logger.error("  3. Inicia Docker: docker-compose up")
        return None


def verificar_tablas(conexion):
    """Verifica que las tablas existan"""
    logger.info("\n📋 Verificando tablas...")
    
    try:
        with conexion.cursor() as cur:
            # Verificar tabla pasajeros
            cur.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name='pasajeros'
                )
            """)
            existe = cur.fetchone()[0]
            
            if existe:
                # Contar registros
                cur.execute("SELECT COUNT(*) FROM pasajeros")
                total = cur.fetchone()[0]
                logger.info(f"  ✓ Tabla 'pasajeros' existe ({total:,} registros)")
                
                # Mostrar estructura
                cur.execute("""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name='pasajeros' 
                    ORDER BY ordinal_position
                """)
                logger.info("  Estructura:")
                for col_name, data_type, nullable in cur.fetchall():
                    nullable_str = "nullable" if nullable == 'YES' else "NOT NULL"
                    logger.info(f"    - {col_name}: {data_type} ({nullable_str})")
            else:
                logger.warning("  ⚠ Tabla 'pasajeros' NO existe")
                logger.info("  Ejecuta primero: python seed_data.py --test")
            
            return existe
    except psycopg2.Error as e:
        logger.error(f"  ✗ Error verificando tablas: {e}")
        return False


def verificar_validaciones():
    """Verifica que las validaciones de Pydantic funcionan"""
    logger.info("\n✅ Verificando validaciones de Pydantic...")
    
    try:
        from schemas import PasajeroSchemaBase, ValidadorTarjeta
        
        # Test 1: Email válido
        try:
            datos_validos = {
                "nombre_completo": "Juan Pérez",
                "correo": "juan@gmail.com",
                "tarjeta_credito": "4532015112830366",  # VISA válida
                "tarjeta_debito": "5425233010103442",   # MASTERCARD válida
                "direccion": "Calle 123",
                "ciudad": "Bogotá",
                "pais": "Colombia",
                "fecha_registro": date.today(),
            }
            pasajero = PasajeroSchemaBase(**datos_validos)
            logger.info("  ✓ Validación de datos correctos: OK")
        except Exception as e:
            logger.error(f"  ✗ Validación de datos correctos falló: {e}")
        
        # Test 2: Email inválido
        try:
            datos_invalidos = datos_validos.copy()
            datos_invalidos["correo"] = "correo_invalido"
            PasajeroSchemaBase(**datos_invalidos)
            logger.warning("  ⚠ Validación de email NO funcionó (debería fallar)")
        except Exception:
            logger.info("  ✓ Validación de email inválido: OK (rechazó)")
        
        # Test 3: Tarjeta inválida
        try:
            datos_invalidos = datos_validos.copy()
            datos_invalidos["tarjeta_credito"] = "1234567890123456"  # Inválida
            PasajeroSchemaBase(**datos_invalidos)
            logger.warning("  ⚠ Validación de tarjeta NO funcionó (debería fallar)")
        except Exception:
            logger.info("  ✓ Validación de tarjeta inválida: OK (rechazó)")
        
        # Test 4: Luhn checksum
        logger.info("  Probando algoritmo de Luhn:")
        tarjetas_test = [
            ("4532015112830366", True),   # VISA válida
            ("5425233010103442", True),   # MASTERCARD válida
            ("4532015112830367", False),  # VISA inválida
        ]
        for tarjeta, deberia_ser_valida in tarjetas_test:
            es_valida = ValidadorTarjeta.validar_numero_tarjeta(tarjeta)
            estado = "✓" if es_valida == deberia_ser_valida else "✗"
            logger.info(f"    {estado} {tarjeta}: {es_valida}")
        
    except ImportError as e:
        logger.error(f"  ✗ Error importando schemas.py: {e}")
    except Exception as e:
        logger.error(f"  ✗ Error en validaciones: {e}")


def main():
    """Ejecuta todas las verificaciones"""
    logger.info("=" * 60)
    logger.info("VALIDACIÓN DE CONFIGURACIÓN - SkyAnalytics Backend")
    logger.info("=" * 60)
    
    # 1. Verificar entorno
    if not verificar_entorno():
        logger.error("\n✗ Falta configurar variables de entorno")
        return False
    
    # 2. Verificar conexión
    conexion = verificar_conexion()
    if not conexion:
        return False
    
    # 3. Verificar tablas
    verificar_tablas(conexion)
    conexion.close()
    
    # 4. Verificar validaciones
    verificar_validaciones()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ VALIDACIÓN COMPLETADA")
    logger.info("=" * 60)
    logger.info("\nPróximos pasos:")
    logger.info("  1. Ejecuta: python seed_data.py --test")
    logger.info("  2. Luego: python seed_data.py --rows 1000000")
    logger.info("  3. Prueba API: curl http://localhost:8000/pasajeros")
    logger.info("=" * 60 + "\n")


if __name__ == "__main__":
    main()
