"""
Script Comprehensive de Seed - Genera datos realistas para todas las tablas.

Uso:
    python seed_comprehensive.py          # Genera datos por defecto (500 pasajeros)
    python seed_comprehensive.py --count 1000   # Genera 1000 pasajeros
    python seed_comprehensive.py --reset        # Limpia todo y empieza de cero
"""

import os
import sys
import random
import uuid
from datetime import datetime, timedelta
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from faker import Faker
from sqlalchemy import text

from database import SessionLocal, engine
from models import Base
from models.airport import Airport
from models.pasajero import Pasajero, MillasAcumuladas, Transaccion
from models.finance import FinancialTransaction
from models.operation import Operation
from models.user import User
from models.alert import Alert
from models.audit_log import AuditLog
from models.ai_recommendation import AIRecommendation
from core.security import hash_password
from services.auth_service import get_user_by_email

fake = Faker(["es_ES", "en_US", "fr_FR", "de_DE", "pt_BR"])

# Constantes
PAISES = [
    "España", "México", "Argentina", "Colombia", "Chile", "Perú", "Venezuela",
    "Ecuador", "Bolivia", "Paraguay", "Uruguay", "Costa Rica", "Panama",
    "Guatemala", "Honduras", "Nicaragua", "El Salvador", "USA", "Canada",
    "Brasil", "Portugal", "Francia", "Italia", "Alemania", "Reino Unido"
]

CIUDADES_POR_PAIS = {
    "España": ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao"],
    "México": ["Ciudad de México", "Guadalajara", "Monterrey", "Cancún", "Playa del Carmen"],
    "Argentina": ["Buenos Aires", "Córdoba", "Rosario", "Mendoza", "La Plata"],
    "USA": ["Nueva York", "Los Ángeles", "Miami", "Chicago", "Houston"],
    "Brasil": ["São Paulo", "Río de Janeiro", "Salvador", "Brasilia", "Belo Horizonte"],
}

AEROPUERTOS = [
    {"iata": "MAD", "nombre": "Aeropuerto Adolfo Suárez Madrid-Barajas", "pais": "España"},
    {"iata": "BCN", "nombre": "Aeropuerto de Barcelona-El Prat", "pais": "España"},
    {"iata": "AGP", "nombre": "Aeropuerto de Málaga-Costa del Sol", "pais": "España"},
    {"iata": "MEX", "nombre": "Aeropuerto Internacional Benito Juárez", "pais": "México"},
    {"iata": "CUN", "nombre": "Aeropuerto Internacional de Cancún", "pais": "México"},
    {"iata": "EZE", "nombre": "Aeropuerto Internacional Ministro Pistarini", "pais": "Argentina"},
    {"iata": "MIA", "nombre": "Aeropuerto Internacional de Miami", "pais": "USA"},
    {"iata": "JFK", "nombre": "Aeropuerto Internacional John F. Kennedy", "pais": "USA"},
    {"iata": "LAX", "nombre": "Aeropuerto Internacional de Los Ángeles", "pais": "USA"},
    {"iata": "GIG", "nombre": "Aeropuerto Internacional de Galeão", "pais": "Brasil"},
    {"iata": "GRU", "nombre": "Aeropuerto Internacional de São Paulo/Guarulhos", "pais": "Brasil"},
    {"iata": "BOG", "nombre": "Aeropuerto Internacional El Dorado", "pais": "Colombia"},
    {"iata": "LIM", "nombre": "Aeropuerto Internacional Jorge Chávez", "pais": "Perú"},
    {"iata": "SCL", "nombre": "Aeropuerto Internacional Comodoro Arturo Merino Benítez", "pais": "Chile"},
]

