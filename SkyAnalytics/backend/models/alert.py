"""
Modelo de alerta para incidentes operacionales y event-driven notifications.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from models.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    module = Column(String(64), nullable=False)
    severity = Column(String(16), nullable=False, default="warning")
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(String(32), nullable=False, default="open")
    source = Column(String(64), nullable=True)
    metadata_payload = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    tenant = relationship("Tenant")
