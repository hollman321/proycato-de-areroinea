"""
Punto de entrada FastAPI: ensambla middlewares, CORS y routers por dominio.

Los endpoints concretos viven en `routers/` para mantener este archivo pequeño y legible.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from core.config import settings
from middleware.errors import register_exception_handlers
from middleware.logging_middleware import RequestLoggingMiddleware
from routers import (
    admin,
    analytics,
    auth,
    enterprise,
    estadisticas,
    flights,
    health,
    pasajeros,
    reference,
)

logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


def create_app() -> FastAPI:
    app = FastAPI(
        title="SkyAnalytics Backend",
        version="2.0.0",
        description="API para analítica de pasajeros, autenticación JWT y operaciones empresariales.",
        contact={"name": "Equipo SkyAnalytics", "email": "admin@skyanalytics.com"},
        license_info={"name": "MIT"},
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True,
            "tryItOutEnabled": True,
        },
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(admin.router)
    app.include_router(analytics.router)
    app.include_router(enterprise.router)
    app.include_router(flights.router)
    app.include_router(estadisticas.router)
    app.include_router(pasajeros.router)
    app.include_router(reference.router)

    return app


app = create_app()
