from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class Pasajero(Base):
    __tablename__ = 'pasajeros'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_completo = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False)
    tarjeta_credito = Column(String, nullable=False)
    tarjeta_debito = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    ciudad = Column(String, nullable=False)
    pais = Column(String, nullable=False)
    fecha_registro = Column(Date, nullable=False)
    
    # Relaciones
    transacciones = relationship("Transaccion", back_populates="pasajero", cascade="all, delete-orphan")
    millas = relationship("MillasAcumuladas", back_populates="pasajero", uselist=False, cascade="all, delete-orphan")


class Transaccion(Base):
    """
    Modelo para registrar transacciones de pasajeros.
    Cada compra/vuelo genera una transacción que suma millas.
    """
    __tablename__ = 'transacciones'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pasajero_id = Column(Integer, ForeignKey('pasajeros.id'), nullable=False)
    monto = Column(Float, nullable=False)  # Monto en USD/moneda local
    millas_ganadas = Column(Integer, default=0)  # Millas por transacción
    descripcion = Column(String)  # "Compra de vuelo", "Compra en tienda", etc.
    fecha_transaccion = Column(DateTime, default=datetime.utcnow)
    
    # Relación
    pasajero = relationship("Pasajero", back_populates="transacciones")


class MillasAcumuladas(Base):
    """
    Modelo para trackear las millas totales acumuladas por cada pasajero.
    Se actualiza con cada transacción.
    """
    __tablename__ = 'millas_acumuladas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pasajero_id = Column(Integer, ForeignKey('pasajeros.id'), unique=True, nullable=False)
    millas_totales = Column(Integer, default=0)
    dinero_gastado = Column(Float, default=0)  # Total gastado en transacciones
    fecha_actualizado = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación
    pasajero = relationship("Pasajero", back_populates="millas")


class CategoriaEnum(str, enum.Enum):
    """Categorías de pasajeros"""
    PREMIUM = "PREMIUM"
    STANDARD = "STANDARD"
    BASICO = "BASICO"