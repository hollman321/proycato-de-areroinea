"""
Referencia IATA / aeropuertos (datos maestros importados, p. ej. OurAirports).

No reemplaza la tabla operativa `pasajeros`; sirve para enriquecer, buscar códigos y validar ubicaciones.
"""

from __future__ import annotations

import time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_active_user
from models.airport import Airport
from models.user import User
from schemas.analytics import AirportReference, GeoValidateResponse
from services import geo_reference_service

router = APIRouter(prefix="/reference", tags=["Reference IATA"])


@router.get("/airports", response_model=List[AirportReference])
async def buscar_aeropuertos(
    response: Response,
    q: Optional[str] = Query(None, description="Nombre, ciudad o código IATA/ICAO"),
    country_iso: Optional[str] = Query(None, min_length=2, max_length=2),
    limit: int = Query(25, ge=1, le=200),
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    t0 = time.perf_counter()
    query = db.query(Airport)
    if country_iso:
        query = query.filter(Airport.country_iso == country_iso.strip().upper())
    if q and q.strip():
        qs = q.strip()
        term = f"%{qs}%"
        parts = [Airport.name.ilike(term), Airport.city.ilike(term)]
        if len(qs) == 3:
            parts.append(Airport.iata_code == qs.upper())
        if len(qs) == 4:
            parts.append(Airport.icao_code == qs.upper())
        query = query.filter(or_(*parts))
    rows = query.limit(limit).all()
    if time.perf_counter() - t0 > 2.0:
        response.headers["X-SkyAnalytics-Slow-Query"] = "1"
    return rows


@router.get("/airports/by-iata/{iata}", response_model=AirportReference)
async def aeropuerto_por_iata(
    iata: str,
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    code = iata.strip().upper()
    if len(code) != 3:
        raise HTTPException(status_code=400, detail="Código IATA debe tener 3 caracteres")
    row = db.query(Airport).filter(Airport.iata_code == code).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"No hay aeropuerto con IATA {code}")
    return row


@router.get("/geo/validate", response_model=GeoValidateResponse)
async def validar_ubicacion(
    ciudad: str = Query(..., min_length=1, max_length=200),
    country_iso: str = Query(..., min_length=2, max_length=2),
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        data = geo_reference_service.validar_ciudad_pais_iso(db, ciudad, country_iso)
        return GeoValidateResponse(**data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
