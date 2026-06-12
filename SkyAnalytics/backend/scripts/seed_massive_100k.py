"""
Script de Seed Masivo - Carga 100,000+ registros con datos financieros realistas.

Uso:
    python seed_massive_100k.py          # Genera 100,000 pasajeros (LENTO, ~5-10 min)
    python seed_massive_100k.py --count 50000   # Genera 50,000 registros
    
Características:
    - 100,000 pasajeros con datos aleatorios realistas
    - Transacciones financieras con descuentos aleatorios (5%-40%)
    - Gastos e ingresos variados por categoría
    - Millones en movimiento de capital
"""

import os
import sys
import random
import uuid
import argparse
from datetime import datetime, timedelta
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from faker import Faker
from sqlalchemy import text, func
from database import SessionLocal, engine
from models import Base
from models.pasajero import Pasajero, MillasAcumuladas, Transaccion
from models.finance import FinancialTransaction
from models.operation import Operation
from models.user import User
from core.security import hash_password
from services.auth_service import get_user_by_email

fake = Faker(["es_ES", "en_US", "fr_FR", "de_DE", "pt_BR", "it_IT", "ja_JP", "ru_RU"])

PAISES = [
    "España", "México", "Argentina", "Colombia", "Chile", "Perú", "Venezuela",
    "Ecuador", "Bolivia", "Paraguay", "Uruguay", "Costa Rica", "Panama",
    "Guatemala", "Honduras", "Nicaragua", "El Salvador", "USA", "Canada",
    "Brasil", "Portugal", "Francia", "Italia", "Alemania", "Reino Unido",
    "Japón", "China", "India", "Rusia", "Australia", "Singapur"
]

CIUDADES_PRINCIPALES = [
    "Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao",
    "Ciudad de México", "Guadalajara", "Monterrey", "Cancún", "México DF",
    "Buenos Aires", "Córdoba", "Rosario", "Mendoza", "La Plata",
    "Nueva York", "Los Ángeles", "Miami", "Chicago", "Houston",
    "São Paulo", "Río de Janeiro", "Salvador", "Brasilia", "Belo Horizonte",
    "Bogotá", "Cartagena", "Cali", "Lima", "Arequipa",
    "Tokio", "Osaka", "Kioto", "Pekín", "Shanghái",
    "Berlín", "Múnich", "París", "Roma", "Ámsterdam"
]

CATEGORIAS_GASTO = [
    "Vuelos nacionales", "Vuelos internacionales", "Hotel y hospedaje",
    "Seguros de viaje", "Alquiler de auto", "Tours y excursiones",
    "Comida y bebida", "Servicios especiales", "Transporte terrestre",
    "Entretenimiento", "Compras retail", "Servicios médicos"
]

CATEGORIAS_INGRESOS = [
    "Comisión de ventas", "Servicios profesionales", "Consultoría",
    "Capacitación", "Soporte técnico", "Asesoría estratégica"
]

ESTADOS_OPERACION = ["PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED"]


def calcular_descuento_aleatorio():
    """Genera descuento aleatorio entre 5% y 40%."""
    return round(random.uniform(0.05, 0.40), 2)


