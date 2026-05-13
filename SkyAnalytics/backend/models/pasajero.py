"""Modelos de dominio: pasajeros, transacciones y millas."""

from datetime import datetime, timezone

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from models.base import Base


class Pasajero(Base):
    __tablename__ = "pasajeros"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_completo = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False)
    tarjeta_credito = Column(String, nullable=False)
    tarjeta_debito = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    ciudad = Column(String, nullable=False)
    pais = Column(String, nullable=False, index=True)
    fecha_registro = Column(Date, nullable=False, index=True)

    transacciones = relationship(
        "Transaccion", back_populates="pasajero", cascade="all, delete-orphan"
    )
    millas = relationship(
        "MillasAcumuladas",
        back_populates="pasajero",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Transaccion(Base):
    """Registro de compras/vuelos que suman millas al pasajero."""

    __tablename__ = "transacciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pasajero_id = Column(Integer, ForeignKey("pasajeros.id"), nullable=False, index=True)
    monto = Column(Float, nullable=False)
    millas_ganadas = Column(Integer, default=0)
    descripcion = Column(String)
    fecha_transaccion = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    pasajero = relationship("Pasajero", back_populates="transacciones")


class MillasAcumuladas(Base):
    """Totales acumulados por pasajero (una fila por pasajero)."""

    __tablename__ = "millas_acumuladas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pasajero_id = Column(Integer, ForeignKey("pasajeros.id"), unique=True, nullable=False)
    millas_totales = Column(Integer, default=0)
    dinero_gastado = Column(Float, default=0)
    fecha_actualizado = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    pasajero = relationship("Pasajero", back_populates="millas")


__all__ = ["Pasajero", "Transaccion", "MillasAcumuladas"]
