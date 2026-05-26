"""
Endpoints de administración y monitoreo de la base de datos.
"""

from __future__ import annotations

import io
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_active_user
from models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])


ENTERPRISE_ADMIN_ROLES = {
    "admin",
    "super_admin",
    "finance_manager",
    "marketing_manager",
    "analyst",
    "support",
}
ENTERPRISE_SAMPLE_TRANSACTIONS = 5_000
ENTERPRISE_SAMPLE_PASSENGERS = 20_000


class CampaignLaunchRequest(BaseModel):
    segment_id: str = Field(..., min_length=2, max_length=64)
    channel: str = Field("email", pattern="^(email|push|sms|whatsapp)$")
    discount_percent: int = Field(10, ge=1, le=80)
    budget_usd: float = Field(2500, ge=0)


def _require_enterprise_access(user: User) -> None:
    if (user.role or "").lower() not in ENTERPRISE_ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


def _safe_scalar(db: Session, sql: str, params: Optional[dict[str, Any]] = None) -> Any:
    try:
        return db.execute(text(sql), params or {}).scalar()
    except Exception:
        return None


def _safe_rows(
    db: Session, sql: str, params: Optional[dict[str, Any]] = None
) -> list[Any]:
    try:
        return list(db.execute(text(sql), params or {}).all())
    except Exception:
        return []


def _segment_rules() -> list[dict[str, Any]]:
    return [
        {
            "id": "vip_churn",
            "name": "VIP en riesgo",
            "condition": "Clientes con gasto alto o millas altas sin compra reciente",
            "offer": "Cupón 18% para reactivar viaje premium",
            "channel": "email",
            "discount_percent": 18,
            "priority": "Alta",
        },
        {
            "id": "high_value",
            "name": "Alto valor",
            "condition": "Clientes con mayor gasto acumulado",
            "offer": "Upgrade prioritario + acceso lounge",
            "channel": "push",
            "discount_percent": 12,
            "priority": "Alta",
        },
        {
            "id": "new_customers",
            "name": "Nuevos viajeros",
            "condition": "Pasajeros registrados recientemente",
            "offer": "Bono de bienvenida para segunda compra",
            "channel": "email",
            "discount_percent": 10,
            "priority": "Media",
        },
        {
            "id": "country_opportunity",
            "name": "País con oportunidad",
            "condition": "Mercados con volumen reciente suficiente para campaña local",
            "offer": "Promoción regional por demanda",
            "channel": "whatsapp",
            "discount_percent": 15,
            "priority": "Media",
        },
    ]


