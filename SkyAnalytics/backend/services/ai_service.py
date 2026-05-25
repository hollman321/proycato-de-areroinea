"""
Servicio de inteligencia artificial para generar recomendaciones operativas y de revenue.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None

from core.config import settings
from models.user import User


def _get_openai_client() -> Optional[Any]:
    if not openai or not settings.openai_api_key:
        return None

    openai.api_key = settings.openai_api_key
    return openai


def _build_recommendation_label(rank: int, name: str) -> str:
    return f"R{rank:02d} - {name}"


def generate_enterprise_recommendations(db: Session, current_user: User) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    passenger_count = int(_safe_scalar(db, "SELECT COUNT(*) FROM pasajeros") or 0)
    high_risk_vip = int(
        _safe_scalar(
            db,
            """
            SELECT COUNT(*)
            FROM pasajeros p
            LEFT JOIN transacciones t ON t.pasajero_id = p.id
            WHERE p.id IN (
                SELECT pasajero_id FROM transacciones GROUP BY pasajero_id HAVING MAX(fecha_transaccion) < NOW() - INTERVAL '90 days'
            )
            AND p.id IN (
                SELECT pasajero_id FROM transacciones GROUP BY pasajero_id HAVING SUM(monto) > 1500)
            """,
        )
        or 0
    )
    revenue_trend = _safe_rows(
        db,
        """
        SELECT date_trunc('week', fecha_transaccion)::date week,
               COALESCE(SUM(monto), 0) revenue
        FROM transacciones
        GROUP BY week
        ORDER BY week DESC
        LIMIT 8
        """,
    )
    recent_routes = _safe_rows(
        db,
        """
        SELECT pais, ciudad, COUNT(*) AS bookings
        FROM pasajeros
        WHERE id > GREATEST((SELECT COALESCE(MAX(id), 0) FROM pasajeros) - 15000, 0)
        GROUP BY pais, ciudad
        ORDER BY bookings DESC
        LIMIT 3
        """,
    )

    recommendations = [
        {
            "id": "price_adjustment_premium_routes",
            "title": _build_recommendation_label(1, "Optimizar pricing premium"),
            "description": "Aumentar pricing un 4% en rutas con alta demanda y capacidad limitada para maximizar revenue sin impactar ocupación.",
            "module": "Revenue",
            "confidence": "high",
            "impact_score": 87,
            "payload": {"delta_pct": 4, "scope": "premium_routes"},
        },
        {
            "id": "retain_vip_churn",
            "title": _build_recommendation_label(2, "Retención VIP en riesgo"),
            "description": f"Detectados {high_risk_vip} clientes VIP con baja actividad reciente; lanzar oferta exclusiva de reactivación.",
            "module": "Customer",
            "confidence": "high",
            "impact_score": 82,
            "payload": {"segment": "vip_churn", "offer": "upgrade + cupón"},
        },
        {
            "id": "schedule_maintenance_priority",
            "title": _build_recommendation_label(3, "Priorizar mantenimiento de flota"),
            "description": "Rutas con indicadores de uso intensivo requieren inspección preventiva para evitar retrasos críticos.",
            "module": "FlightOps",
            "confidence": "medium",
            "impact_score": 79,
            "payload": {"route_group": [route[0] for route in recent_routes[:2]], "type": "preflight_check"},
        },
    ]

    forecast = {
        "next_30_days_revenue": max(0, sum(float(row[1] or 0) for row in revenue_trend) * 1.08),
        "churn_probability": min(0.22, high_risk_vip / max(1, passenger_count)),
        "recommended_discount": 0.12,
    }

    model = _get_openai_client()
    if model:
        try:
            prompt = (
                "Genera tres recomendaciones empresariales breves para una aerolínea, "
                "basadas en tendencias de revenue, churn y operaciones en el último mes. "
                "Incluye una sugerencia de optimización de precios y retención de clientes."
            )
            response = model.ChatCompletion.create(
                model=settings.openai_model,
                messages=[{"role": "system", "content": "Eres un asistente de operaciones empresariales."},
                          {"role": "user", "content": prompt}],
                max_tokens=260,
                temperature=0.7,
            )
            content = response.choices[0].message.get("content", "")
            recommendations.append(
                {
                    "id": "openai_insight_1",
                    "title": _build_recommendation_label(4, "OpenAI insight"),
                    "description": content.strip()[:240],
                    "module": "AI",
                    "confidence": "medium",
                    "impact_score": 74,
                    "payload": {"source": "openai", "message": content.strip()},
                }
            )
        except Exception:
            pass

    return {
        "generated_at": now.isoformat(),
        "forecast": forecast,
        "recommendations": recommendations,
        "revenue_trend": [
            {"period": row[0].strftime("%Y-%m-%d"), "revenue": float(row[1] or 0)}
            for row in revenue_trend
        ],
    }


def _safe_scalar(db: Session, sql: str, params: Optional[dict[str, Any]] = None) -> Any:
    try:
        return db.execute(text(sql), params or {}).scalar()
    except Exception:
        return None


def _safe_rows(db: Session, sql: str, params: Optional[dict[str, Any]] = None) -> list[Any]:
    try:
        return list(db.execute(text(sql), params or {}).all())
    except Exception:
        return []
