"""Rutas públicas de salud y bienvenida."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_connection_info, get_db

router = APIRouter(tags=["Health"])


@router.get("/")
async def root():
    return {
        "message": "Welcome to SkyAnalytics Backend",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@router.get("/health")
async def health():
    return {"status": "healthy"}


@router.get("/health/system")
async def health_system(db: Session = Depends(get_db)):
    status = "online"
    error = None
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        status = "offline"
        error = str(exc)

    return {
        "api_gateway": {
            "status": "online",
            "message": "API Gateway disponible",
            "latency": "-",
        },
        "database": {
            "status": status,
            "message": (
                "Conexión a PostgreSQL establecida"
                if status == "online"
                else "No se puede conectar a la base de datos"
            ),
            "latency": "-",
            "info": get_connection_info(),
            "error": error,
        },
        "services": {
            "ia_engine": {
                "status": "offline",
                "message": "No hay servicio IA configurado",
                "latency": "-",
            }
        },
    }