def seed_admin_user(db):
    """Asegurar que el usuario admin existe."""
    print("👤 Verificando usuario admin...")
    admin = get_user_by_email(db, "admin@skyanalytics.com")
    if admin:
        print("   ✓ Admin ya existe")
        return admin

    admin = User(
        email="admin@skyanalytics.com",
        full_name="Administrador del Sistema",
        hashed_password=hash_password("admin123"),
        role="admin",
        is_active=True,
        tenant_id=1,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print("   ✓ Admin creado")
    return admin


def seed_pasajeros_masivos(db, count: int = 100000):
    """Generar pasajeros en lotes para optimizar velocidad."""
    print(f"\n✈️  Generando {count:,} pasajeros...")

    existing = db.query(Pasajero).count()
    if existing > 0:
        print(f"   ⚠️  {existing:,} pasajeros ya existen. Continuando...")
        return

    batch_size = 1000
    total_batches = (count + batch_size - 1) // batch_size

    for batch_num in range(total_batches):
        batch = []
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, count)
        batch_count = end_idx - start_idx

        for i in range(batch_count):
            pais = random.choice(PAISES)
            ciudad = random.choice(CIUDADES_PRINCIPALES)
            fecha_registro = datetime.now() - timedelta(days=random.randint(1, 1095))

            pasajero = Pasajero(
                nombre_completo=fake.name(),
                correo=fake.unique.email(),
                tarjeta_credito=fake.credit_card_number(card_type="visa"),
                tarjeta_debito=fake.credit_card_number(card_type="mastercard"),
                direccion=fake.street_address(),
                ciudad=ciudad,
                pais=pais,
                fecha_registro=fecha_registro.date(),
            )
            batch.append(pasajero)

        db.bulk_save_objects(batch)
        db.commit()

        progress = ((batch_num + 1) / total_batches) * 100
        print(f"   [{progress:5.1f}%] Pasajeros creados: {min((batch_num + 1) * batch_size, count):,}")

    print(f"   ✅ {count:,} pasajeros creados exitosamente")


def seed_transacciones_masivas(db, transacciones_por_pasajero: int = 5):
    """Generar transacciones con descuentos aleatorios."""
    print(f"\n💳 Generando transacciones con descuentos aleatorios...")

    pasajeros = db.query(Pasajero).all()
    total_pasajeros = len(pasajeros)

    if total_pasajeros == 0:
        print("   ✗ No hay pasajeros para generar transacciones")
        return

    batch_size = 5000
    batch = []
    total_transacciones = 0
    total_gastado = 0

    for idx, pasajero in enumerate(pasajeros):
        num_transacciones = random.randint(2, transacciones_por_pasajero + 3)

        for _ in range(num_transacciones):
            # Monto original entre 50 y 10,000
            monto_original = round(random.uniform(50, 10000), 2)

            # Aplicar descuento aleatorio
            descuento_pct = calcular_descuento_aleatorio()
            monto_descuento = round(monto_original * descuento_pct, 2)
            monto_final = round(monto_original - monto_descuento, 2)

            # Millas basadas en monto final
            millas_ganadas = int(monto_final / 5) + random.randint(0, 50)

            fecha = datetime.now() - timedelta(days=random.randint(0, 730))

            transaccion = Transaccion(
                pasajero_id=pasajero.id,
                monto=monto_final,  # Ya con descuento aplicado
                millas_ganadas=millas_ganadas,
                descripcion=f"{random.choice(CATEGORIAS_GASTO)} (-{descuento_pct*100:.0f}%)",
                fecha_transaccion=fecha,
            )
            batch.append(transaccion)
            total_transacciones += 1
            total_gastado += monto_final

            if len(batch) >= batch_size:
                db.bulk_save_objects(batch)
                db.commit()
                print(f"   [{(idx + 1) / total_pasajeros * 100:5.1f}%] Transacciones: {total_transacciones:,} | Total gastado: ${total_gastado:,.2f}")
                batch = []

        if (idx + 1) % 1000 == 0:
            print(f"   [{(idx + 1) / total_pasajeros * 100:5.1f}%] Procesando pasajero {idx + 1:,}/{total_pasajeros:,}")

    # Guardar batch final
    if batch:
        db.bulk_save_objects(batch)
        db.commit()

    print(f"   ✅ {total_transacciones:,} transacciones creadas")
    print(f"   💰 Total gastado por pasajeros: ${total_gastado:,.2f}")


