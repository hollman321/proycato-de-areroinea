"""
Caché Redis para agregados del dashboard (ventana 30s).

Soporta multi-instancia con Redis centralizado.
"""

from __future__ import annotations

import json
import os
from typing import Any, Callable, TypeVar

import redis

T = TypeVar("T")

# Segundos — alineado con especificación SkyAnalytics Operational Intelligence
TTL_SECONDS = 30

# Conexión Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=int(os.getenv("REDIS_DB", "0")),
    decode_responses=True,
)


def get_cached(key: str, factory: Callable[[], T]) -> T:
    """
    Devuelve `factory()` si la clave expiró o no existe; si no, devuelve el valor cacheado desde Redis.

    `factory` debe ser barato de construir en cierre; típicamente llama consultas SQL con la sesión ya abierta.
    """
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)

    val = factory()
    redis_client.setex(key, TTL_SECONDS, json.dumps(val))
    return val


def cache_ttl_seconds() -> int:
    return TTL_SECONDS
