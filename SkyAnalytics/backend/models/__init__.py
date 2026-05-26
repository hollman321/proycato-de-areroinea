"""
Paquete de modelos ORM.

Import centralizado para Alembic (`from models import Base`) y para la app.
"""

from models.airport import Airport
from models.ai_recommendation import AIRecommendation
from models.alert import Alert
from models.audit_log import AuditLog
from models.base import Base
from models.enums import CategoriaEnum
from models.operation import Operation
from models.pasajero import MillasAcumuladas, Pasajero, Transaccion
from models.tenant import Tenant
from models.user import User
from models.workflow import WorkflowExecution, WorkflowTemplate

__all__ = [
    "Airport",
    "AIRecommendation",
    "Alert",
    "AuditLog",
    "Base",
    "CategoriaEnum",
    "MillasAcumuladas",
    "Pasajero",
    "Tenant",
    "Transaccion",
    "User",
    "WorkflowExecution",
    "WorkflowTemplate",
]
