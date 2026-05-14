"""
JWT y hashing de contraseñas.

JWT es stateless: el "logout" real implica olvidar el token en el cliente o usar lista de revocación (no incluida aquí).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Optional

from jose import jwt
from passlib.context import CryptContext

from core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    subject: str,
    *,
    remember_me: bool = False,
    extra_claims: Optional[dict[str, Any]] = None,
) -> str:
    """Genera JWT de acceso. Si remember_me=True, dura varios días en lugar de minutos."""
    if remember_me:
        delta = timedelta(days=settings.access_token_remember_days)
    else:
        delta = timedelta(minutes=settings.access_token_expire_minutes)

    expire = datetime.utcnow() + delta
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire}
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
