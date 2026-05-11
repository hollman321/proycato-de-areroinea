"""Reglas de categorización de pasajeros y beneficios (lógica de negocio pura)."""

from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session

from models.enums import CategoriaEnum
from models.pasajero import MillasAcumuladas

PAISES_PREMIUM = {
    "Estados Unidos",
    "Canadá",
    "Reino Unido",
    "Alemania",
    "Francia",
    "Japón",
    "Suiza",
    "Australia",
    "Singapur",
    "Emiratos Árabes",
}


def calcular_categoria(millas_totales: int, dinero_gastado: float, pais: str) -> str:
    if millas_totales > 50000:
        return CategoriaEnum.PREMIUM.value
    if dinero_gastado > 5000:
        return CategoriaEnum.PREMIUM.value
    if pais in PAISES_PREMIUM and millas_totales > 30000:
        return CategoriaEnum.PREMIUM.value
    if millas_totales >= 10000 or dinero_gastado >= 1000:
        return CategoriaEnum.STANDARD.value
    return CategoriaEnum.BASICO.value


def obtener_o_crear_millas(pasajero_id: int, db: Session) -> MillasAcumuladas:
    millas = db.query(MillasAcumuladas).filter(MillasAcumuladas.pasajero_id == pasajero_id).first()
    if not millas:
        millas = MillasAcumuladas(pasajero_id=pasajero_id, millas_totales=0, dinero_gastado=0)
        db.add(millas)
        db.commit()
    return millas


def obtener_beneficios(categoria: str) -> List[str]:
    beneficios_map: dict[str, List[str]] = {
        CategoriaEnum.PREMIUM.value: [
            "✈️ Acceso a salas VIP",
            "🎁 Doble acumulación de millas",
            "🅰️ Upgrade prioritario a primera clase",
            "🎫 Tarjeta de embarque prioritario",
            "💼 Asistencia 24/7 dedicada",
        ],
        CategoriaEnum.STANDARD.value: [
            "✈️ Acceso a salas de espera mejoradas",
            "🎁 Acumulación normal de millas",
            "🅰️ Upgrade según disponibilidad",
            "🎫 Prioridad media en check-in",
        ],
        CategoriaEnum.BASICO.value: [
            "✈️ Acceso a salas básicas",
            "🎁 Acumulación lenta de millas",
            "🎫 Check-in estándar",
        ],
    }
    return beneficios_map.get(categoria, [])
