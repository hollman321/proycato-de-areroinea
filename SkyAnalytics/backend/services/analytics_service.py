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

from sqlalchemy import case, func, text
from sqlalchemy.orm import Session

from models.airport import Airport
from models.pasajero import Pasajero
from models.pasajero import MillasAcumuladas, Transaccion
from services import categoria_service

# Ventana de “cobertura activa comercial” (especificación negocio)
COBERTURA_ACTIVA_DIAS = 30
DASHBOARD_SAMPLE_ROWS = 100_000


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

    total, paises_cobertura_activa_30d, paises_historico_distintos, ciudades_nodos_urbanos = (
        db.query(
            func.count(Pasajero.id),
            func.count(func.distinct(Pasajero.pais)).filter(Pasajero.fecha_registro >= corte_activo),
            func.count(func.distinct(Pasajero.pais)),
            func.count(func.distinct(Pasajero.ciudad)),
        ).one()
    )

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


def _perfil_comercial(
    pasajero: Pasajero,
    millas: Optional[MillasAcumuladas],
    vuelos: int,
) -> dict:
    millas_totales = int(millas.millas_totales if millas else 0)
    dinero_gastado = float(millas.dinero_gastado if millas else 0)
    categoria = categoria_service.calcular_categoria(
        millas_totales,
        dinero_gastado,
        pasajero.pais,
        vuelos,
    )
    return {
        "categoria": categoria,
        "descuento": categoria_service.calcular_nivel_descuento(
            millas_totales,
            dinero_gastado,
            vuelos,
        ),
        "millas_totales": millas_totales,
        "dinero_gastado": dinero_gastado,
    }


def resumen_dashboard_rapido(db: Session) -> dict:
    """KPIs rápidos para el dashboard sobre bases masivas."""
    hoy = date.today()
    corte_activo = hoy - timedelta(days=COBERTURA_ACTIVA_DIAS)
    row = db.execute(
        text(
            """
            WITH bounds AS (
                SELECT COALESCE(MAX(id), 0) AS total FROM pasajeros
            ),
            sample AS (
                SELECT pais, ciudad, fecha_registro
                FROM pasajeros, bounds
                WHERE id <= LEAST(bounds.total, :sample_rows)
            )
            SELECT
                bounds.total,
                COUNT(DISTINCT sample.pais) FILTER (WHERE sample.fecha_registro >= :corte_activo),
                COUNT(DISTINCT sample.pais),
                COUNT(DISTINCT sample.ciudad)
            FROM bounds
            LEFT JOIN sample ON true
            GROUP BY bounds.total
            """
        ),
        {"sample_rows": DASHBOARD_SAMPLE_ROWS, "corte_activo": corte_activo},
    ).one()

    return {
        "total_pasajeros": int(row[0] or 0),
        "paises_cobertura_activa_30d": int(row[1] or 0),
        "paises_historico_distintos": int(row[2] or 0),
        "ciudades_nodos_urbanos": int(row[3] or 0),
        "cobertura_activa_dias": COBERTURA_ACTIVA_DIAS,
        "fecha_consulta": hoy,
        "generated_at": datetime.now(timezone.utc),
    }


def por_pais_dashboard_rapido(db: Session, limit: int = 15) -> List[dict]:
    rows = db.execute(
        text(
            """
            WITH bounds AS (
                SELECT COALESCE(MAX(id), 0) AS total FROM pasajeros
            )
            SELECT pais, COUNT(*) AS cantidad
            FROM pasajeros, bounds
            WHERE id <= LEAST(bounds.total, :sample_rows)
              AND pais IS NOT NULL
            GROUP BY pais
            ORDER BY COUNT(*) DESC
            LIMIT :limit
            """
        ),
        {"sample_rows": DASHBOARD_SAMPLE_ROWS, "limit": max(1, min(limit, 100))},
    ).all()
    return [{"pais": pais, "cantidad": int(cantidad)} for pais, cantidad in rows]


