"""
Schemas de Pydantic con validaciones ESTRICTAS.

Este archivo centraliza todas las validaciones de entrada para garantizar
que los datos sean correctos antes de entrar a la BD.
"""

from pydantic import BaseModel, EmailStr, field_validator, Field
from datetime import date, datetime
from typing import Optional
import re


class ValidadorTarjeta:
    """Validaciones para tarjetas de crédito y débito"""

    @staticmethod
    def validar_numero_tarjeta(numero: str) -> bool:
        """
        Valida número de tarjeta usando Algoritmo de Luhn.

        El algoritmo de Luhn es un checksum para detectar errores:
        - Dobla cada segundo dígito de derecha a izquierda
        - Si > 9, resta 9
        - Suma todos los dígitos
        - Si la suma es divisible por 10, la tarjeta es válida
        """
        # Remover espacios y guiones
        numero_limpio = numero.replace(" ", "").replace("-", "")

        # Debe tener 13-19 dígitos (estándar de tarjetas)
        if (
            not numero_limpio.isdigit()
            or len(numero_limpio) < 13
            or len(numero_limpio) > 19
        ):
            return False

        # Algoritmo de Luhn
        def luhn_checksum(card_number):
            def digits_of(n):
                return [int(d) for d in str(n)]

            digits = digits_of(card_number)
            odd_digits = digits[-1::-2]  # Cada segundo dígito de derecha a izq
            even_digits = digits[-2::-2]

            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))

            return checksum % 10

        return luhn_checksum(numero_limpio) == 0

    @staticmethod
    def validar_formato_tarjeta(numero: str) -> str:
        """
        Detecta y valida el tipo de tarjeta por su número.
        VISA: comienza con 4, 13 o 16 dígitos
        MASTERCARD: comienza con 5, 16 dígitos
        AMEX: comienza con 3, 15 dígitos
        """
        numero_limpio = numero.replace(" ", "").replace("-", "")

        if numero_limpio.startswith("4"):
            if len(numero_limpio) in [13, 16]:
                return "VISA"
        elif numero_limpio.startswith("5"):
            if len(numero_limpio) == 16:
                return "MASTERCARD"
        elif numero_limpio.startswith("3"):
            if len(numero_limpio) == 15:
                return "AMEX"

        return "DESCONOCIDO"


class PasajeroSchemaBase(BaseModel):
    """Schema base con validaciones"""

    nombre_completo: str = Field(..., min_length=3, max_length=100)
    correo: EmailStr  # Validación automática de email
    tarjeta_credito: str = Field(..., min_length=13, max_length=19)
    tarjeta_debito: str = Field(..., min_length=13, max_length=19)
    direccion: str = Field(..., min_length=5, max_length=255)
    ciudad: str = Field(..., min_length=2, max_length=100)
    pais: str = Field(..., min_length=2, max_length=100)
    fecha_registro: date

    @field_validator("nombre_completo")
    @classmethod
    def validar_nombre(cls, v):
        """Valida que el nombre no contenga caracteres inválidos"""
        if not re.match(r"^[a-zA-ZáéíóúñüÁÉÍÓÚÑÜ\s'-]+$", v):
            raise ValueError("Nombre contiene caracteres inválidos")
        return v.strip()

    @field_validator("tarjeta_credito")
    @classmethod
    def validar_tarjeta_credito(cls, v):
        """Valida formato y checksum de tarjeta de crédito"""
        if not ValidadorTarjeta.validar_numero_tarjeta(v):
            raise ValueError(
                "Número de tarjeta de crédito inválido (Luhn checksum fallo)"
            )
        return v.replace(" ", "").replace("-", "")

    @field_validator("tarjeta_debito")
    @classmethod
    def validar_tarjeta_debito(cls, v):
        """Valida formato y checksum de tarjeta de débito"""
        if not ValidadorTarjeta.validar_numero_tarjeta(v):
            raise ValueError(
                "Número de tarjeta de débito inválido (Luhn checksum fallo)"
            )
        return v.replace(" ", "").replace("-", "")

    @field_validator("ciudad", "pais")
    @classmethod
    def validar_ubicacion(cls, v):
        """Valida que ciudad/país sean válidos"""
        # No permitir números solamente
        if v.isdigit():
            raise ValueError("Ciudad/País no puede contener solo números")
        # Remover espacios extras
        return v.strip().title()

    @field_validator("fecha_registro")
    @classmethod
    def validar_fecha(cls, v):
        """Valida que la fecha no sea en el futuro"""
        if v > date.today():
            raise ValueError("Fecha de registro no puede ser en el futuro")
        return v


class PasajeroCreate(PasajeroSchemaBase):
    """Schema para crear un pasajero"""

    pass


class PasajeroUpdate(BaseModel):
    """Schema para actualizar un pasajero (campos opcionales)"""

    nombre_completo: Optional[str] = Field(None, min_length=3, max_length=100)
    correo: Optional[EmailStr] = None
    tarjeta_credito: Optional[str] = Field(None, min_length=13, max_length=19)
    tarjeta_debito: Optional[str] = Field(None, min_length=13, max_length=19)
    direccion: Optional[str] = Field(None, min_length=5, max_length=255)
    ciudad: Optional[str] = Field(None, min_length=2, max_length=100)
    pais: Optional[str] = Field(None, min_length=2, max_length=100)

    @field_validator("tarjeta_credito", "tarjeta_debito", mode="before")
    @classmethod
    def validar_tarjetas_update(cls, v):
        """Valida tarjetas en update"""
        if v is None:
            return None
        if not ValidadorTarjeta.validar_numero_tarjeta(v):
            raise ValueError("Número de tarjeta inválido")
        return v.replace(" ", "").replace("-", "")


class TransaccionCreate(BaseModel):
    """Schema para crear transacción"""

    monto: float
    descripcion: str = "Transacción general"

    @field_validator("monto")
    @classmethod
    def validar_monto(cls, v):
        """Valida que el monto sea positivo"""
        if v is None or v <= 0:
            raise ValueError("Monto debe ser mayor a 0")
        if v > 999999999:  # Máximo ~1 billón USD
            raise ValueError("Monto excede límite máximo")
        return round(v, 2)

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, v):
        """Valida descripción"""
        if len(v) > 500:
            raise ValueError("Descripción no puede exceder 500 caracteres")
        return v.strip()


class TransaccionResponse(BaseModel):
    """Schema para respuesta de transacción"""

    id: int
    pasajero_id: int
    monto: float
    millas_ganadas: int
    descripcion: str
    fecha_transaccion: datetime

    class Config:
        from_attributes = True


class MillasResponse(BaseModel):
    """Schema para respuesta de millas"""

    pasajero_id: int
    millas_totales: int
    dinero_gastado: float
    fecha_actualizado: datetime

    class Config:
        from_attributes = True


class PasajeroResponse(PasajeroSchemaBase):
    """Schema para respuesta de pasajero"""

    id: int

    class Config:
        from_attributes = True


class PerfillPasajero(BaseModel):
    """Perfil completo del pasajero"""

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