def seed_millas_acumuladas_masivas(db):
    """Calcular millas acumuladas por pasajero."""
    print(f"\n🎁 Calculando millas acumuladas...")

    # Usar agregación SQL para ser más eficiente
    pasajeros = db.query(Pasajero).all()
    batch = []
    batch_size = 5000

    for idx, pasajero in enumerate(pasajeros):
        existe = (
            db.query(MillasAcumuladas)
            .filter(MillasAcumuladas.pasajero_id == pasajero.id)
            .first()
        )
        if existe:
            continue

        transacciones = (
            db.query(Transaccion)
            .filter(Transaccion.pasajero_id == pasajero.id)
            .all()
        )

        total_millas = sum(t.millas_ganadas for t in transacciones)
        total_gastado = sum(t.monto for t in transacciones)

        millas = MillasAcumuladas(
            pasajero_id=pasajero.id,
            millas_totales=total_millas,
            dinero_gastado=total_gastado,
        )
        batch.append(millas)

        if len(batch) >= batch_size:
            db.bulk_save_objects(batch)
            db.commit()
            print(f"   [{(idx + 1) / len(pasajeros) * 100:5.1f}%] Millas calculadas para {idx + 1:,} pasajeros")
            batch = []

    if batch:
        db.bulk_save_objects(batch)
        db.commit()

    print(f"   ✅ Millas acumuladas calculadas")


def seed_transacciones_financieras_masivas(db, por_tipo: int = 5000):
    """Generar transacciones financieras de ingresos y gastos."""
    print(f"\n💰 Generando {por_tipo * 2:,} transacciones financieras...")

    batch = []
    total_ingresos = 0
    total_gastos = 0
    batch_size = 5000

    # INGRESOS
    print(f"   Creando {por_tipo:,} ingresos...")
    for i in range(por_tipo):
        fecha = datetime.now() - timedelta(days=random.randint(0, 365))
        monto = round(random.uniform(5000, 500000), 2)
        descuento_aplicado = round(random.uniform(0, 0.30) * monto, 2)  # Hasta 30% descuento
        monto_neto = monto - descuento_aplicado

        transaccion = FinancialTransaction(
            type="INCOME",
            amount=monto_neto,
            category=random.choice(CATEGORIAS_INGRESOS),
            description=f"Ingreso operativo (Desc: ${descuento_aplicado:,.2f})",
            date=fecha.date(),
        )
        batch.append(transaccion)
        total_ingresos += monto_neto

        if len(batch) >= batch_size:
            db.bulk_save_objects(batch)
            db.commit()
            print(f"      Ingresos: {min(i + 1, por_tipo):,} | Total: ${total_ingresos:,.2f}")
            batch = []

    # GASTOS
    print(f"   Creando {por_tipo:,} gastos...")
    for i in range(por_tipo):
        fecha = datetime.now() - timedelta(days=random.randint(0, 365))
        monto = round(random.uniform(2000, 100000), 2)
        descuento_aplicado = round(random.uniform(0, 0.25) * monto, 2)  # Hasta 25% descuento
        monto_neto = monto - descuento_aplicado

        transaccion = FinancialTransaction(
            type="EXPENSE",
            amount=monto_neto,
            category=random.choice(
                ["Operación", "Salarios", "Marketing", "Infraestructura", "Servicios"]
            ),
            description=f"Gasto operativo (Desc: ${descuento_aplicado:,.2f})",
            date=fecha.date(),
        )
        batch.append(transaccion)
        total_gastos += monto_neto

        if len(batch) >= batch_size:
            db.bulk_save_objects(batch)
            db.commit()
            print(f"      Gastos: {min(i + 1, por_tipo):,} | Total: ${total_gastos:,.2f}")
            batch = []

    # Guardar batch final
    if batch:
        db.bulk_save_objects(batch)
        db.commit()

    print(f"   ✅ Transacciones financieras creadas")
    print(f"   📊 INGRESOS TOTALES: ${total_ingresos:,.2f}")
    print(f"   📊 GASTOS TOTALES: ${total_gastos:,.2f}")
    print(f"   📊 BALANCE: ${total_ingresos - total_gastos:,.2f}")


