"""
Paquete de modelos ORM.

Import centralizado para Alembic (`from models import Base`) y para la app.
"""

from .airport import Airport
from .ai_recommendation import AIRecommendation
from .alert import Alert
from .audit_log import AuditLog
from .base import Base
from .enums import CategoriaEnum
from .finance import FinancialTransaction
from .operation import Operation
from .pasajero import MillasAcumuladas, Pasajero, Transaccion
from .tenant import Tenant
from .user import User
from .workflow import WorkflowExecution, WorkflowTemplate

__all__ = [
    "Airport",
    "AIRecommendation",
    "Alert",
    "AuditLog",
    "Base",
    "CategoriaEnum",
    "FinancialTransaction",
    "MillasAcumuladas",
    "Pasajero",
    "Tenant",
    "Transaccion",
    "User",
    "WorkflowExecution",
    "WorkflowTemplate",
]
