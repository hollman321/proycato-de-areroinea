"""Enumeraciones usadas en dominio (categorías de pasajero, etc.)."""

import enum


class CategoriaEnum(str, enum.Enum):
    """Categorías de pasajeros según reglas de negocio."""

    PREMIUM = "PREMIUM"
    STANDARD = "STANDARD"
    BASICO = "BASICO"