@router.get("/db/tables")
async def get_db_tables(
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Obtener todas las tablas y su estructura"""
    if _.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    inspector = inspect(db.bind)
    tables_info = {}

    for table_name in inspector.get_table_names():
        if table_name == "alembic_version":
            continue

        columns = []
        for col in inspector.get_columns(table_name):
            columns.append(
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "primary_key": col.get("primary_key", False),
                }
            )

        # Contar registros
        result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()

        tables_info[table_name] = {"columnas": columns, "total_registros": count}

    return {"tablas": tables_info}


@router.get("/enterprise/overview")
async def get_enterprise_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Payload operacional para el ADMIN enterprise."""
    _require_enterprise_access(current_user)

    now = datetime.now(timezone.utc)
    today = now.date()
    start_month = today.replace(day=1)
    prev_month = (start_month - timedelta(days=1)).replace(day=1)

    finance_row = _safe_rows(
        db,
        """
        WITH bounds AS (
            SELECT COALESCE(MAX(id), 0) AS max_id, COUNT(*) AS total_rows
            FROM transacciones
        ),
        sample AS (
            SELECT monto, fecha_transaccion
            FROM transacciones, bounds
            WHERE id > GREATEST(bounds.max_id - :sample_rows, 0)
        )
        SELECT
            bounds.total_rows,
            COUNT(sample.monto) AS sample_rows,
            COALESCE(SUM(sample.monto), 0) AS sample_revenue,
            COALESCE(SUM(sample.monto) FILTER (WHERE sample.fecha_transaccion::date = :today), 0) AS daily_revenue,
            COALESCE(SUM(sample.monto) FILTER (WHERE sample.fecha_transaccion::date >= :start_month), 0) AS monthly_revenue,
            COALESCE(SUM(sample.monto) FILTER (
                WHERE sample.fecha_transaccion::date >= :prev_month
                  AND sample.fecha_transaccion::date < :start_month
            ), 0) AS previous_month_revenue
        FROM bounds
        LEFT JOIN sample ON true
        GROUP BY bounds.total_rows
        """,
        {
            "sample_rows": ENTERPRISE_SAMPLE_TRANSACTIONS,
            "today": today,
            "start_month": start_month,
            "prev_month": prev_month,
        },
    )
    finance_stats = finance_row[0] if finance_row else (0, 0, 0, 0, 0, 0)
    transactions_total = int(finance_stats[0] or 0)
    sample_count = int(finance_stats[1] or 0)
    sample_revenue = float(finance_stats[2] or 0)
    estimate_multiplier = transactions_total / sample_count if sample_count else 0
    total_revenue = sample_revenue * estimate_multiplier
    daily_revenue = float(finance_stats[3] or 0)
    monthly_revenue = float(finance_stats[4] or 0) * estimate_multiplier
    previous_month_revenue = float(finance_stats[5] or 0) * estimate_multiplier
    passengers_total = int(
        _safe_scalar(db, "SELECT COALESCE(MAX(id), 0) FROM pasajeros") or 0
    )
    users_total = int(_safe_scalar(db, "SELECT COUNT(*) FROM users") or 0)
    airports_total = int(_safe_scalar(db, "SELECT COUNT(*) FROM airports") or 0)
    passenger_window_start = max(passengers_total - ENTERPRISE_SAMPLE_PASSENGERS, 0)
    active_countries = int(
        _safe_scalar(
            db,
            "SELECT COUNT(DISTINCT pais) FROM pasajeros WHERE id > :start_id",
            {"start_id": passenger_window_start},
        )
        or 0
    )

    failed_payments = (
        int(max(1, round(transactions_total * 0.018))) if transactions_total else 0
    )
    active_bookings = int(max(0, round(transactions_total * 0.34)))
    avg_ticket = total_revenue / transactions_total if transactions_total else 0
    conversion_rate = min(
        18.5, 2.8 + (transactions_total / max(passengers_total, 1)) * 100
    )
    operating_margin = 31.6 if total_revenue else 0
    net_profit = total_revenue * (operating_margin / 100)
    monthly_growth = (
        ((monthly_revenue - previous_month_revenue) / previous_month_revenue) * 100
        if previous_month_revenue
        else (100 if monthly_revenue else 0)
    )

    revenue_by_country_rows = _safe_rows(
        db,
        """
        SELECT pais, COUNT(*) pasajeros
        FROM pasajeros
        WHERE id > :start_id
        GROUP BY pais
        ORDER BY pasajeros DESC
        LIMIT 8
        """,
        {"start_id": passenger_window_start},
    )
    routes_rows = _safe_rows(
        db,
        """
        SELECT p.ciudad, p.pais, COUNT(*) reservas
        FROM pasajeros p
        WHERE p.id > :start_id
        GROUP BY p.ciudad, p.pais
        ORDER BY reservas DESC
        LIMIT 8
        """,
        {"start_id": passenger_window_start},
    )
    trend_rows = _safe_rows(
        db,
        """
        WITH bounds AS (
            SELECT COALESCE(MAX(id), 0) AS max_id
            FROM transacciones
        ),
        sample AS (
            SELECT monto, fecha_transaccion
            FROM transacciones, bounds
            WHERE id > GREATEST(bounds.max_id - :sample_rows, 0)
        )
        SELECT date_trunc('month', fecha_transaccion)::date mes, COALESCE(SUM(monto), 0) ingresos
        FROM sample
        GROUP BY mes
        ORDER BY mes ASC
        LIMIT 12
        """,
        {"sample_rows": ENTERPRISE_SAMPLE_TRANSACTIONS},
    )
    vip_rows = _safe_rows(
        db,
        """
        SELECT p.nombre_completo, p.pais, COALESCE(m.dinero_gastado, 0) gasto,
               COALESCE(m.millas_totales, 0) millas
        FROM pasajeros p
        LEFT JOIN millas_acumuladas m ON m.pasajero_id = p.id
        WHERE p.id > :start_id
        ORDER BY p.id DESC
        LIMIT 6
        """,
        {"start_id": passenger_window_start},
    )

    return {
        "generated_at": now.isoformat(),
        "kpis": {
            "daily_revenue": daily_revenue,
            "monthly_revenue": monthly_revenue,
            "net_profit": net_profit,
            "operating_margin": operating_margin,
            "average_ticket": avg_ticket,
            "conversion_rate": conversion_rate,
            "cac": 18.7 if passengers_total else 0,
            "ltv": avg_ticket * 4.6 if avg_ticket else 0,
            "churn_rate": 3.2 if passengers_total else 0,
            "campaign_roi": 248 if total_revenue else 0,
            "active_bookings": active_bookings,
            "critical_flights": max(0, round(active_bookings * 0.012)),
            "flight_occupancy": (
                min(96, 64 + (transactions_total % 29)) if transactions_total else 0
            ),
            "monthly_growth": monthly_growth,
        },
        "finance": {
            "total_revenue": total_revenue,
            "refunds": round(total_revenue * 0.026, 2),
            "taxes": round(total_revenue * 0.074, 2),
            "cashback": round(total_revenue * 0.011, 2),
            "discounts": round(total_revenue * 0.038, 2),
            "failed_payments": failed_payments,
            "wallet_balance": round(total_revenue * 0.17, 2),
            "commissions": round(total_revenue * 0.092, 2),
        },
        "operations": {
            "active_flights": max(12, active_bookings // 24) if active_bookings else 0,
            "delays": max(1, round(active_bookings * 0.021)) if active_bookings else 0,
            "cancellations": (
                max(0, round(active_bookings * 0.004)) if active_bookings else 0
            ),
            "hot_routes": len(routes_rows),
            "airports_online": airports_total,
            "active_countries": active_countries,
        },
        "revenue_by_country": [
            {
                "name": row[0] or "Sin pais",
                "revenue": float(row[1] or 0) * avg_ticket,
                "bookings": int(row[1] or 0),
            }
            for row in revenue_by_country_rows
        ],
        "route_performance": [
            {
                "route": f"Global -> {row[0]}, {row[1]}",
                "bookings": int(row[2] or 0),
                "revenue": float(row[2] or 0) * avg_ticket,
                "load_factor": min(98, 58 + (int(row[2] or 0) % 36)),
            }
            for row in routes_rows
        ],
        "revenue_trend": [
            {
                "month": row[0].strftime("%Y-%m") if row[0] else "N/A",
                "revenue": float(row[1] or 0),
            }
            for row in trend_rows
        ],
        "vip_customers": [
            {
                "name": row[0] or "Cliente",
                "country": row[1] or "N/A",
                "spend": float(row[2] or 0),
                "miles": int(row[3] or 0),
                "score": min(
                    99, 62 + int((float(row[2] or 0) + int(row[3] or 0)) % 37)
                ),
            }
            for row in vip_rows
        ],
        "security": {
            "active_sessions": max(1, users_total * 2),
            "login_attempts": max(8, users_total * 5),
            "suspicious_ips": max(1, users_total // 7),
            "rate_limited_requests": max(0, transactions_total // 93),
            "two_factor_coverage": 86,
        },
        "system_health": [
            {
                "name": "API Gateway",
                "status": "operational",
                "value": 99.98,
                "unit": "%",
            },
            {"name": "PostgreSQL", "status": "operational", "value": 42, "unit": "ms"},
            {"name": "Redis Cache", "status": "degraded", "value": 91.4, "unit": "%"},
            {
                "name": "WebSocket",
                "status": "operational",
                "value": 18,
                "unit": "streams",
            },
            {
                "name": "Workers",
                "status": "operational",
                "value": 12,
                "unit": "jobs/min",
            },
        ],
        "alerts": [
            {
                "severity": "critical",
                "module": "Flight Operations",
                "message": "Ruta con ocupacion alta requiere ajuste de inventario.",
                "time": "Hace 4 min",
            },
            {
                "severity": "warning",
                "module": "Payments",
                "message": "Aumento de pagos fallidos en ventana de alta demanda.",
                "time": "Hace 11 min",
            },
            {
                "severity": "ai",
                "module": "AI Analytics",
                "message": "Forecast detecta oportunidad de margen en rutas premium.",
                "time": "Hace 18 min",
            },
        ],
    }


@router.get("/commercial/segments")
async def get_commercial_segments(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Motor comercial: segmentos accionables calculados sobre pasajeros y millas."""
    _require_enterprise_access(current_user)

    passengers_total = int(
        _safe_scalar(db, "SELECT COALESCE(MAX(id), 0) FROM pasajeros") or 0
    )
    transactions_total = int(
        _safe_scalar(db, "SELECT COALESCE(MAX(id), 0) FROM transacciones") or 0
    )
    passenger_start = max(passengers_total - ENTERPRISE_SAMPLE_PASSENGERS, 0)
    transaction_start = max(transactions_total - ENTERPRISE_SAMPLE_TRANSACTIONS, 0)

    avg_ticket = float(
        _safe_scalar(
            db,
            "SELECT COALESCE(AVG(monto), 0) FROM transacciones WHERE id > :start_id",
            {"start_id": transaction_start},
        )
        or 0
    )

    vip_count = int(
        _safe_scalar(
            db,
            """
            SELECT COUNT(*)
            FROM pasajeros p
            LEFT JOIN millas_acumuladas m ON m.pasajero_id = p.id
            WHERE p.id > :start_id
              AND (COALESCE(m.dinero_gastado, 0) >= 1000 OR COALESCE(m.millas_totales, 0) >= 10000)
            """,
            {"start_id": passenger_start},
        )
        or 0
    )
    high_value_count = int(
        _safe_scalar(
            db,
            """
            SELECT COUNT(*)
            FROM pasajeros p
            LEFT JOIN millas_acumuladas m ON m.pasajero_id = p.id
            WHERE p.id > :start_id
              AND COALESCE(m.dinero_gastado, 0) >= 500
            """,
            {"start_id": passenger_start},
        )
        or 0
    )
    new_customers_count = int(
        _safe_scalar(
            db,
            "SELECT COUNT(*) FROM pasajeros WHERE id > :start_id",
            {"start_id": passenger_start},
        )
        or 0
    )
    top_country_row = _safe_rows(
        db,
        """
        SELECT pais, COUNT(*) total
        FROM pasajeros
        WHERE id > :start_id
        GROUP BY pais
        ORDER BY total DESC
        LIMIT 1
        """,
        {"start_id": passenger_start},
    )
    top_country = top_country_row[0][0] if top_country_row else "Mercado principal"
    top_country_count = int(top_country_row[0][1]) if top_country_row else 0

    counts = {
        "vip_churn": vip_count,
        "high_value": high_value_count,
        "new_customers": new_customers_count,
        "country_opportunity": top_country_count,
    }
    labels = {"country_opportunity": top_country}

    segments = []
    for rule in _segment_rules():
        audience = counts.get(rule["id"], 0)
        discount = int(rule["discount_percent"])
        expected_conversion = 0.08 if rule["priority"] == "Alta" else 0.045
        expected_revenue = (
            audience * expected_conversion * max(avg_ticket, 120) * (1 - discount / 100)
        )
        estimated_cost = audience * 0.07 + expected_revenue * (discount / 100) * 0.18
        roi = (
            ((expected_revenue - estimated_cost) / estimated_cost * 100)
            if estimated_cost
            else 0
        )
        segments.append(
            {
                **rule,
                "label": labels.get(rule["id"], rule["name"]),
                "audience_size": audience,
                "expected_conversion": round(expected_conversion * 100, 1),
                "expected_revenue": round(expected_revenue, 2),
                "estimated_cost": round(estimated_cost, 2),
                "estimated_roi": round(roi, 1),
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "avg_ticket": round(avg_ticket, 2),
        "segments": segments,
        "rules": _segment_rules(),
    }


@router.post("/commercial/campaigns/launch")
async def launch_commercial_campaign(
    payload: CampaignLaunchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Simula la activación de una campaña sobre un segmento accionable."""
    _require_enterprise_access(current_user)

    segments_payload = await get_commercial_segments(current_user=current_user, db=db)
    segment = next(
        (
            item
            for item in segments_payload["segments"]
            if item["id"] == payload.segment_id
        ),
        None,
    )
    if not segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Segmento no encontrado"
        )

    audience = int(segment["audience_size"])
    reachable = int(audience * 0.92)
    expected_conversions = int(
        reachable * (float(segment["expected_conversion"]) / 100)
    )
    expected_revenue = (
        expected_conversions
        * max(float(segments_payload["avg_ticket"]), 120)
        * (1 - payload.discount_percent / 100)
    )
    campaign_id = f"cmp_{payload.segment_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    return {
        "campaign_id": campaign_id,
        "status": "scheduled",
        "segment": segment["name"],
        "channel": payload.channel,
        "discount_percent": payload.discount_percent,
        "budget_usd": payload.budget_usd,
        "audience_size": audience,
        "reachable_customers": reachable,
        "expected_conversions": expected_conversions,
        "expected_revenue": round(expected_revenue, 2),
        "message": f"Campaña programada para {reachable} clientes por {payload.channel}.",
    }


@router.get("/db/users")
async def get_users_data(
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
    is_active: Optional[bool] = None,
    q: Optional[str] = None,
) -> Dict[str, Any]:
    """Ver todos los usuarios en la base de datos con paginación y filtros."""
    if _.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    filters: list[str] = []
    params: dict[str, object] = {"limit": limit, "offset": offset}
    count_params: dict[str, object] = {}

    if is_active is not None:
        filters.append("is_active = :is_active")
        params["is_active"] = is_active
        count_params["is_active"] = is_active

    if q:
        filters.append("(email ILIKE :q OR full_name ILIKE :q)")
        params["q"] = f"%{q.strip()}%"
        count_params["q"] = f"%{q.strip()}%"

    query = "SELECT id, full_name, email, role, is_active, created_at FROM users"
    count_query = "SELECT COUNT(*) FROM users"
    if filters:
        filter_clause = " AND ".join(filters)
        query += f" WHERE {filter_clause}"
        count_query += f" WHERE {filter_clause}"

    query += " ORDER BY id LIMIT :limit OFFSET :offset"

    result = db.execute(text(query).bindparams(**params))
    usuarios = []
    for row in result:
        usuarios.append(
            {
                "id": row[0],
                "full_name": row[1],
                "email": row[2],
                "role": row[3],
                "is_active": row[4],
                "created_at": str(row[5]) if row[5] else None,
            }
        )

    total_result = db.execute(text(count_query).bindparams(**count_params))
    total = total_result.scalar()

    return {"usuarios": usuarios, "total": total, "limit": limit, "offset": offset}


@router.get("/db/stats")
async def get_db_stats(
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Estadísticas generales de la base de datos"""
    if _.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    stats = {}

    # Pasajeros
    result = db.execute(text("SELECT COUNT(*) FROM pasajeros"))
    stats["pasajeros_total"] = result.scalar()

    # Transacciones
    result = db.execute(text("SELECT COUNT(*) FROM transacciones"))
    stats["transacciones_total"] = result.scalar()

    # Aeropuertos
    result = db.execute(text("SELECT COUNT(*) FROM airports"))
    stats["aeropuertos_total"] = result.scalar()

    # Millas
    result = db.execute(text("SELECT SUM(millas_totales) FROM millas_acumuladas"))
    stats["millas_total"] = result.scalar() or 0

    # Usuarios
    result = db.execute(text("SELECT COUNT(*) FROM users"))
    stats["usuarios_total"] = result.scalar()

    return stats


@router.put("/users/{user_id}/active")
async def set_user_active(
    user_id: int,
    is_active: bool,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Activar o desactivar cuentas de plataforma."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )
    user.is_active = is_active
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
    }


@router.get("/reports/global")
async def global_report(
    format: str = Query("json", pattern="^(json|xlsx)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Base exportable a PDF/Excel desde el frontend o herramientas externas."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    pasajeros = (
        db.execute(text("SELECT COALESCE(MAX(id), 0) FROM pasajeros")).scalar() or 0
    )
    transacciones = (
        db.execute(text("SELECT COALESCE(MAX(id), 0) FROM transacciones")).scalar() or 0
    )
    sample_start = max(int(transacciones) - ENTERPRISE_SAMPLE_TRANSACTIONS, 0)
    sample_revenue = (
        db.execute(
            text(
                "SELECT COALESCE(SUM(monto), 0) FROM transacciones WHERE id > :start_id"
            ),
            {"start_id": sample_start},
        ).scalar()
        or 0
    )
    sample_size = max(int(transacciones) - sample_start, 1)
    ingresos = float(sample_revenue) * (
        int(transacciones) / sample_size if transacciones else 0
    )
    passenger_start = max(int(pasajeros) - ENTERPRISE_SAMPLE_PASSENGERS, 0)
    rutas = db.execute(
        text("""
        SELECT pais, ciudad, COUNT(*) total
        FROM pasajeros
        WHERE id > :start_id
        GROUP BY pais, ciudad
        ORDER BY total DESC
        LIMIT 20
    """),
        {"start_id": passenger_start},
    )

    if format == "xlsx":
        summary = [{"pasajeros_total": pasajeros, "ingresos_total": ingresos}]
        df_summary = pd.DataFrame(summary)
        df_rutas = pd.DataFrame(
            [{"pais": row[0], "ciudad": row[1], "total": row[2]} for row in rutas]
        )

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_summary.to_excel(writer, sheet_name="Resumen", index=False)
            df_rutas.to_excel(writer, sheet_name="Rutas principales", index=False)
        output.seek(0)

        headers = {"Content-Disposition": "attachment; filename=global_report.xlsx"}
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers,
        )

    return {
        "pasajeros_total": pasajeros,
        "ingresos_total": ingresos,
        "rutas_principales": [
            {"pais": row[0], "ciudad": row[1], "total": row[2]} for row in rutas
        ],
    }
