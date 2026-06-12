import os
import sys
import logging

# Entrada serverless (Vercel) y local: asegurar raíz del monorepo SkyAnalytics y backend en sys.path.
_HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
BACKEND_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "backend"))

# Orden: primero PROJECT_ROOT, luego BACKEND insertado al inicio => [BACKEND_DIR, PROJECT_ROOT, ...]
for _path in (PROJECT_ROOT, BACKEND_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from main import app  # noqa: E402
except Exception as e:
    logger.error(f"Error al importar main.app: {e}", exc_info=True)
    # Crear app de emergencia que al menos responde
    from fastapi import FastAPI
    app = FastAPI(title="SkyAnalytics - Recovery Mode")
    
    @app.get("/")
    async def root():
        return {
            "message": "SkyAnalytics Backend - Recovery Mode",
            "error": "No se pudo cargar la aplicación principal. Revisa los logs en Vercel."
        }
    
    @app.get("/health")
    async def health():
        return {"status": "degraded", "error": str(e)}
