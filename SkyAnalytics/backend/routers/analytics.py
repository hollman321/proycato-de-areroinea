"""Agregados y listados optimizados para dashboards analíticos."""

from __future__ import annotations

import time
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_active_user
from models.user import User
from schemas.analytics import (
    AnalyticsAvanzado,
    CategoriaCantidad,
    CursorPasajerosResponse,
    MesCantidad,
    PaisCantidad,
    RutaPopular,
    ResumenAnalytics,
    TopUsuario,
)
from schemas.pasajero import PasajeroResponse
from services import analytics_service
from services.analytics_cache import cache_ttl_seconds

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/resumen", response_model=ResumenAnalytics)
def analytics_resumen(
    response: Response,
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    t0 = time.perf_counter()
    raw = analytics_service.resumen_cached(db)
    payload = {**raw, "cache_ttl_seconds": cache_ttl_seconds()}
    if time.perf_counter() - t0 > 2.0:
        response.headers["X-SkyAnalytics-Slow-Query"] = "1"
    return ResumenAnalytics(**payload)


@router.get("/dashboard")
def analytics_dashboard(
    response: Response,
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Payload único y cacheado para pintar el dashboard con una sola llamada HTTP."""
    t0 = time.perf_counter()
    payload = analytics_service.dashboard_payload_cached(db)
    if time.perf_counter() - t0 > 2.0:
        response.headers["X-SkyAnalytics-Slow-Query"] = "1"
    return payload


@router.get("/por-pais", response_model=List[PaisCantidad])
def analytics_por_pais(
    response: Response,
    limit: int = Query(15, ge=1, le=100),
    fecha_inicio: Optional[date] = Query(
        None, description="Inicio período (inclusive) para top países"
    ),
    fecha_fin: Optional[date] = Query(None, description="Fin período (inclusive)"),
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    t0 = time.perf_counter()
    rows = analytics_service.por_pais_cached(db, limit, fecha_inicio, fecha_fin)
    if time.perf_counter() - t0 > 2.0:
        response.headers["X-SkyAnalytics-Slow-Query"] = "1"
    return [PaisCantidad(**row) for row in rows]


@router.get("/viajes-por-pais", response_model=List[PaisCantidad])
def analytics_viajes_por_pais(
    response: Response,
    limit: int = Query(15, ge=1, le=100),
    fecha_inicio: Optional[date] = Query(
        None, description="Inicio período (inclusive) para top países"
    ),
    fecha_fin: Optional[date] = Query(None, description="Fin período (inclusive)"),
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return analytics_por_pais(response, limit, fecha_inicio, fecha_fin, _, db)


@router.get("/tendencia-mensual", response_model=List[MesCantidad])
def analytics_tendencia(
    response: Response,
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    t0 = time.perf_counter()
    rows = analytics_service.tendencia_mensual_cached(db)
    if time.perf_counter() - t0 > 2.0:
        response.headers["X-SkyAnalytics-Slow-Query"] = "1"
    return [MesCantidad(**row) for row in rows]


@router.get("/categorias", response_model=List[CategoriaCantidad])
def analytics_categorias(
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    rows = analytics_service.distribucion_categorias(db)
    return [CategoriaCantidad(**row) for row in rows]


@router.get("/rutas-populares", response_model=List[RutaPopular])
def analytics_rutas_populares(
    limit: int = Query(10, ge=1, le=50),
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    rows = analytics_service.rutas_mas_populares(db, limit)
    return [RutaPopular(**row) for row in rows]


@router.get("/usuarios-top", response_model=List[TopUsuario])
def analytics_usuarios_top(
    limit: int = Query(10, ge=1, le=50),
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    rows = analytics_service.usuarios_con_mas_vuelos(db, limit)
    return [TopUsuario(**row) for row in rows]


@router.get("/avanzado", response_model=AnalyticsAvanzado)
def analytics_avanzado(
    response: Response,
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    t0 = time.perf_counter()
    raw = analytics_service.analytics_avanzado_cached(db)
    if time.perf_counter() - t0 > 2.0:
        response.headers["X-SkyAnalytics-Slow-Query"] = "1"
    return AnalyticsAvanzado(**raw)


@router.get("/pasajeros", response_model=CursorPasajerosResponse)
def analytics_pasajeros_cursor(
    cursor: Optional[int] = Query(
        None, description="Último id visto; devuelve filas con id mayor"
    ),
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
