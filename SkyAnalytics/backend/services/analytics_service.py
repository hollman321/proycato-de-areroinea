"""
Consultas de analítica pensadas para tablas muy grandes.

Reglas SkyAnalytics (Operational Intelligence):
- Volumen total: COUNT(*) sobre `pasajeros` (cada fila es un registro de pasajero;
  si existiera `hechos_viajes`, aquí iría SUM(pasajeros) o COUNT DISTINCT por viaje).
- Cobertura activa (país): países con al menos un registro en los últimos 30 días (fecha_registro).
- Nodos urbanos: ciudades distintas con al menos un pasajero histórico.
- Top países: orden descendente por volumen; con rango de fechas, solo países con >0 en el período.
- Tendencia mensual: agrupación año-mes, orden cronológico ascendente.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Sequence, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.pasajero import Pasajero

# Ventana de “cobertura activa comercial” (especificación negocio)
COBERTURA_ACTIVA_DIAS = 30


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
    """
    KPIs del dashboard ejecutivo. Valores 0 si no hay datos en el período / tabla vacía.
    """
    hoy = date.today()
    corte_activo = hoy - timedelta(days=COBERTURA_ACTIVA_DIAS)

    total = db.query(Pasajero).count()

    paises_cobertura_activa_30d = (
        db.query(func.count(func.distinct(Pasajero.pais)))
        .filter(Pasajero.fecha_registro >= corte_activo)
        .scalar()
    ) or 0

    paises_historico_distintos = db.query(func.count(func.distinct(Pasajero.pais))).scalar() or 0

    ciudades_nodos_urbanos = db.query(func.count(func.distinct(Pasajero.ciudad))).scalar() or 0

    return {
        "total_pasajeros": int(total),
        "paises_cobertura_activa_30d": int(paises_cobertura_activa_30d),
        "paises_historico_distintos": int(paises_historico_distintos),
        "ciudades_nodos_urbanos": int(ciudades_nodos_urbanos),
        "cobertura_activa_dias": COBERTURA_ACTIVA_DIAS,
        "fecha_consulta": hoy,
        "generated_at": datetime.now(timezone.utc),
    }


def por_pais(
    db: Session,
    limit: int = 15,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
) -> List[dict]:
    """
    Top países por volumen. Con filtro de fechas, excluye países sin actividad en el período (GROUP BY).
    """
    limit = max(1, min(limit, 100))
    q = db.query(Pasajero.pais, func.count(Pasajero.id).label("cantidad"))
    if fecha_inicio is not None:
        q = q.filter(Pasajero.fecha_registro >= fecha_inicio)
    if fecha_fin is not None:
        q = q.filter(Pasajero.fecha_registro <= fecha_fin)
    rows = (
        q.group_by(Pasajero.pais)
        .order_by(func.count(Pasajero.id).desc())
        .limit(limit)
        .all()
    )
    return [{"pais": r[0], "cantidad": int(r[1])} for r in rows if r[0] is not None]


def tendencia_mensual(db: Session) -> List[dict]:
    """Serie mensual ordenada cronológicamente (año-mes), no por volumen."""
    mes = func.date_trunc("month", Pasajero.fecha_registro).label("mes")
    rows = (
        db.query(mes, func.count(Pasajero.id).label("cantidad"))
        .group_by(mes)
        .order_by(mes.asc())
        .all()
    )
    out: List[dict] = []
    for m, c in rows:
        d = m.date() if hasattr(m, "date") else m
        out.append({"mes": d, "cantidad": int(c)})
    return out


def resumen_cached(db: Session) -> dict:
    """Mismo cálculo que `resumen` pero con ventana de cache 30s (ver `analytics_cache`)."""
    from services import analytics_cache

    return analytics_cache.get_cached("analytics:resumen:v1", lambda: resumen(db))


def por_pais_cached(
    db: Session,
    limit: int,
    fecha_inicio: Optional[date],
    fecha_fin: Optional[date],
) -> List[dict]:
    from services import analytics_cache

    key = f"analytics:por_pais:{limit}:{fecha_inicio}:{fecha_fin}"
    return analytics_cache.get_cached(key, lambda: por_pais(db, limit, fecha_inicio, fecha_fin))


def tendencia_mensual_cached(db: Session) -> List[dict]:
    from services import analytics_cache

    return analytics_cache.get_cached("analytics:tendencia:v1", lambda: tendencia_mensual(db))
