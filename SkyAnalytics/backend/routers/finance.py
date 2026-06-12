"""Router de finanzas: gestión de transacciones, ingresos y egresos."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, datetime
from typing import List

from models.finance import FinancialTransaction
from schemas.finance import (
    FinancialTransactionCreate,
    FinancialTransactionUpdate,
    FinancialTransactionResponse,
    FinancialSummaryResponse,
)
from database import get_db
from deps import get_current_active_user

router = APIRouter(prefix="/finance", tags=["Finanzas"])

@router.get("", response_model=List[FinancialTransactionResponse])
def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type_filter: str = Query(None, regex="^(INCOME|EXPENSE)$"),
    category: str = Query(None),
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db),
):
    """
    Obtener transacciones financieras con filtros.

    Parámetros:
    - skip: Desplazamiento de paginación (default: 0)
    - limit: Cantidad de resultados (default: 100, máx: 1000)
    - type_filter: Filtrar por INCOME o EXPENSE
    - category: Filtrar por categoría
    - start_date: Filtrar desde fecha
    - end_date: Filtrar hasta fecha
    """
    query = db.query(FinancialTransaction)

    if type_filter:
        query = query.filter(FinancialTransaction.type == type_filter)

    if category:
        query = query.filter(FinancialTransaction.category == category)

    if start_date:
        query = query.filter(FinancialTransaction.date >= start_date)

    if end_date:
        query = query.filter(FinancialTransaction.date <= end_date)

    transactions = query.order_by(FinancialTransaction.date.desc()).offset(skip).limit(limit).all()
    return transactions

@router.get("/summary/overview", response_model=FinancialSummaryResponse)
def get_financial_summary(
    db: Session = Depends(get_db),
):
    """
    Obtener resumen financiero general: balance total, ingresos y gastos.
    Endpoint público para dashboards de reportes.
    """
    # Calcular totales
    total_income = db.query(func.coalesce(func.sum(FinancialTransaction.amount), 0)).filter(
        FinancialTransaction.type == "INCOME"
    ).scalar()

    total_expenses = db.query(func.coalesce(func.sum(FinancialTransaction.amount), 0)).filter(
        FinancialTransaction.type == "EXPENSE"
    ).scalar()

    balance = float(total_income) - float(total_expenses)

    return FinancialSummaryResponse(
        total_income=float(total_income),
        total_expense=float(total_expenses),
        balance=balance,
        transaction_count=db.query(FinancialTransaction).count(),
    )

@router.post("", response_model=FinancialTransactionResponse, status_code=201)
def create_transaction(
    data: FinancialTransactionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Crear una transaccion financiera desde el dashboard."""
    transaction = FinancialTransaction(
        type=data.type,
        amount=data.amount,
        category=data.category,
        description=data.description,
        date=data.date,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.get("/{transaction_id}", response_model=FinancialTransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Obtener detalle de una transacción."""
    transaction = db.query(FinancialTransaction).filter(
        FinancialTransaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    return transaction

@router.patch("/{transaction_id}", response_model=FinancialTransactionResponse)
def update_transaction(
    transaction_id: int,
    data: FinancialTransactionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Actualizar transacción financiera."""
    transaction = db.query(FinancialTransaction).filter(
        FinancialTransaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    if data.type is not None:
        transaction.type = data.type
    if data.amount is not None:
        transaction.amount = data.amount
    if data.category is not None:
        transaction.category = data.category
    if data.description is not None:
        transaction.description = data.description
    if data.date is not None:
        transaction.date = data.date

    transaction.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(transaction)
    return transaction

@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Eliminar transacción financiera."""
    transaction = db.query(FinancialTransaction).filter(
        FinancialTransaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    db.delete(transaction)
    db.commit()
    return None

@router.get("/summary/dashboard", response_model=FinancialSummaryResponse)
def get_financial_summary_dashboard(
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """
    Obtener resumen de finanzas (totales, balance, conteo).

    Parámetros opcionales:
    - start_date: Filtrar desde fecha
    - end_date: Filtrar hasta fecha
    """
    query = db.query(FinancialTransaction)

    if start_date:
        query = query.filter(FinancialTransaction.date >= start_date)

    if end_date:
        query = query.filter(FinancialTransaction.date <= end_date)

    # Totales por tipo
    income_result = db.query(func.coalesce(func.sum(FinancialTransaction.amount), 0)).filter(
        and_(
            FinancialTransaction.type == "INCOME",
            *(
                [FinancialTransaction.date >= start_date] if start_date else []
            ) + (
                [FinancialTransaction.date <= end_date] if end_date else []
            )
        )
    ).scalar()

    expense_result = db.query(func.coalesce(func.sum(FinancialTransaction.amount), 0)).filter(
        and_(
            FinancialTransaction.type == "EXPENSE",
            *(
                [FinancialTransaction.date >= start_date] if start_date else []
            ) + (
                [FinancialTransaction.date <= end_date] if end_date else []
            )
        )
    ).scalar()

    total_income = float(income_result) if income_result else 0.0
    total_expense = float(expense_result) if expense_result else 0.0
    balance = total_income - total_expense

    transaction_count = query.count()

    return FinancialSummaryResponse(
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        transaction_count=transaction_count,
        date_range_start=start_date,
        date_range_end=end_date,
    )
