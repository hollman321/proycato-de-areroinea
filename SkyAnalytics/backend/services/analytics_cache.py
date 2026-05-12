"""
Caché en memoria para agregados del dashboard (ventana 30s).

Regla de negocio: no recalcular KPIs pesados más de una vez cada 30 segundos por clave lógica.
No sustituye Redis en multi-instancia; para un solo worker de API es suficiente.
"""

from __future__ import annotations

import time
from typing import Any, Callable, TypeVar

T = TypeVar("T")

# Segundos — alineado con especificación SkyAnalytics Operational Intelligence
TTL_SECONDS = 30.0

_store: dict[str, tuple[float, Any]] = {}


def get_cached(key: str, factory: Callable[[], T]) -> T:
    """
    Devuelve `factory()` si la clave expiró o no existe; si no, devuelve el valor cacheado.

    `factory` debe ser barato de construir en cierre; típicamente llama consultas SQL con la sesión ya abierta.
    """
    now = time.monotonic()
    entry = _store.get(key)
    if entry is not None:
        ts, val = entry
        if now - ts < TTL_SECONDS:
            return val
    val = factory()
    _store[key] = (now, val)
    return val


def cache_ttl_seconds() -> int:
    return int(TTL_SECONDS)
