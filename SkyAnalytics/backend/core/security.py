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

# FastAPI imports para autenticación
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from models.user import User
from database import get_db
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Alias antiguo: algunas scripts esperan `hash_password`
def hash_password(password: str) -> str:
    return get_password_hash(password)


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


# --- NUEVO: get_current_user para FastAPI ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # Buscar usuario en la base de datos
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
