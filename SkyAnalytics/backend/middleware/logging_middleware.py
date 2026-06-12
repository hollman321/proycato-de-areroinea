"""Log de peticiones HTTP (método, ruta, status, duración aproximada)."""

from __future__ import annotations

import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("skyanalytics.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()

        # Leer y registrar el cuerpo para diagnósticos solo en /auth/login
        try:
            if request.method.upper() == "POST" and request.url.path == "/auth/login":
                body = await request.body()
                try:
                    logger.info("Raw body for /auth/login: %s", body.decode('utf-8', errors='replace'))
                except Exception:
                    logger.info("Raw body for /auth/login: (binary data)")

                # Reconstruir el receive para que downstream pueda leer el body otra vez
                async def receive() -> dict:
                    return {"type": "http.request", "body": body, "more_body": False}

                request._receive = receive  # type: ignore[attr-defined]

        except Exception:
            logger.exception("Error leyendo cuerpo de la petición para diagnóstico")

        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s -> %s (%.1f ms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        return response
