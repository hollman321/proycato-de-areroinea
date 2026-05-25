"""
Servicio de auditoría para persistir y consultar eventos de plataforma.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from models.audit_log import AuditLog
from models.user import User


def log_audit_event(
    db: Session,
    user: Optional[User],
    module: str,
    action: str,
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    session_id: Optional[str] = None,
) -> AuditLog:
    tenant_id = getattr(user, "tenant_id", 1) if user else 1
    audit = AuditLog(
        tenant_id=tenant_id,
        user_id=user.id if user else None,
        module=module,
        action=action,
        metadata_payload=metadata or {},
        ip_address=ip_address,
        session_id=session_id,
        created_at=datetime.utcnow(),
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def get_recent_audit_logs(db: Session, limit: int = 30):
    return (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )
