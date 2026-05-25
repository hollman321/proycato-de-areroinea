"""Estadísticas agregadas (requieren JWT)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_active_user
from models.pasajero import MillasAcumuladas, Pasajero
from models.user import User
from services import analytics_service, categoria_service
from services.analytics_cache import get_cached

router = APIRouter(tags=["Estadísticas"])


@router.get("/estadisticas/total-pasajeros")
def total_pasajeros(
    _: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    total = db.query(Pasajero).count()
    return {"total_pasajeros": total}


@router.get("/estadisticas/por-pais")
def estadisticas_por_pais(
    _: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    resultados = (
        db.query(Pasajero.pais, func.count(Pasajero.id).label("cantidad"))
        .group_by(Pasajero.pais)
        .order_by(func.count(Pasajero.id).desc())
        .all()
    )
    estadisticas = [{"pais": r[0], "cantidad": r[1]} for r in resultados]
    return {"estadisticas": estadisticas}


@router.get("/estadisticas/resumen")
def resumen_estadisticas(
    _: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    # Misma lógica y caché 30s que GET /analytics/resumen (dict crudo sin schema Pydantic).
    return analytics_service.resumen_cached(db)


@router.get("/estadisticas/categorias")
def estadisticas_por_categoria(
    _: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    def build():
        rows = (
            db.query(
                Pasajero.pais,
                MillasAcumuladas.millas_totales,
                MillasAcumuladas.dinero_gastado,
            )
            .outerjoin(MillasAcumuladas)
            .all()
        )
        conteo = {"PREMIUM": 0, "STANDARD": 0, "BASICO": 0}
        for pais, millas_totales, dinero_gastado in rows:
            millas_totales = int(millas_totales or 0)
            dinero_gastado = float(dinero_gastado or 0)
            cat = categoria_service.calcular_categoria(
                millas_totales, dinero_gastado, pais
            )
            conteo[cat] = conteo.get(cat, 0) + 1
        return {"estadisticas_categorias": conteo, "total": sum(conteo.values())}

    return get_cached("estadisticas:categorias:v1", build)


@router.get("/stats/categoria-promedio")
def categoria_promedio_por_pais(
    _: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    def build():
        rows = (
            db.query(
                Pasajero.pais,
                MillasAcumuladas.millas_totales,
                MillasAcumuladas.dinero_gastado,
            )
            .outerjoin(MillasAcumuladas)
            .all()
        )
        resumen_por_pais: dict[str, dict[str, int | float]] = {}
        for pais, millas_totales, dinero_gastado in rows:
            millas_totales = int(millas_totales or 0)
            dinero_gastado = float(dinero_gastado or 0)
            cat = categoria_service.calcular_categoria(
                millas_totales, dinero_gastado, pais
            )
            pais_key = pais or "Desconocido"
            if pais_key not in resumen_por_pais:
                resumen_por_pais[pais_key] = {
                    "total": 0,
                    "PREMIUM": 0,
                    "STANDARD": 0,
                    "BASICO": 0,
                }
            resumen_por_pais[pais_key]["total"] += 1
            resumen_por_pais[pais_key][cat] += 1

        stats_por_pais = []
        for pais_key, datos in resumen_por_pais.items():
            total = datos["total"]
            premium = int(datos["PREMIUM"])
            standard = int(datos["STANDARD"])
            basico = int(datos["BASICO"])
            porcentaje_premium = (premium / total) * 100 if total else 0.0
            stats_por_pais.append(
                {
                    "pais": pais_key,
                    "total_pasajeros": total,
                    "premium": premium,
                    "standard": standard,
                    "basico": basico,
                    "porcentaje_premium": round(porcentaje_premium, 2),
                }
            )
        stats_por_pais.sort(key=lambda x: x["porcentaje_premium"], reverse=True)
        return {"estadisticas_por_pais": stats_por_pais}

    return get_cached("estadisticas:categoria-promedio:v1", build)
