"""
Consultas de analítica pensadas para tablas muy grandes.

Usamos cursor por `id` ascendente en lugar de OFFSET profundo.
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional, Sequence, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.pasajero import Pasajero


def list_pasajeros_keyset(
    db: Session,
    *,
    cursor_id: Optional[int] = None,
    limit: int = 50,
    q: Optional[str] = None,
    paises: Optional[Sequence[str]] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
) -> Tuple[List[Pasajero], Optional[int], bool]:
    query = db.query(Pasajero)
    if cursor_id is not None:
        query = query.filter(Pasajero.id > cursor_id)
    if paises:
        query = query.filter(Pasajero.pais.in_(list(paises)))
    if fecha_inicio is not None:
        query = query.filter(Pasajero.fecha_registro >= fecha_inicio)
    if fecha_fin is not None:
        query = query.filter(Pasajero.fecha_registro <= fecha_fin)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            (Pasajero.nombre_completo.ilike(like)) | (Pasajero.correo.ilike(like))
        )

    limit = max(1, min(limit, 1000))
    rows = query.order_by(Pasajero.id.asc()).limit(limit + 1).all()
    has_more = len(rows) > limit
    items = rows[:limit]
    next_cursor = items[-1].id if has_more and items else None
    return items, next_cursor, has_more


def resumen(db: Session) -> dict:
    total = db.query(Pasajero).count()
    paises_unicos = db.query(func.count(func.distinct(Pasajero.pais))).scalar() or 0
    ciudades_unicas = db.query(func.count(func.distinct(Pasajero.ciudad))).scalar() or 0
    return {
        "total_pasajeros": total,
        "paises_unicos": paises_unicos,
        "ciudades_unicas": ciudades_unicas,
    }


def por_pais(db: Session, limit: int = 15) -> List[dict]:
    limit = max(1, min(limit, 100))
    rows = (
        db.query(Pasajero.pais, func.count(Pasajero.id).label("cantidad"))
        .group_by(Pasajero.pais)
        .order_by(func.count(Pasajero.id).desc())
        .limit(limit)
        .all()
    )
    return [{"pais": r[0], "cantidad": int(r[1])} for r in rows]


def tendencia_mensual(db: Session) -> List[dict]:
    mes = func.date_trunc("month", Pasajero.fecha_registro).label("mes")
    rows = (
        db.query(mes, func.count(Pasajero.id).label("cantidad"))
        .group_by(mes)
        .order_by(mes)
        .all()
    )
    out = []
    for m, c in rows:
        d = m.date() if hasattr(m, "date") else m
        out.append({"mes": d, "cantidad": int(c)})
    return out