def seed_operaciones_masivas(db, count: int = 5000):
    """Generar operaciones comerciales masivas."""
    print(f"\n📊 Generando {count:,} operaciones...")

    pasajeros = db.query(Pasajero).all()
    if not pasajeros:
        print("   ✗ No hay pasajeros para operaciones")
        return

    batch = []
    batch_size = 2000
    total_operaciones = 0
    total_monto = 0

    for i in range(count):
        pasajero = random.choice(pasajeros)
        monto = round(random.uniform(100, 50000), 2)
        descuento = calcular_descuento_aleatorio()
        monto_final = round(monto * (1 - descuento), 2)

        operacion = Operation(
            title=f"Operación {i + 1} - {pasajero.pais}",
            description=f"Gestión operativa para {pasajero.nombre_completo} (Desc: {descuento*100:.0f}%)",
            client_id=pasajero.id,
            status=random.choice(ESTADOS_OPERACION),
            category=random.choice(CATEGORIAS_GASTO),
            type=random.choice(["INCOME", "EXPENSE"]),
            amount=monto_final,
        )
        batch.append(operacion)
        total_operaciones += 1
        total_monto += monto_final

        if len(batch) >= batch_size:
            db.bulk_save_objects(batch)
            db.commit()
            progress = (i + 1) / count * 100
            print(f"   [{progress:5.1f}%] Operaciones: {total_operaciones:,} | Monto total: ${total_monto:,.2f}")
            batch = []

    if batch:
        db.bulk_save_objects(batch)
        db.commit()

    print(f"   ✅ {total_operaciones:,} operaciones creadas")
    print(f"   💵 Monto total operaciones: ${total_monto:,.2f}")


def mostrar_resumen(db):
    """Mostrar estadísticas finales."""
    print("\n" + "=" * 80)
    print("📊 RESUMEN FINAL DEL SEED MASIVO")
    print("=" * 80)

    total_pasajeros = db.query(Pasajero).count()
    total_transacciones = db.query(Transaccion).count()
    total_millas = db.query(MillasAcumuladas).count()
    total_ingresos_db = (
        db.query(func.sum(FinancialTransaction.amount))
        .filter(FinancialTransaction.type == "INCOME")
        .scalar() or 0
    )
    total_gastos_db = (
        db.query(func.sum(FinancialTransaction.amount))
        .filter(FinancialTransaction.type == "EXPENSE")
        .scalar() or 0
    )
    total_operaciones = db.query(Operation).count()

    print(f"👥 Pasajeros registrados:           {total_pasajeros:>15,}")
    print(f"💳 Transacciones de pasajeros:      {total_transacciones:>15,}")
    print(f"🎁 Registros de millas:             {total_millas:>15,}")
    print(f"📊 Operaciones comerciales:         {total_operaciones:>15,}")
    print(f"💰 INGRESOS FINANCIEROS:            ${total_ingresos_db:>14,.2f}")
    print(f"💸 GASTOS FINANCIEROS:              ${total_gastos_db:>14,.2f}")
    print(f"📈 BALANCE NETO:                    ${total_ingresos_db - total_gastos_db:>14,.2f}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Seed masivo con 100K+ registros y datos financieros realistas"
    )
    parser.add_argument(
        "--count", type=int, default=100000, help="Número de pasajeros a generar (default: 100000)"
    )
    parser.add_argument(
        "--transacciones", type=int, default=10, help="Transacciones por pasajero (default: 10)"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Resetear la base de datos antes de seed (PELIGROSO)",
    )

    args = parser.parse_args()

    db = SessionLocal()

    try:
        print("\n" + "=" * 80)
        print("🚀 INICIANDO SEED MASIVO - SkyAnalytics")
        print("=" * 80)
        print(f"   Pasajeros a generar: {args.count:,}")
        print(f"   Transacciones por pasajero: {args.transacciones}")
        print("=" * 80)

        # Admin
        seed_admin_user(db)

        # Pasajeros
        seed_pasajeros_masivos(db, args.count)

        # Transacciones con descuentos
        seed_transacciones_masivas(db, args.transacciones)

        # Millas
        seed_millas_acumuladas_masivas(db)

        # Transacciones financieras
        seed_transacciones_financieras_masivas(db, por_tipo=5000)

        # Operaciones
        seed_operaciones_masivas(db, count=5000)

        # Resumen
        mostrar_resumen(db)

        print("\n✅ SEED COMPLETADO EXITOSAMENTE\n")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
