"""Modelo de transacciones financieras (ingresos, egresos, balances)."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Enum
from sqlalchemy.orm import relationship
import enum

from models.base import Base


class TransactionTypeEnum(str, enum.Enum):
    """Tipos de transacción financiera."""
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class FinancialTransaction(Base):
    """Modelo de transacciones financieras para gestión de ingresos/egresos."""

    __tablename__ = "financial_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)  # INCOME o EXPENSE
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)  # Ventas, Servicios, Sueldos, etc.
    description = Column(String, nullable=True)
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<FinancialTransaction id={self.id} type={self.type} amount={self.amount} category={self.category}>"
