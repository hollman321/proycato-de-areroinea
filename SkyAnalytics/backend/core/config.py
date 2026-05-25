"""
Configuración central leída del entorno.

Buena práctica: nunca commitear secretos reales; usar .env (ver .env.example en la raíz del proyecto).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


_CORE_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.dirname(_CORE_DIR)
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)

for env_path in (
    os.path.join(_PROJECT_ROOT, ".env"),
    os.path.join(_BACKEND_DIR, ".env"),
    ".env",
):
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Valores de configuración inmutables tras el primer load."""

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    access_token_remember_days: int
    cors_origins: list[str]
    log_level: str
    openai_api_key: str
    openai_model: str


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
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    )


settings = get_settings()
