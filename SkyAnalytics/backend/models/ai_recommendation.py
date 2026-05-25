"""
Modelo para recomendaciones de IA accionables.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from models.base import Base


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id = Column(String(64), primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    module = Column(String(64), nullable=False)
    confidence = Column(String(16), nullable=False, default="medium")
    impact_score = Column(Integer, nullable=False, default=0)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    applied_at = Column(DateTime, nullable=True)
    status = Column(String(32), nullable=False, default="pending")

    tenant = relationship("Tenant")
    user = relationship("User")
