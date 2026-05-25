"""
Caché Redis para agregados del dashboard.

Soporta multi-instancia con Redis centralizado.
"""

from __future__ import annotations

import fnmatch
import json
import os
import time
from typing import Any, Callable, TypeVar

import redis
from redis.exceptions import RedisError

T = TypeVar("T")

# Segundos. El dashboard no necesita recalcular agregados pesados en cada visita.
TTL_SECONDS = int(os.getenv("ANALYTICS_CACHE_TTL_SECONDS", "60"))
REDIS_RETRY_COOLDOWN_SECONDS = float(os.getenv("REDIS_RETRY_COOLDOWN_SECONDS", "30"))
REDIS_CACHE_DISABLED = os.getenv("DISABLE_REDIS_CACHE", "0").lower() in {
    "1",
    "true",
    "yes",
}

_memory_cache: dict[str, tuple[float, Any]] = {}
_redis_disabled_until = 0.0

# Conexión Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=int(os.getenv("REDIS_DB", "0")),
    decode_responses=True,
    socket_connect_timeout=0.15,
    socket_timeout=0.25,
)


def get_cached(key: str, factory: Callable[[], T]) -> T:
    """
    Devuelve `factory()` si la clave expiró o no existe; si no, devuelve el valor cacheado desde Redis.

    `factory` debe ser barato de construir en cierre; típicamente llama consultas SQL con la sesión ya abierta.
    """
    global _redis_disabled_until
    now = time.time()

    cached_memory = _memory_cache.get(key)
    if cached_memory and cached_memory[0] > now:
        return cached_memory[1]

    redis_available = not REDIS_CACHE_DISABLED and now >= _redis_disabled_until
    if redis_available:
        try:
            cached = redis_client.get(key)
            if cached:
                val = json.loads(cached)
                _memory_cache[key] = (now + TTL_SECONDS, val)
                return val
        except RedisError:
            _redis_disabled_until = now + REDIS_RETRY_COOLDOWN_SECONDS

    val = factory()
    _memory_cache[key] = (now + TTL_SECONDS, val)
    if redis_available:
        try:
            redis_client.setex(key, TTL_SECONDS, json.dumps(val, default=str))
        except RedisError:
            _redis_disabled_until = now + REDIS_RETRY_COOLDOWN_SECONDS
    return val


def invalidate_dashboard_cache() -> None:
    """Limpia agregados del dashboard cuando cambian pasajeros/transacciones."""
    global _redis_disabled_until
    patterns = [
        "analytics:*",
    ]
    if REDIS_CACHE_DISABLED or time.time() < _redis_disabled_until:
        for key in list(_memory_cache):
            if any(fnmatch.fnmatch(key, pattern) for pattern in patterns):
                _memory_cache.pop(key, None)
        return

    try:
        keys: list[str] = []
        for pattern in patterns:
            keys.extend(redis_client.keys(pattern))
        if keys:
            redis_client.delete(*keys)
    except RedisError:
        _redis_disabled_until = time.time() + REDIS_RETRY_COOLDOWN_SECONDS
        for key in list(_memory_cache):
            if any(fnmatch.fnmatch(key, pattern) for pattern in patterns):
                _memory_cache.pop(key, None)


def cache_ttl_seconds() -> int:
    return TTL_SECONDS