# Mapeo simple nombre -> ISO (para seed). Ampliable según necesidad.
COUNTRY_TO_ISO = {
    "España": "ES",
    "México": "MX",
    "Argentina": "AR",
    "Colombia": "CO",
    "Chile": "CL",
    "Perú": "PE",
    "Venezuela": "VE",
    "Ecuador": "EC",
    "Bolivia": "BO",
    "Paraguay": "PY",
    "Uruguay": "UY",
    "Costa Rica": "CR",
    "Panama": "PA",
    "Guatemala": "GT",
    "Honduras": "HN",
    "Nicaragua": "NI",
    "El Salvador": "SV",
    "USA": "US",
    "Canada": "CA",
    "Brasil": "BR",
    "Portugal": "PT",
    "Francia": "FR",
    "Italia": "IT",
    "Alemania": "DE",
    "Reino Unido": "GB",
}

CATEGORIAS_PRODUCTO = [
    "Vuelos nacionales", "Vuelos internacionales", "Hotel y hospedaje", 
    "Seguros de viaje", "Alquiler de auto", "Tours y excursiones",
    "Comida y bebida", "Servicios especiales"
]

MODULOS_EMPRESA = [
    "Passengers", "Analytics", "Operations", "Finance", "Flights",
    "Estadisticas", "Enterprise", "AI_Recommendations"
]

def seed_airports(db):
    """Crear aeropuertos de referencia."""
    print("🌍 Creando aeropuertos...")
    existing_count = db.query(Airport).count()
    if existing_count > 0:
        print(f"   ✓ {existing_count} aeropuertos ya existen")
        return
    
    for airport_data in AEROPUERTOS:
        country_name = airport_data.get("pais", "")
        country_iso = COUNTRY_TO_ISO.get(country_name, "XX")
        airport = Airport(
            iata_code=airport_data["iata"],
            name=airport_data["nombre"],
            country_iso=country_iso,
            city=None,
        )
        db.add(airport)
    
    db.commit()
    print(f"   ✓ {len(AEROPUERTOS)} aeropuertos creados")


def seed_admin_user(db):
    """Asegurar que el usuario admin existe."""
    print("👤 Preparando usuario admin...")
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


def seed_pasajeros(db, count: int = 500):
    """Generar pasajeros realistas con datos coherentes."""
    print(f"✈️  Generando {count} pasajeros...")
    existing = db.query(Pasajero).count()
    if existing > 0:
        print(f"   ✓ {existing} pasajeros ya existen")
        return
    
    for _ in range(count):
        pais = random.choice(PAISES)
        ciudad = random.choice(CIUDADES_POR_PAIS.get(pais, [pais]))
        fecha_registro = datetime.now() - timedelta(days=random.randint(1, 730))
        
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
        db.add(pasajero)
    
    db.commit()
    print(f"   ✓ {count} pasajeros creados")


def seed_transacciones(db, pasajeros_por_transaccion: int = 3):
    """Generar transacciones realistas."""
    print("💳 Generando transacciones...")
    pasajeros = db.query(Pasajero).all()
    if not pasajeros:
        print("   ✗ No hay pasajeros para generar transacciones")
        return
    
    transacciones_count = 0
    for pasajero in pasajeros:
        # Cada pasajero tiene entre 1 y pasajeros_por_transaccion transacciones
        num_transacciones = random.randint(1, pasajeros_por_transaccion)
        for _ in range(num_transacciones):
            monto = round(random.uniform(100, 5000), 2)
            millas_ganadas = int(monto / 10) + random.randint(0, 100)
            fecha = datetime.now() - timedelta(days=random.randint(0, 365))
            
            transaccion = Transaccion(
                pasajero_id=pasajero.id,
                monto=monto,
                millas_ganadas=millas_ganadas,
                descripcion=f"Compra en {random.choice(CATEGORIAS_PRODUCTO)}",
                fecha_transaccion=fecha,
            )
            db.add(transaccion)
            transacciones_count += 1
    
    db.commit()
    print(f"   ✓ {transacciones_count} transacciones creadas")


