"""Respuestas del módulo de analítica (cursor, KPIs, series temporales)."""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

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


class CategoriaCantidad(BaseModel):
    categoria: str
    cantidad: int


class RutaPopular(BaseModel):
    origen: str
    destino: str
    cantidad: int
    ingresos: float = 0


class TopUsuario(BaseModel):
    pasajero_id: int
    nombre_completo: str
    correo: str
    pais: str
    vuelos: int
    millas_totales: int
    dinero_gastado: float
    categoria: str
    descuento: dict


class AirportUsage(BaseModel):
    codigo: str
    nombre: str
    ciudad: Optional[str] = None
    pais: str
    usos_estimados: int


class IngresoPais(BaseModel):
    pais: str
    ingresos: float


class AnalyticsAvanzado(BaseModel):
    distribucion_categorias: List[CategoriaCantidad]
    rutas_mas_populares: List[RutaPopular]
    usuarios_con_mas_vuelos: List[TopUsuario]
    ingresos_por_pais: List[IngresoPais]
    aeropuertos_mas_usados: List[AirportUsage]


class ResumenAnalytics(BaseModel):
    """KPIs alineados a reglas SkyAnalytics (caché 30s aplicada en el router)."""

    total_pasajeros: int
    paises_cobertura_activa_30d: int = Field(
        ..., description="Países con ≥1 pasajero en los últimos 30 días (fecha_registro)"
    )
    paises_historico_distintos: int = Field(..., description="Países distintos en toda la historia cargada")
    ciudades_nodos_urbanos: int = Field(..., description="Ciudades distintas con al menos un pasajero")
    cobertura_activa_dias: int = 30
    fecha_consulta: date
    generated_at: datetime
    cache_ttl_seconds: int = 30


class AirportReference(BaseModel):
    """Registro de la tabla de referencia IATA / OurAirports."""

    id: int
    iata_code: Optional[str] = None
    icao_code: Optional[str] = None
    name: str
    city: Optional[str] = None
    country_iso: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    airport_type: Optional[str] = None

    class Config:
        from_attributes = True


class GeoValidateResponse(BaseModel):
    """Validación ligera ciudad ↔ país ISO contra referencia de aeropuertos."""

    ciudad: str
    country_iso: str
    match_count: int
    consistente: bool
    muestra_iata: List[str] = Field(default_factory=list, description="Hasta 5 códigos IATA de ejemplo")