def tendencia_mensual_dashboard_rapido(db: Session) -> List[dict]:
    rows = db.execute(
        text(
            """
            WITH bounds AS (
                SELECT COALESCE(MAX(id), 0) AS total FROM pasajeros
            )
            SELECT date_trunc('month', fecha_registro)::date AS mes, COUNT(*) AS cantidad
            FROM pasajeros, bounds
            WHERE id <= LEAST(bounds.total, :sample_rows)
            GROUP BY mes
            ORDER BY mes ASC
            """
        ),
        {"sample_rows": DASHBOARD_SAMPLE_ROWS},
    ).all()
    return [{"mes": mes, "cantidad": int(cantidad)} for mes, cantidad in rows]


def distribucion_categorias(db: Session) -> List[dict]:
    vuelos_sq = (
        db.query(
            Transaccion.pasajero_id.label("pasajero_id"),
            func.count(Transaccion.id).label("vuelos"),
        )
        .group_by(Transaccion.pasajero_id)
        .subquery()
    )

    millas = func.coalesce(MillasAcumuladas.millas_totales, 0)
    gasto = func.coalesce(MillasAcumuladas.dinero_gastado, 0)
    vuelos = func.coalesce(vuelos_sq.c.vuelos, 0)

    categoria_expr = case(
        ( (millas >= 120000) | (gasto >= 20000) | (vuelos >= 80), "VIP"),
        ( (millas >= 80000) | (gasto >= 12000) | (vuelos >= 50), "Empresarial"),
        ( (millas >= 50000) | (gasto >= 7500) | (vuelos >= 30), "Ejecutivo"),
        ( (millas >= 25000) | (gasto >= 3500) | (vuelos >= 15), "Premium"),
        ( (millas >= 5000) | (gasto >= 750) | (vuelos >= 3), "Frecuente"),
        else_="Nuevo",
    ).label("categoria")

    grouped = (
        db.query(categoria_expr, func.count(MillasAcumuladas.pasajero_id).label("cantidad"))
        .outerjoin(vuelos_sq, vuelos_sq.c.pasajero_id == MillasAcumuladas.pasajero_id)
        .group_by(categoria_expr)
        .all()
    )

    orden = ["Nuevo", "Frecuente", "Premium", "Ejecutivo", "Empresarial", "VIP"]
    conteo = {categoria: int(cantidad or 0) for categoria, cantidad in grouped}
    total = int(db.query(func.max(Pasajero.id)).scalar() or 0)
    perfilados = int(db.query(func.count(MillasAcumuladas.pasajero_id)).scalar() or 0)
    conteo["Nuevo"] = max(0, total - perfilados)
    return [
        {"categoria": categoria, "cantidad": conteo[categoria]}
        for categoria in orden
        if conteo.get(categoria, 0) > 0
    ]


def rutas_mas_populares(db: Session, limit: int = 10) -> List[dict]:
    """Rutas operativas estimadas desde ciudad/pais y compras registradas."""
    limit = max(1, min(limit, 50))
    rows = (
        db.query(
            Pasajero.ciudad,
            Pasajero.pais,
            func.count(Transaccion.id).label("cantidad"),
            func.coalesce(func.sum(Transaccion.monto), 0).label("ingresos"),
        )
        .select_from(Transaccion)
        .join(Pasajero, Pasajero.id == Transaccion.pasajero_id)
        .group_by(Pasajero.ciudad, Pasajero.pais)
        .order_by(func.count(Transaccion.id).desc(), func.count(Pasajero.id).desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "origen": "Global",
            "destino": f"{ciudad}, {pais}",
            "cantidad": int(cantidad or 0),
            "ingresos": float(ingresos or 0),
        }
        for ciudad, pais, cantidad, ingresos in rows
    ]


