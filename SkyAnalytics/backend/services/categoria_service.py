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


def calcular_categoria(
    millas_totales: int,
    dinero_gastado: float,
    pais: str,
    numero_transacciones: int = 0,
) -> str:
    """Categoria comercial usada por dashboard, descuentos y checkout."""
    if millas_totales >= 120000 or dinero_gastado >= 20000 or numero_transacciones >= 80:
        return "VIP"
    if millas_totales >= 80000 or dinero_gastado >= 12000 or numero_transacciones >= 50:
        return "Empresarial"
    if millas_totales >= 50000 or dinero_gastado >= 7500 or numero_transacciones >= 30:
        return "Ejecutivo"
    if millas_totales >= 25000 or dinero_gastado >= 3500 or numero_transacciones >= 15:
        return "Premium"
    if millas_totales >= 5000 or dinero_gastado >= 750 or numero_transacciones >= 3:
        return "Frecuente"
    if pais in PAISES_PREMIUM and millas_totales >= 15000:
        return "Premium"
    return "Nuevo"


def calcular_nivel_descuento(
    millas_totales: int,
    dinero_gastado: float,
    numero_transacciones: int,
) -> dict:
    """Reglas de descuento automatico visibles en checkout."""
    if numero_transacciones >= 70 or millas_totales >= 100000 or dinero_gastado >= 18000:
        nivel, porcentaje = "Diamante", 25
    elif numero_transacciones >= 35 or millas_totales >= 60000 or dinero_gastado >= 9000:
        nivel, porcentaje = "Platino", 18
    elif numero_transacciones >= 12 or millas_totales >= 20000 or dinero_gastado >= 2500:
        nivel, porcentaje = "Oro", 12
    else:
        nivel, porcentaje = "Base", 5 if numero_transacciones > 0 else 0

    cashback = round(porcentaje * 0.2, 2)
    puntos_multiplicador = 1 + (porcentaje / 100)
    cupon = f"SKY-{nivel.upper()}-{porcentaje}" if porcentaje else None
    return {
        "nivel": nivel,
        "porcentaje_descuento": porcentaje,
        "cashback_porcentaje": cashback,
        "puntos_multiplicador": round(puntos_multiplicador, 2),
        "cupon_automatico": cupon,
    }


def obtener_o_crear_millas(pasajero_id: int, db: Session) -> MillasAcumuladas:
    millas = db.query(MillasAcumuladas).filter(MillasAcumuladas.pasajero_id == pasajero_id).first()
    if not millas:
        millas = MillasAcumuladas(pasajero_id=pasajero_id, millas_totales=0, dinero_gastado=0)
        db.add(millas)
        db.commit()
    return millas


def obtener_beneficios(categoria: str) -> List[str]:
    beneficios_map: dict[str, List[str]] = {
        "VIP": [
            "Acceso VIP internacional",
            "Descuento Diamante automatico",
            "Cashback preferencial",
            "Prioridad maxima en promociones",
            "Soporte dedicado 24/7",
        ],
        "Empresarial": [
            "Promociones corporativas",
            "Descuento Platino automatico",
            "Acumulacion acelerada de puntos",
            "Prioridad alta en cambios",
        ],
        "Ejecutivo": [
            "Upgrade prioritario segun disponibilidad",
            "Descuento Platino/Oro automatico",
            "Alertas anticipadas de precio",
        ],
        "Premium": [
            "Acceso a promociones premium",
            "Descuento Oro automatico",
            "Mayor acumulacion de puntos",
        ],
        "Frecuente": [
            "Cupones automaticos por recurrencia",
            "Acumulacion de puntos",
            "Promociones por destino habitual",
        ],
        "Nuevo": [
            "Promocion de bienvenida",
            "Acumulacion inicial de puntos",
            "Acceso a alertas de precios",
        ],
        CategoriaEnum.PREMIUM.value: [
            "Acceso a salas VIP",
            "Doble acumulacion de millas",
            "Upgrade prioritario a primera clase",
            "Tarjeta de embarque prioritario",
            "Asistencia 24/7 dedicada",
        ],
        CategoriaEnum.STANDARD.value: [
            "Acceso a salas de espera mejoradas",
            "Acumulacion normal de millas",
            "Upgrade segun disponibilidad",
            "Prioridad media en check-in",
        ],
        CategoriaEnum.BASICO.value: [
            "Acceso a salas basicas",
            "Acumulacion lenta de millas",
            "Check-in estandar",
        ],
    }
    return beneficios_map.get(categoria, [])
