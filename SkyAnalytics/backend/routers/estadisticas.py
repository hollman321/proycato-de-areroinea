"""Estadísticas agregadas (requieren JWT)."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_active_user
from models.pasajero import Pasajero
from models.user import User
from services import categoria_service

router = APIRouter(tags=["Estadísticas"])


@router.get("/estadisticas/total-pasajeros")
async def total_pasajeros(_: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    total = db.query(Pasajero).count()
    return {"total_pasajeros": total}


@router.get("/estadisticas/por-pais")
async def estadisticas_por_pais(_: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    resultados = (
        db.query(Pasajero.pais, func.count(Pasajero.id).label("cantidad"))
        .group_by(Pasajero.pais)
        .order_by(func.count(Pasajero.id).desc())
        .all()
    )
    estadisticas = [{"pais": r[0], "cantidad": r[1]} for r in resultados]
    return {"estadisticas": estadisticas}


@router.get("/estadisticas/resumen")
async def resumen_estadisticas(_: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    total = db.query(Pasajero).count()
    paises_unicos = db.query(func.count(func.distinct(Pasajero.pais))).scalar()
    ciudades_unicas = db.query(func.count(func.distinct(Pasajero.ciudad))).scalar()
    return {
        "total_pasajeros": total,
        "paises_unicos": paises_unicos,
        "ciudades_unicas": ciudades_unicas,
        "fecha_consulta": date.today(),
    }


@router.get("/estadisticas/categorias")
async def estadisticas_por_categoria(_: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    from models.pasajero import MillasAcumuladas

    pasajeros_con_millas = db.query(Pasajero, MillasAcumuladas).outerjoin(MillasAcumuladas).all()
    conteo = {"PREMIUM": 0, "STANDARD": 0, "BASICO": 0}
    for pasajero, millas in pasajeros_con_millas:
        millas_totales = millas.millas_totales if millas else 0
        dinero_gastado = millas.dinero_gastado if millas else 0
        cat = categoria_service.calcular_categoria(millas_totales, dinero_gastado, pasajero.pais)
        conteo[cat] = conteo.get(cat, 0) + 1
    return {"estadisticas_categorias": conteo, "total": sum(conteo.values())}


@router.get("/stats/categoria-promedio")
async def categoria_promedio_por_pais(_: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    from models.pasajero import MillasAcumuladas

    resultado = db.query(Pasajero.pais).distinct().all()
    stats_por_pais = []
    for (pais,) in resultado:
        pasajeros_pais = db.query(Pasajero).filter(Pasajero.pais == pais).all()
        if not pasajeros_pais:
            continue
        conteo_categoria = {"PREMIUM": 0, "STANDARD": 0, "BASICO": 0}
        for p in pasajeros_pais:
            millas = db.query(MillasAcumuladas).filter(MillasAcumuladas.pasajero_id == p.id).first()
            millas_totales = millas.millas_totales if millas else 0
            dinero_gastado = millas.dinero_gastado if millas else 0
            cat = categoria_service.calcular_categoria(millas_totales, dinero_gastado, p.pais)
            conteo_categoria[cat] = conteo_categoria.get(cat, 0) + 1
        porcentaje_premium = (conteo_categoria["PREMIUM"] / len(pasajeros_pais)) * 100
        stats_por_pais.append(
            {
                "pais": pais,
                "total_pasajeros": len(pasajeros_pais),
                "premium": conteo_categoria["PREMIUM"],
                "standard": conteo_categoria["STANDARD"],
                "basico": conteo_categoria["BASICO"],
                "porcentaje_premium": round(porcentaje_premium, 2),
            }
        )
    stats_por_pais.sort(key=lambda x: x["porcentaje_premium"], reverse=True)
    return {"estadisticas_por_pais": stats_por_pais}
