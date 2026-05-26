"""
Genera datos de prueba: pasajeros y operaciones para testing.
Ejecutar: python scripts/seed_test_data.py (desde backend/)
"""

import os
import sys
from datetime import datetime, timedelta
from random import choice, randint, uniform

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.pasajero import Pasajero, Transaccion, MillasAcumuladas
from models.operation import Operation


def seed_test_data():
    """Genera 10 pasajeros y 30 operaciones para testing."""
    db = SessionLocal()

    try:
        # Verificar si ya existen datos
        pasajero_count = db.query(Pasajero).count()
        if pasajero_count > 0:
            print(f"Ya existen {pasajero_count} pasajeros. Saltando seed...")
            return

        # Datos ficticios
        nombres = [
            "Juan García",
            "María López",
            "Carlos Rodríguez",
            "Ana Martínez",
            "Pedro Sánchez",
            "Laura González",
            "Marco Fernández",
            "Sofia Díaz",
            "Diego Ruiz",
            "Elena Torres",
        ]

        ciudades = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao"]
        paises = ["España", "Portugal", "Francia", "Italia", "Alemania"]

        # Crear pasajeros
        pasajeros = []
        for i, nombre in enumerate(nombres):
            pasajero = Pasajero(
                nombre_completo=nombre,
                correo=f"{nombre.lower().replace(' ', '.')}@example.com",
                tarjeta_credito=f"4532-{randint(1000, 9999)}-{randint(1000, 9999)}-{randint(1000, 9999)}",
                tarjeta_debito=f"5233-{randint(1000, 9999)}-{randint(1000, 9999)}-{randint(1000, 9999)}",
                direccion=f"Calle Principal {i+1}, {randint(100, 999)}",
                ciudad=choice(ciudades),
                pais=choice(paises),
                fecha_registro=(
                    datetime.now() - timedelta(days=randint(30, 365))
                ).date(),
            )
            db.add(pasajero)
            db.flush()
            pasajeros.append(pasajero)

            # Crear millas acumuladas
            millas = MillasAcumuladas(
                pasajero_id=pasajero.id,
                millas_totales=randint(1000, 50000),
                dinero_gastado=uniform(1000, 50000),
            )
            db.add(millas)

        db.commit()
        print(f"✓ Creados {len(pasajeros)} pasajeros")

        # Crear operaciones
        operaciones = []
        estados = ["PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED"]
        tipos = ["INCOME", "EXPENSE"]
        categorias = [
            "Vuelo",
            "Hotel",
            "Transporte",
            "Catering",
            "Mantenimiento",
            "Marketing",
            "Administrativo",
        ]

        for i in range(30):
            operacion = Operation(
                title=f"Operación {i+1} - {choice(categorias)}",
                description=f"Descripción operativa para {choice(categorias).lower()}",
                client_id=choice(pasajeros).id,
                status=choice(estados),
                category=choice(categorias),
                type=choice(tipos),
                amount=uniform(100, 10000),
                created_at=datetime.now() - timedelta(days=randint(0, 30)),
                updated_at=datetime.now() - timedelta(days=randint(0, 30)),
            )
            db.add(operacion)
            operaciones.append(operacion)

        db.commit()
        print(f"✓ Creadas {len(operaciones)} operaciones")
        print("✓ Seed completado exitosamente")

    except Exception as e:
        db.rollback()
        print(f"✗ Error al generar datos: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_test_data()
