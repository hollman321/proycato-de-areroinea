"""
Paquete de modelos ORM.

Import centralizado para Alembic (`from models import Base`) y para la app.
"""

from models.airport import Airport
from models.base import Base
from models.enums import CategoriaEnum
from models.pasajero import MillasAcumuladas, Pasajero, Transaccion
from models.user import User

__all__ = [
    "Airport",
    "Base",
    "CategoriaEnum",
    "Pasajero",
    "Transaccion",
    "MillasAcumuladas",
    "User",
]