def seed_millas_acumuladas(db):
    """Generar registros de millas acumuladas basado en transacciones."""
    print("🎁 Generando millas acumuladas...")
    # Obtener todos los pasajeros y crear millas si no existen
    pasajeros = db.query(Pasajero).all()
    creados = 0
    for pasajero in pasajeros:
        existe = db.query(MillasAcumuladas).filter(MillasAcumuladas.pasajero_id == pasajero.id).first()
        if existe:
            continue
        transacciones = db.query(Transaccion).filter(Transaccion.pasajero_id == pasajero.id).all()
        total_millas = sum(t.millas_ganadas for t in transacciones)
        total_gastado = sum(t.monto for t in transacciones)
        millas_acumuladas = MillasAcumuladas(
            pasajero_id=pasajero.id,
            millas_totales=total_millas,
            dinero_gastado=total_gastado,
        )
        db.add(millas_acumuladas)
        creados += 1

    db.commit()
    print(f"   ✓ {creados} registros de millas creados")


def seed_transacciones_financieras(db, por_tipo: int = 50):
    """Generar transacciones financieras (INCOME/EXPENSE)."""
    print("💰 Generando transacciones financieras...")
    existing = db.query(FinancialTransaction).count()
    if existing > 0:
        print(f"   ✓ {existing} transacciones financieras ya existen")
        return
    
    # INCOME
    for _ in range(por_tipo):
        fecha = datetime.now() - timedelta(days=random.randint(0, 90))
        transaccion = FinancialTransaction(
            type="INCOME",
            amount=round(random.uniform(1000, 50000), 2),
            category=random.choice(CATEGORIAS_PRODUCTO),
            description="Ingreso por venta de servicios",
            date=fecha.date(),
        )
        db.add(transaccion)
    
    # EXPENSE
    for _ in range(por_tipo):
        fecha = datetime.now() - timedelta(days=random.randint(0, 90))
        transaccion = FinancialTransaction(
            type="EXPENSE",
            amount=round(random.uniform(500, 10000), 2),
            category=random.choice(["Operación", "Marketing", "Personal", "Tecnología"]),
            description="Gasto operativo",
            date=fecha.date(),
        )
        db.add(transaccion)
    
    db.commit()
    print(f"   ✓ {por_tipo * 2} transacciones financieras creadas")


def seed_operaciones(db, count: int = 50):
    """Generar operaciones comerciales."""
    print("📊 Generando operaciones...")
    pasajeros = db.query(Pasajero).all()[:count]
    
    for i, pasajero in enumerate(pasajeros):
        operacion = Operation(
            title=f"Operación {i+1} - {pasajero.nombre_completo}",
            description=f"Gestión operativa para {pasajero.pais}",
            client_id=pasajero.id,
            status=random.choice(["PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED"]),
            category=random.choice(["Ventas", "Soporte", "Operación", "Marketing"]),
            type=random.choice(["INCOME", "EXPENSE"]),
            amount=round(random.uniform(100, 5000), 2),
        )
        db.add(operacion)
    
    db.commit()
    print(f"   ✓ {len(pasajeros)} operaciones creadas")


def seed_alerts(db, admin: User, count: int = 20):
    """Generar alertas de ejemplo."""
    print("⚠️  Generando alertas...")
    
    for _ in range(count):
        alert = Alert(
            tenant_id=admin.tenant_id,
            module=random.choice(MODULOS_EMPRESA),
            title=fake.sentence(nb_words=5),
            description=fake.sentence(nb_words=10),
            severity=random.choice(["info", "warning", "critical", "ai"]),
            status=random.choice(["open", "resolved"]),
            source=random.choice(["system", "user", "ai_command_center"]),
        )
        db.add(alert)
    
    db.commit()
    print(f"   ✓ {count} alertas creadas")


