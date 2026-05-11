"""Rutas públicas de salud y bienvenida."""

from fastapi import APIRouter

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
