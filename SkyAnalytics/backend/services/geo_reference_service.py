"""
Validación ciudad ↔ país ISO usando la tabla `airports` (referencia IATA/OurAirports).

Nota para juniors: `pasajeros.pais` hoy es nombre libre (ej. \"España\"); para validación estricta
convendría almacenar `country_iso` en pasajeros o una tabla puente país→ISO.
"""

from __future__ import annotations

from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.airport import Airport


def validar_ciudad_pais_iso(db: Session, ciudad: str, country_iso: str) -> dict:
    ciudad_limpia = (ciudad or "").strip()
    iso = (country_iso or "").strip().upper()
    if len(iso) != 2:
        raise ValueError("country_iso debe ser código ISO 3166-1 alpha-2 (2 letras)")

    filtro = (Airport.country_iso == iso) & (Airport.city.ilike(f"%{ciudad_limpia}%"))
    total = db.query(func.count(Airport.id)).filter(filtro).scalar() or 0
    muestra = (
        db.query(Airport)
        .filter(filtro)
        .limit(5)
        .all()
    )
    iatas: List[str] = []
    for a in muestra:
        if a.iata_code:
            iatas.append(a.iata_code)
    return {
        "ciudad": ciudad_limpia,
        "country_iso": iso,
        "match_count": int(total),
        "consistente": total > 0,
        "muestra_iata": iatas[:5],
    }
