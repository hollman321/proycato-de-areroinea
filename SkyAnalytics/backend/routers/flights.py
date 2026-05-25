"""Busqueda avanzada de oportunidades de vuelo sobre datos operativos actuales."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_active_user
from models.airport import Airport
from models.pasajero import MillasAcumuladas, Pasajero, Transaccion
from models.user import User
from services import categoria_service

router = APIRouter(prefix="/flights", tags=["Flights"])


@router.get("/search")
def search_flights(
    aeropuerto_salida: Optional[str] = Query(None),
    aeropuerto_llegada: Optional[str] = Query(None),
    pais_origen: Optional[str] = Query(None),
    pais_destino: Optional[str] = Query(None),
    fecha_salida: Optional[date] = Query(None),
    fecha_regreso: Optional[date] = Query(None),
    escalas: Optional[int] = Query(None, ge=0, le=4),
    clase_vuelo: Optional[str] = Query(None),
    precio_min: Optional[float] = Query(None, ge=0),
    precio_max: Optional[float] = Query(None, ge=0),
    categoria_pasajero: Optional[str] = Query(None),
    aerolinea: Optional[str] = Query(None),
    viajes_mas_frecuentes: bool = Query(False),
    usuarios_vip: bool = Query(False),
    viajeros_frecuentes: bool = Query(False),
    limit: int = Query(25, ge=1, le=100),
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Devuelve resultados dinamicos derivados de pasajeros, compras y aeropuertos.

    El proyecto todavia no tiene una tabla `flights`; por eso este endpoint opera como
    buscador analitico de demanda: destino, pasajero, frecuencia, precio historico,
    descuento aplicable y aeropuertos asociados.
    """
    query = (
        db.query(
            Pasajero,
            MillasAcumuladas,
            func.count(Transaccion.id).label("vuelos"),
            func.coalesce(func.sum(Transaccion.monto), 0).label("total_gastado"),
        )
        .outerjoin(MillasAcumuladas, MillasAcumuladas.pasajero_id == Pasajero.id)
        .outerjoin(Transaccion, Transaccion.pasajero_id == Pasajero.id)
    )

    if pais_destino:
        query = query.filter(Pasajero.pais.ilike(f"%{pais_destino}%"))
    if pais_origen:
        query = query.filter(Pasajero.pais.ilike(f"%{pais_origen}%"))
    if fecha_salida:
        query = query.filter(Pasajero.fecha_registro >= fecha_salida)
    if fecha_regreso:
        query = query.filter(Pasajero.fecha_registro <= fecha_regreso)
    if precio_min is not None:
        query = query.filter(Transaccion.monto >= precio_min)
    if precio_max is not None:
        query = query.filter(Transaccion.monto <= precio_max)

    rows = (
        query.group_by(Pasajero.id, MillasAcumuladas.id)
        .order_by(func.count(Transaccion.id).desc(), func.coalesce(func.sum(Transaccion.monto), 0).desc())
        .limit(limit * 3)
        .all()
    )

    airport_codes = [code.upper() for code in [aeropuerto_salida, aeropuerto_llegada] if code]
    airports = {}
    if airport_codes:
        for airport in db.query(Airport).filter(Airport.iata_code.in_(airport_codes)).all():
            airports[airport.iata_code] = airport

    results: List[dict] = []
    for pasajero, millas, vuelos, total_gastado in rows:
        vuelos_int = int(vuelos or 0)
        millas_totales = int(millas.millas_totales if millas else 0)
        dinero_gastado = float(total_gastado or (millas.dinero_gastado if millas else 0))
        categoria = categoria_service.calcular_categoria(
            millas_totales,
            dinero_gastado,
            pasajero.pais,
            vuelos_int,
        )
        descuento = categoria_service.calcular_nivel_descuento(
            millas_totales,
            dinero_gastado,
            vuelos_int,
        )
        if categoria_pasajero and categoria.lower() != categoria_pasajero.lower():
            continue
        if usuarios_vip and categoria != "VIP":
            continue
        if viajeros_frecuentes and categoria not in {"Frecuente", "Premium", "Ejecutivo", "Empresarial", "VIP"}:
            continue
        if viajes_mas_frecuentes and vuelos_int < 3:
            continue

        precio_estimado = round(max(120.0, dinero_gastado / max(vuelos_int, 1)), 2)
        salida = airports.get((aeropuerto_salida or "").upper())
        llegada = airports.get((aeropuerto_llegada or "").upper())
        results.append(
            {
                "pasajero_id": pasajero.id,
                "pasajero": pasajero.nombre_completo,
                "categoria": categoria,
                "pais_origen": pais_origen or pasajero.pais,
                "pais_destino": pais_destino or pasajero.pais,
                "ciudad_destino": pasajero.ciudad,
                "aeropuerto_salida": salida.iata_code if salida else aeropuerto_salida,
                "aeropuerto_llegada": llegada.iata_code if llegada else aeropuerto_llegada,
                "clase_vuelo": clase_vuelo or ("Ejecutiva" if categoria in {"Ejecutivo", "Empresarial", "VIP"} else "Economica"),
                "escalas": escalas if escalas is not None else 0,
                "aerolinea": aerolinea or "SkyAnalytics Partner",
                "vuelos_historicos": vuelos_int,
                "precio_estimado": precio_estimado,
                "descuento_checkout": descuento,
                "cashback_estimado": round(precio_estimado * descuento["cashback_porcentaje"] / 100, 2),
                "millas_totales": millas_totales,
            }
        )
        if len(results) >= limit:
            break

    return {"items": results, "total": len(results), "filters_applied": {
        "aeropuerto_salida": aeropuerto_salida,
        "aeropuerto_llegada": aeropuerto_llegada,
        "pais_origen": pais_origen,
        "pais_destino": pais_destino,
        "fecha_salida": fecha_salida,
        "fecha_regreso": fecha_regreso,
        "escalas": escalas,
        "clase_vuelo": clase_vuelo,
        "precio_min": precio_min,
        "precio_max": precio_max,
        "categoria_pasajero": categoria_pasajero,
        "aerolinea": aerolinea,
    }}
