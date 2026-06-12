"""Schemas Pydantic para transacciones financieras."""

from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class FinancialTransactionBase(BaseModel):
    """Base schema para transacciones financieras."""
    type: str = Field(..., pattern="^(INCOME|EXPENSE)$")
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    date: date


class FinancialTransactionCreate(FinancialTransactionBase):
    """Schema para crear transacción financiera."""
    pass


class FinancialTransactionUpdate(BaseModel):
    """Schema para actualizar transacción financiera."""
    type: Optional[str] = Field(None, pattern="^(INCOME|EXPENSE)$")
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    date: Optional[date] = None


class FinancialTransactionResponse(FinancialTransactionBase):
    """Schema de respuesta para transacción financiera."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FinancialSummaryResponse(BaseModel):
    """Schema de resumen de finanzas."""
    total_income: float
    total_expense: float
    balance: float
    transaction_count: int
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