def seed_audit_logs(db, admin: User, count: int = 50):
    """Generar logs de auditoría."""
    print("📝 Generando logs de auditoría...")
    
    for _ in range(count):
        log = AuditLog(
            user_id=admin.id,
            module=random.choice(MODULOS_EMPRESA),
            action=random.choice(["CREATE", "READ", "UPDATE", "DELETE", "EXPORT"]),
            metadata={"details": fake.sentence(nb_words=5)},
            tenant_id=admin.tenant_id,
        )
        db.add(log)
    
    db.commit()
    print(f"   ✓ {count} logs de auditoría creados")


def seed_ai_recommendations(db, admin: User, count: int = 15):
    """Generar recomendaciones de IA."""
    print("🤖 Generando recomendaciones de IA...")
    
    for i in range(count):
        rec = AIRecommendation(
            id=str(uuid.uuid4()),
            tenant_id=admin.tenant_id,
            user_id=admin.id,
            title=f"Recomendación {i+1}: {fake.sentence(nb_words=4)}",
            description=fake.sentence(nb_words=10),
            module=random.choice(MODULOS_EMPRESA),
            confidence=random.choice(["high", "medium", "low"]),
            impact_score=random.randint(1, 100),
            payload={
                "action": fake.word(),
                "metric": random.choice(["revenue", "efficiency", "satisfaction"]),
            },
            status=random.choice(["pending", "applied", "rejected"]),
        )
        db.add(rec)
    
    db.commit()
    print(f"   ✓ {count} recomendaciones de IA creadas")


def reset_database(db):
    """Eliminar todos los datos (solo para desarrollo)."""
    print("🗑️  Limpiando base de datos...")
    # Desactivar foreign key constraints temporalmente (PostgreSQL)
    db.execute(text("TRUNCATE TABLE millas_acumuladas CASCADE"))
    db.execute(text("TRUNCATE TABLE transacciones CASCADE"))
    db.execute(text("TRUNCATE TABLE pasajeros CASCADE"))
    db.execute(text("TRUNCATE TABLE financial_transactions CASCADE"))
    db.execute(text("TRUNCATE TABLE operations CASCADE"))
    db.execute(text("TRUNCATE TABLE alerts CASCADE"))
    db.execute(text("TRUNCATE TABLE audit_logs CASCADE"))
    db.execute(text("TRUNCATE TABLE ai_recommendations CASCADE"))
    db.execute(text("TRUNCATE TABLE airports CASCADE"))
    db.commit()
    print("   ✓ Base de datos limpiada")


def main():
    """Ejecutar seed."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generar datos de prueba")
    parser.add_argument("--count", type=int, default=500, help="Número de pasajeros a generar")
    parser.add_argument("--reset", action="store_true", help="Limpiar BD antes de generar")
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        print("=" * 60)
        print("🚀 SEED COMPREHENSIVE - SkyAnalytics")
        print("=" * 60)
        
        if args.reset:
            reset_database(db)
        
        admin = seed_admin_user(db)
        seed_airports(db)
        seed_pasajeros(db, count=args.count)
        seed_transacciones(db, pasajeros_por_transaccion=5)
        seed_millas_acumuladas(db)
        seed_transacciones_financieras(db, por_tipo=100)
        seed_operaciones(db, count=args.count // 10)
        seed_alerts(db, admin, count=30)
        seed_audit_logs(db, admin, count=100)
        seed_ai_recommendations(db, admin, count=25)
        
        print("=" * 60)
        print("✅ SEED COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"\nPasajeros: {db.query(Pasajero).count()}")
        print(f"Transacciones: {db.query(Transaccion).count()}")
        print(f"Transacciones Financieras: {db.query(FinancialTransaction).count()}")
        print(f"Operaciones: {db.query(Operation).count()}")
        print(f"Alertas: {db.query(Alert).count()}")
        print(f"Logs: {db.query(AuditLog).count()}")
        print(f"Recomendaciones IA: {db.query(AIRecommendation).count()}")
        print(f"Aeropuertos: {db.query(Airport).count()}\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
