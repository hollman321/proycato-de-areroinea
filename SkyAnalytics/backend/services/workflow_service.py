"""
Servicio de workflows para ejecutar reglas operacionales y automatizaciones.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional

from sqlalchemy.orm import Session

from models.user import User
from models.workflow import WorkflowExecution, WorkflowTemplate
from services.audit_service import log_audit_event

DEFAULT_WORKFLOW_TEMPLATES: list[Dict[str, Any]] = [
    {
        "id": "retain_vip_customers",
        "name": "Retención VIP automática",
        "trigger": "vip_churn_detected",
        "description": "Detecta VIP con baja actividad y activa un workflow de cupones exclusivos.",
        "actions": ["apply_coupon", "notify_care_team"],
    },
    {
        "id": "pricing_premium_routes",
        "name": "Ajuste dinámico de pricing",
        "trigger": "route_demand_spike",
        "description": "Ajusta precios dinámicos para rutas con sostenida alta demanda.",
        "actions": ["update_pricing_model", "publish_internal_alert"],
    },
    {
        "id": "security_threat_response",
        "name": "Respuesta de seguridad automática",
        "trigger": "suspicious_login_pattern",
        "description": "Activa bloqueo temporal y notificación a SOC para anomalías de acceso.",
        "actions": ["suspend_sessions", "notify_soc"],
    },
]


def seed_workflow_templates(db: Session, current_user: User) -> list[WorkflowTemplate]:
    existing = (
        db.query(WorkflowTemplate)
        .filter(WorkflowTemplate.tenant_id == current_user.tenant_id)
        .all()
    )
    if existing:
        return existing

    templates = []
    for template in DEFAULT_WORKFLOW_TEMPLATES:
        templates.append(
            WorkflowTemplate(
                id=template["id"],
                tenant_id=current_user.tenant_id,
                name=template["name"],
                description=template["description"],
                trigger=template["trigger"],
                actions=template["actions"],
            )
        )
    db.add_all(templates)
    db.commit()
    return templates


def list_workflows(db: Session, current_user: User) -> list[WorkflowTemplate]:
    templates = (
        db.query(WorkflowTemplate)
        .filter(WorkflowTemplate.tenant_id == current_user.tenant_id)
        .all()
    )
    if not templates:
        templates = seed_workflow_templates(db, current_user)
    return templates


def execute_workflow(
    db: Session,
    current_user: User,
    workflow_id: str,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    workflow = (
        db.query(WorkflowTemplate)
        .filter(
            WorkflowTemplate.id == workflow_id,
            WorkflowTemplate.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not workflow:
        raise ValueError("Workflow no encontrado")

    result = {
        "workflow_id": workflow.id,
        "name": workflow.name,
        "status": "executed",
        "trigger": workflow.trigger,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "actions": workflow.actions,
        "context": context or {},
    }

    execution = WorkflowExecution(
        workflow_id=workflow.id,
        tenant_id=current_user.tenant_id,
        trigger_source=workflow.trigger,
        executed_by=current_user.id,
        context=context or {},
        status="completed",
        result=result,
        started_at=datetime.now(timezone.utc),
        finished_at=datetime.now(timezone.utc),
    )
    db.add(execution)
    db.commit()

    log_audit_event(
        db,
        current_user,
        module="Automation",
        action="execute_workflow",
        metadata={"workflow_id": workflow_id, "result": result},
    )

    return result


def _render_workflow_payload(workflow: Dict[str, Any], target: str) -> str:
    return f"Workflow {workflow['name']} triggered for {target}."
