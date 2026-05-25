"""
Rutas enterprise para administración operativa, IA, auditoría y workflows.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import SessionLocal, get_db
from deps import get_current_active_user
from models.user import User
from services import audit_service, enterprise_service

router = APIRouter(prefix="/admin/enterprise", tags=["Admin Enterprise"])


@router.get("/ai/recommendations")
async def get_ai_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    return enterprise_service.list_ai_recommendations(db, current_user)


@router.post("/ai/apply")
async def apply_ai_recommendation(
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    recommendation_id = body.get("recommendation_id")
    if not recommendation_id:
        raise HTTPException(status_code=400, detail="recommendation_id es requerido")
    return enterprise_service.apply_ai_recommendation(
        db, current_user, recommendation_id
    )


@router.get("/live-feed")
async def get_live_operational_feed(
    limit: int = Query(18, ge=5, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    feed = enterprise_service.get_live_operational_feed(
        db, current_user, limit=min(limit, 50)
    )
    return {
        "data": [
            {
                **item,
                "occurred_at": (
                    item["occurred_at"].isoformat()
                    if hasattr(item["occurred_at"], "isoformat")
                    else str(item["occurred_at"])
                ),
            }
            for item in feed
        ]
    }


@router.get("/live-feed/stream")
async def stream_live_operational_feed(
    current_user: User = Depends(get_current_active_user),
) -> StreamingResponse:
    async def event_generator():
        while True:
            with SessionLocal() as session:
                feed = enterprise_service.get_live_operational_feed(
                    session, current_user, limit=12
                )
            payload = json.dumps(
                [
                    {
                        **item,
                        "occurred_at": (
                            item["occurred_at"].isoformat()
                            if hasattr(item["occurred_at"], "isoformat")
                            else str(item["occurred_at"])
                        ),
                    }
                    for item in feed
                ]
            )
            yield f"data: {payload}\n\n"
            await asyncio.sleep(4)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/security/incidents")
async def get_security_incidents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    return enterprise_service.get_security_incidents(db, current_user)


@router.get("/audit/logs")
async def get_audit_logs(
    limit: int = Query(30, ge=5, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    logs = audit_service.get_recent_audit_logs(db, limit=limit)
    return {
        "logs": [
            {
                "id": log.id,
                "tenant_id": log.tenant_id,
                "user_id": log.user_id,
                "module": log.module,
                "action": log.action,
                "metadata": getattr(log, "metadata_payload", None),
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ]
    }


@router.get("/workflows")
async def list_workflows(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    return {"workflows": enterprise_service.list_workflows(db, current_user)}


@router.post("/workflows/execute")
async def execute_workflow(
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    workflow_id = body.get("workflow_id")
    if not workflow_id:
        raise HTTPException(status_code=400, detail="workflow_id es requerido")
    context = body.get("context", {})
    return enterprise_service.execute_workflow(
        db, current_user, workflow_id, context=context
    )


@router.get("/monitoring/status")
async def get_monitoring_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    return enterprise_service.get_monitoring_status(db)


@router.get("/alerts")
async def get_alerts(
    limit: int = Query(25, ge=5, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    return {"alerts": enterprise_service.list_alerts(db, current_user, limit=limit)}


@router.get("/modules/{module_key}")
async def get_enterprise_module(
    module_key: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    return enterprise_service.get_module_workbench(db, current_user, module_key)


@router.post("/modules/{module_key}/actions")
async def execute_enterprise_module_action(
    module_key: str,
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    action_id = body.get("action_id")
    if not action_id:
        raise HTTPException(status_code=400, detail="action_id es requerido")
    return enterprise_service.execute_module_action(
        db,
        current_user,
        module_key,
        action_id,
        payload=body.get("payload", {}),
    )


@router.post("/alerts")
async def create_alert(
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    module = body.get("module")
    title = body.get("title")
    description = body.get("description")
    severity = body.get("severity", "warning")
    if not module or not title or not description:
        raise HTTPException(
            status_code=400, detail="module, title y description son requeridos"
        )
    alert = enterprise_service.raise_alert(
        db, current_user, module, title, description, severity=severity
    )
    return {
        "id": alert.id,
        "module": alert.module,
        "severity": alert.severity,
        "title": alert.title,
        "description": alert.description,
        "status": alert.status,
        "created_at": alert.created_at.isoformat(),
    }
