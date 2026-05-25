"""
Modelos de automatización: plantillas de workflows y ejecuciones.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from models.base import Base


class WorkflowTemplate(Base):
    __tablename__ = "workflow_templates"

    id = Column(String(64), primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    trigger = Column(String(80), nullable=False)
    actions = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant")
    executions = relationship("WorkflowExecution", back_populates="workflow")


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(
        String(64), ForeignKey("workflow_templates.id"), nullable=False
    )
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    trigger_source = Column(String(80), nullable=False)
    executed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    context = Column(JSON, nullable=True)
    status = Column(String(32), nullable=False, default="completed")
    result = Column(JSON, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)

    workflow = relationship("WorkflowTemplate", back_populates="executions")
    tenant = relationship("Tenant")
