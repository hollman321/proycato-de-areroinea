"""
Punto de entrada FastAPI: ensambla middlewares, CORS y routers por dominio.

Los endpoints concretos viven en `routers/` para mantener este archivo pequeño y legible.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from middleware.errors import register_exception_handlers
from middleware.logging_middleware import RequestLoggingMiddleware
from routers import analytics, auth, estadisticas, health, pasajeros

logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))


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
    app.include_router(analytics.router)
    app.include_router(estadisticas.router)
    app.include_router(pasajeros.router)

    return app


app = create_app()
