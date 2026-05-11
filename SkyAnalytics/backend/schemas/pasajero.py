"""
Schemas de pasajeros y transacciones con validaciones estrictas.

Separado del router para que FastAPI solo orqueste y aquí queden las reglas de entrada/salida.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, constr, field_validator

from schemas.pagination import PaginationMetadata


class ValidadorTarjeta:
    """Validaciones para tarjetas de crédito y débito (algoritmo de Luhn)."""

    @staticmethod
    def validar_numero_tarjeta(numero: str) -> bool:
        numero_limpio = numero.replace(" ", "").replace("-", "")
        if not numero_limpio.isdigit() or len(numero_limpio) < 13 or len(numero_limpio) > 19:
            return False

        def luhn_checksum(card_number: str) -> int:
            def digits_of(n: str) -> list[int]:
                return [int(d) for d in str(n)]

            digits = digits_of(card_number)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(str(d * 2)))
            return checksum % 10

        return luhn_checksum(numero_limpio) == 0

    @staticmethod
    def validar_formato_tarjeta(numero: str) -> str:
        numero_limpio = numero.replace(" ", "").replace("-", "")
        if numero_limpio.startswith("4") and len(numero_limpio) in [13, 16]:
            return "VISA"
        if numero_limpio.startswith("5") and len(numero_limpio) == 16:
            return "MASTERCARD"
        if numero_limpio.startswith("3") and len(numero_limpio) == 15:
            return "AMEX"
        return "DESCONOCIDO"


class PasajeroSchemaBase(BaseModel):
    nombre_completo: constr(min_length=3, max_length=100)  # type: ignore[valid-type]
    correo: EmailStr
    tarjeta_credito: constr(min_length=13, max_length=19)  # type: ignore[valid-type]
    tarjeta_debito: constr(min_length=13, max_length=19)  # type: ignore[valid-type]
    direccion: constr(min_length=5, max_length=255)  # type: ignore[valid-type]
    ciudad: constr(min_length=2, max_length=100)  # type: ignore[valid-type]
    pais: constr(min_length=2, max_length=100)  # type: ignore[valid-type]
    fecha_registro: date

    @field_validator("nombre_completo")
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        if not re.match(r"^[a-zA-ZáéíóúñüÁÉÍÓÚÑÜ\s'-]+$", v):
            raise ValueError("Nombre contiene caracteres inválidos")
        return v.strip()

    @field_validator("tarjeta_credito")
    @classmethod
    def validar_tarjeta_credito(cls, v: str) -> str:
        if not ValidadorTarjeta.validar_numero_tarjeta(v):
            raise ValueError("Número de tarjeta de crédito inválido (Luhn checksum fallo)")
        return v.replace(" ", "").replace("-", "")

    @field_validator("tarjeta_debito")
    @classmethod
    def validar_tarjeta_debito(cls, v: str) -> str:
        if not ValidadorTarjeta.validar_numero_tarjeta(v):
            raise ValueError("Número de tarjeta de débito inválido (Luhn checksum fallo)")
        return v.replace(" ", "").replace("-", "")

    @field_validator("ciudad", "pais")
    @classmethod
    def validar_ubicacion(cls, v: str) -> str:
        if v.isdigit():
            raise ValueError("Ciudad/País no puede contener solo números")
        return v.strip().title()

    @field_validator("fecha_registro")
    @classmethod
    def validar_fecha(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Fecha de registro no puede ser en el futuro")
        return v


class PasajeroCreate(PasajeroSchemaBase):
    pass


class PasajeroUpdate(BaseModel):
    nombre_completo: Optional[constr(min_length=3, max_length=100)] = None  # type: ignore[valid-type]
    correo: Optional[EmailStr] = None
    tarjeta_credito: Optional[constr(min_length=13, max_length=19)] = None  # type: ignore[valid-type]
    tarjeta_debito: Optional[constr(min_length=13, max_length=19)] = None  # type: ignore[valid-type]
    direccion: Optional[constr(min_length=5, max_length=255)] = None  # type: ignore[valid-type]
    ciudad: Optional[constr(min_length=2, max_length=100)] = None  # type: ignore[valid-type]
    pais: Optional[constr(min_length=2, max_length=100)] = None  # type: ignore[valid-type]

    @field_validator("tarjeta_credito", "tarjeta_debito", mode="before")
    @classmethod
    def validar_tarjetas_update(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if not ValidadorTarjeta.validar_numero_tarjeta(v):
            raise ValueError("Número de tarjeta inválido")
        return v.replace(" ", "").replace("-", "")


class TransaccionCreate(BaseModel):
    monto: float
    descripcion: str = "Transacción general"

    @field_validator("monto")
    @classmethod
    def validar_monto(cls, v: float) -> float:
        if v is None or v <= 0:
            raise ValueError("Monto debe ser mayor a 0")
        if v > 999999999:
            raise ValueError("Monto excede límite máximo")
        return round(v, 2)

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, v: str) -> str:
        if len(v) > 500:
            raise ValueError("Descripción no puede exceder 500 caracteres")
        return v.strip()


class TransaccionResponse(BaseModel):
    id: int
    pasajero_id: int
    monto: float
    millas_ganadas: int
    descripcion: str
    fecha_transaccion: datetime

    class Config:
        from_attributes = True


class MillasResponse(BaseModel):
    pasajero_id: int
    millas_totales: int
    dinero_gastado: float
    fecha_actualizado: datetime

    class Config:
        from_attributes = True


class PasajeroResponse(PasajeroSchemaBase):
    id: int

    class Config:
        from_attributes = True


class PerfillPasajero(BaseModel):
    id: int
    nombre_completo: str
    correo: str
    pais: str
    categoria: str
    millas_totales: int
    dinero_gastado: float
    numero_transacciones: int
    beneficios: list[str]

    class Config:
        from_attributes = True


class PaginatedPasajeros(BaseModel):
    items: List[PasajeroResponse]
    pagination: PaginationMetadata
