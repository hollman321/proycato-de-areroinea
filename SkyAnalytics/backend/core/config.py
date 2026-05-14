"""
Configuración central leída del entorno.

Buena práctica: nunca commitear secretos reales; usar .env (ver .env.example en la raíz del proyecto).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    """Valores de configuración inmutables tras el primer load."""

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    access_token_remember_days: int
    cors_origins: list[str]
    log_level: str


@lru_cache
def get_settings() -> Settings:
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise ValueError("SECRET_KEY environment variable is required")

    # CORS: lista separada por comas, o "*" para desarrollo
    raw_cors = os.getenv("CORS_ORIGINS", "*").strip()
    if raw_cors == "*":
        cors: list[str] = ["*"]
    else:
        cors = [o.strip() for o in raw_cors.split(",") if o.strip()]

    return Settings(
        secret_key=secret_key,
        algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        access_token_remember_days=int(os.getenv("ACCESS_TOKEN_REMEMBER_DAYS", "7")),
        cors_origins=cors,
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )


settings = get_settings()
