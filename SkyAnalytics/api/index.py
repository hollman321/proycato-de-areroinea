import os
import sys
import logging

# Setup paths
_HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
BACKEND_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "backend"))

for _path in (PROJECT_ROOT, BACKEND_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create minimal FastAPI app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="SkyAnalytics Backend",
    version="2.0.0",
    description="API para analítica de pasajeros, autenticación JWT y operaciones empresariales.",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic routes
@app.get("/")
async def root():
    return {
        "message": "Bienvenido al backend de SkyAnalytics",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "online"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "SkyAnalytics Backend"}

# Attempt to load full app
try:
    logger.info("Attempting to import full main.app...")
    from main import app as full_app
    
    # If successful, use the full app but keep our basic endpoints
    for route in app.routes:
        full_app.routes.append(route) if route not in full_app.routes else None
    
    app = full_app
    logger.info("✓ Full application loaded successfully")
    
except Exception as e:
    logger.error(f"✗ Failed to load full application: {e}", exc_info=True)
    logger.info("Running in minimal mode with basic endpoints only")

