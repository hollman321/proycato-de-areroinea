"""
CRUD de operaciones comerciales y financieras.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_active_user
from models.operation import Operation
from models.pasajero import Pasajero
from models.user import User

router = APIRouter(prefix="/operations", tags=["Operations"])


class OperationPayload(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    description: Optional[str] = Field(None, max_length=500)
    client_id: int = Field(..., gt=0)
    status: str = Field(
        "PENDING", pattern="^(PENDING|IN_PROGRESS|COMPLETED|CANCELLED)$"
    )
    category: Optional[str] = Field(None, max_length=100)
    type: str = Field("INCOME", pattern="^(INCOME|EXPENSE)$")
    amount: float = Field(..., ge=0)


class OperationUpdatePayload(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=150)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(
        None, pattern="^(PENDING|IN_PROGRESS|COMPLETED|CANCELLED)$"
    )
    category: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = Field(None, pattern="^(INCOME|EXPENSE)$")
    amount: Optional[float] = Field(None, ge=0)


def _operation_to_dict(operation: Operation) -> Dict[str, Any]:
    return {
        "id": operation.id,
        "title": operation.title,
        "description": operation.description,
        "client_id": operation.client_id,
        "status": operation.status,
        "category": operation.category,
        "type": operation.type,
        "amount": operation.amount,
        "created_at": (
            operation.created_at.isoformat() if operation.created_at else None
        ),
        "updated_at": (
            operation.updated_at.isoformat() if operation.updated_at else None
        ),
    }


@router.get("/")
async def list_operations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    client_id: Optional[int] = Query(None, gt=0),
    status: Optional[str] = Query(
        None, pattern="^(PENDING|IN_PROGRESS|COMPLETED|CANCELLED)$"
    ),
    operation_type: Optional[str] = Query(
        None, alias="type", pattern="^(INCOME|EXPENSE)$"
    ),
) -> Dict[str, Any]:
    query = db.query(Operation)
    if client_id:
        query = query.filter(Operation.client_id == client_id)
    if status:
        query = query.filter(Operation.status == status)
    if operation_type:
        query = query.filter(Operation.type == operation_type)

    total = query.count()
    operations = (
        query.order_by(Operation.created_at.desc()).offset(offset).limit(limit).all()
    )
    return {
        "operations": [_operation_to_dict(item) for item in operations],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/")
async def create_operation(
    payload: OperationPayload,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    client = db.query(Pasajero).filter(Pasajero.id == payload.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado para la operación",
        )

    operation = Operation(**payload.dict())
    db.add(operation)
    db.commit()
    db.refresh(operation)
    return _operation_to_dict(operation)


@router.get("/{operation_id}")
async def get_operation(
    operation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    operation = db.query(Operation).filter(Operation.id == operation_id).first()
    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Operación no encontrada"
        )
    return _operation_to_dict(operation)


@router.put("/{operation_id}")
async def update_operation(
    operation_id: int,
    payload: OperationUpdatePayload,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    operation = db.query(Operation).filter(Operation.id == operation_id).first()
    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Operación no encontrada"
        )

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(operation, field, value)

    db.add(operation)
    db.commit()
    db.refresh(operation)
    return _operation_to_dict(operation)


@router.delete("/{operation_id}")
async def delete_operation(
    operation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    operation = db.query(Operation).filter(Operation.id == operation_id).first()
    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Operación no encontrada"
        )

    db.delete(operation)
    db.commit()
    return {"success": True, "id": operation_id}
