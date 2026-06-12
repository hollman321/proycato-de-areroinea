"""
Punto de entrada FastAPI: ensambla middlewares, CORS y routers por dominio.

Los endpoints concretos viven en `routers/` para mantener este archivo pequeño y legible.
"""

from __future__ import annotations

import logging
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from core.config import settings
from middleware.errors import register_exception_handlers
from middleware.logging_middleware import RequestLoggingMiddleware

logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Importar routers con manejo de errores
routers_to_load = [
    ("health", "routers.health"),
    ("auth", "routers.auth"),
    ("admin", "routers.admin"),
    ("analytics", "routers.analytics"),
    ("enterprise", "routers.enterprise"),
    ("finance", "routers.finance"),
    ("flights", "routers.flights"),
    ("estadisticas", "routers.estadisticas"),
    ("operaciones", "routers.operaciones"),
    ("pasajeros", "routers.pasajeros"),
    ("reference", "routers.reference"),
    ("ia", "routers.ia"),
]

loaded_routers = {}
for name, module_path in routers_to_load:
    try:
        mod = __import__(module_path, fromlist=["router"])
        loaded_routers[name] = mod.router
        logger.info(f"✓ Router '{name}' cargado exitosamente")
    except Exception as e:
        logger.warning(f"✗ No se pudo cargar router '{name}': {e}")

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

    # Configurar CORS desde settings
    cors_origins = settings.cors_origins or ["*"]

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    # Cargar routers disponibles
    for name, router in loaded_routers.items():
        app.include_router(router)
        logger.info(f"Router '{name}' incluido en la app")

    return app

app = create_app()