def usuarios_con_mas_vuelos(db: Session, limit: int = 10) -> List[dict]:
    limit = max(1, min(limit, 50))
    rows = (
        db.query(Pasajero, MillasAcumuladas)
        .join(MillasAcumuladas, MillasAcumuladas.pasajero_id == Pasajero.id)
        .order_by(MillasAcumuladas.dinero_gastado.desc(), MillasAcumuladas.millas_totales.desc())
        .limit(limit)
        .all()
    )
    usuarios = []
    for pasajero, millas in rows:
        vuelos_int = int(
            db.query(func.count(Transaccion.id))
            .filter(Transaccion.pasajero_id == pasajero.id)
            .scalar()
            or 0
        )
        perfil = _perfil_comercial(pasajero, millas, vuelos_int)
        usuarios.append(
            {
                "pasajero_id": pasajero.id,
                "nombre_completo": pasajero.nombre_completo,
                "correo": pasajero.correo,
                "pais": pasajero.pais,
                "vuelos": vuelos_int,
                "millas_totales": perfil["millas_totales"],
                "dinero_gastado": perfil["dinero_gastado"],
                "categoria": perfil["categoria"],
                "descuento": perfil["descuento"],
            }
        )
    return usuarios


def ingresos_por_pais(db: Session, limit: int = 15) -> List[dict]:
    rows = (
        db.query(Pasajero.pais, func.coalesce(func.sum(Transaccion.monto), 0).label("ingresos"))
        .join(Transaccion, Transaccion.pasajero_id == Pasajero.id)
        .group_by(Pasajero.pais)
        .order_by(func.sum(Transaccion.monto).desc())
        .limit(max(1, min(limit, 100)))
        .all()
    )
    return [{"pais": pais, "ingresos": float(ingresos or 0)} for pais, ingresos in rows]


def aeropuertos_mas_usados(db: Session, limit: int = 10) -> List[dict]:
    rows = (
        db.query(
            Airport.iata_code,
            Airport.name,
            Airport.city,
            Airport.country_iso,
            func.count(Pasajero.id).label("usos"),
        )
        .join(Pasajero, func.lower(Pasajero.ciudad) == func.lower(Airport.city))
        .filter(Airport.iata_code.isnot(None))
        .group_by(Airport.iata_code, Airport.name, Airport.city, Airport.country_iso)
        .order_by(func.count(Pasajero.id).desc())
        .limit(max(1, min(limit, 50)))
        .all()
    )
    return [
        {
            "codigo": codigo or "",
            "nombre": nombre,
            "ciudad": ciudad,
            "pais": pais,
            "usos_estimados": int(usos or 0),
        }
        for codigo, nombre, ciudad, pais, usos in rows
    ]


def analytics_avanzado(db: Session) -> dict:
    return {
        "distribucion_categorias": distribucion_categorias(db),
        "rutas_mas_populares": rutas_mas_populares(db),
        "usuarios_con_mas_vuelos": usuarios_con_mas_vuelos(db),
        "ingresos_por_pais": ingresos_por_pais(db),
        "aeropuertos_mas_usados": aeropuertos_mas_usados(db),
    }


def analytics_avanzado_dashboard_rapido(db: Session) -> dict:
    """Analytics para la primera carga del dashboard sin joins masivos por ciudad."""
    return {
        "distribucion_categorias": distribucion_categorias(db),
        "rutas_mas_populares": rutas_mas_populares(db, limit=10),
        "usuarios_con_mas_vuelos": usuarios_con_mas_vuelos(db, limit=10),
        "ingresos_por_pais": [],
        "aeropuertos_mas_usados": [],
    }


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


def analytics_avanzado_cached(db: Session) -> dict:
    from services import analytics_cache

    return analytics_cache.get_cached("analytics:avanzado:v1", lambda: analytics_avanzado(db))


def dashboard_payload_cached(db: Session) -> dict:
    from services import analytics_cache

    def build() -> dict:
        return {
            "resumen": {**resumen_dashboard_rapido(db), "cache_ttl_seconds": analytics_cache.cache_ttl_seconds()},
            "viajes_por_pais": por_pais_dashboard_rapido(db, limit=15),
            "tendencia_mensual": tendencia_mensual_dashboard_rapido(db),
            "avanzado": analytics_avanzado_dashboard_rapido(db),
        }

    return analytics_cache.get_cached("analytics:dashboard:v4", build)
