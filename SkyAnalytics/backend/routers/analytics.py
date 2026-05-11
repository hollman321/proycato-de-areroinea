"""Agregados y listados optimizados para dashboards analíticos."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_active_user
from models.user import User
from schemas.analytics import CursorPasajerosResponse, MesCantidad, PaisCantidad, ResumenAnalytics
from schemas.pasajero import PasajeroResponse
from services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/resumen", response_model=ResumenAnalytics)
async def analytics_resumen(_: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    data = analytics_service.resumen(db)
    return ResumenAnalytics(**data)


@router.get("/por-pais", response_model=List[PaisCantidad])
async def analytics_por_pais(
    limit: int = Query(15, ge=1, le=100),
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return [PaisCantidad(**row) for row in analytics_service.por_pais(db, limit=limit)]


@router.get("/tendencia-mensual", response_model=List[MesCantidad])
async def analytics_tendencia(
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return [MesCantidad(**row) for row in analytics_service.tendencia_mensual(db)]


@router.get("/pasajeros", response_model=CursorPasajerosResponse)
async def analytics_pasajeros_cursor(
    cursor: Optional[int] = Query(None, description="Último id visto; devuelve filas con id mayor"),
    limit: int = Query(50, ge=1, le=1000),
    q: Optional[str] = Query(None, description="Búsqueda por nombre o correo (ILIKE)"),
    pais: Optional[List[str]] = Query(None),
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    items, next_cursor, has_more = analytics_service.list_pasajeros_keyset(
        db,
        cursor_id=cursor,
        limit=limit,
        q=q,
        paises=pais,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )
    return CursorPasajerosResponse(
        items=[PasajeroResponse.model_validate(p) for p in items],
        next_cursor=next_cursor,
        has_more=has_more,
        page_size=len(items),
    )
