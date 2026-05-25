"""
Autenticación contra tabla `users`.

Mantiene un admin por defecto para entornos demo (misma credencial que documentación).
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from sqlalchemy.orm import Session

from core.security import get_password_hash, verify_password
from models.tenant import Tenant
from models.user import User

logger = logging.getLogger(__name__)

DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@skyanalytics.com")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD")


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == normalize_email(email)).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(
    db: Session,
    *,
    email: str,
    password: str,
    full_name: Optional[str] = None,
    role: str = "analyst",
    tenant_id: int = 1,
) -> User:
    user = User(
        email=normalize_email(email),
        hashed_password=get_password_hash(password),
        full_name=full_name,
        role=role,
        tenant_id=tenant_id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Usuario registrado: %s", user.email)
    return user


def ensure_default_admin(db: Session) -> None:
    """
    Si no hay usuarios y DEFAULT_ADMIN_PASSWORD está definido, crea el admin demo (idempotente).

    Útil en Docker el primer arranque sin pasos manuales.
    """
    if db.query(User).first() is not None or not DEFAULT_ADMIN_PASSWORD:
        return

    if db.query(Tenant).filter(Tenant.id == 1).first() is None:
        tenant = Tenant(id=1, name="Global Tenant", slug="global", is_active=True)
        db.add(tenant)
        db.commit()

    create_user(
        db,
        email=DEFAULT_ADMIN_EMAIL,
        password=DEFAULT_ADMIN_PASSWORD,
        full_name="Administrador",
        role="admin",
        tenant_id=1,
    )
    logger.warning(
        "Creado usuario admin por defecto (%s). Cambia la contraseña en producción.",
        DEFAULT_ADMIN_EMAIL,
    )
