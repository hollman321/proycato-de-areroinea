"""Respuestas del módulo de analítica (cursor, KPIs, series temporales)."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from schemas.pasajero import PasajeroResponse


class CursorPasajerosResponse(BaseModel):
    """
    Paginación por cursor sobre `id` (eficiente con millones de filas).

    Evita OFFSET grande que en PostgreSQL recorre muchas filas innecesarias.
    """

    items: List[PasajeroResponse]
    next_cursor: Optional[int] = None
    has_more: bool
    page_size: int


class PaisCantidad(BaseModel):
    pais: str
    cantidad: int


class MesCantidad(BaseModel):
    mes: date
    cantidad: int


class ResumenAnalytics(BaseModel):
    total_pasajeros: int
    paises_unicos: int
    ciudades_unicas: int
