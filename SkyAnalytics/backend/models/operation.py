from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from models.base import Base


class Operation(Base):
    __tablename__ = "operaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(150), nullable=False)
    description = Column(String(500), nullable=True)
    client_id = Column(Integer, ForeignKey("pasajeros.id"), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="PENDING")
    category = Column(String(100), nullable=True)
    type = Column(String(16), nullable=False, default="INCOME")
    amount = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    pasajero = relationship("Pasajero", back_populates="operations")
