"""
Configuración centralizada de base de datos.

Este módulo centraliza:
- Conexión a PostgreSQL
- Creación de tablas
- Sesión SQLAlchemy
- Dependency injection para BD
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, StaticPool
from dotenv import load_dotenv

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)

# En Docker, el .env está en /app/; en desarrollo, está en SkyAnalytics/
# Intentar cargar desde múltiples ubicaciones
for env_path in [
    os.path.join(_PROJECT_ROOT, ".env"),  # SkyAnalytics/.env (desarrollo)
    os.path.join(_BACKEND_DIR, ".env"),  # backend/.env (alternativo)
    ".env",  # Ruta actual
]:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

load_dotenv()  # Cargar cualquier variable de entorno disponible

# ==================== CONFIGURACIÓN ====================
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://admin:secretpassword@db:5432/skyanalytics"
)

# Importar modelos AQUÍ para evitar circular imports.
# Intentar import relativo cuando el paquete se ejecute como paquete,
# y hacer fallback a la importación absoluta cuando se ejecute desde el directorio.
try:
    from .models import Base  # type: ignore
except Exception:
    from models import Base  # type: ignore

# ==================== ENGINE Y SESIONES ====================
# echo=True muestra SQL en logs (desactiva en producción)
IS_SERVERLESS = os.getenv("VERCEL") == "1"
IS_SQLITE = DATABASE_URL.startswith("sqlite")

engine_args = {
    "echo": False,  # Cambiar a True para debug
}

if IS_SQLITE:
    engine_args["connect_args"] = {"check_same_thread": False}
    if DATABASE_URL in {"sqlite://", "sqlite:///:memory:"}:
        engine_args["poolclass"] = StaticPool
elif IS_SERVERLESS:
    # En serverless evitamos mantener pools persistentes por instancia.
    engine_args["pool_pre_ping"] = True
    engine_args["poolclass"] = NullPool
else:
    engine_args["pool_pre_ping"] = True
    engine_args["pool_size"] = 20
    engine_args["max_overflow"] = 0

engine = create_engine(DATABASE_URL, **engine_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas al importar; en serverless la BD puede no estar aún (p. ej. sin DATABASE_URL en Vercel).
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    import logging

    logging.getLogger(__name__).warning(
        "No se pudieron crear tablas al iniciar (¿DATABASE_URL o red?). La API arrancará; revisa la BD.",
        exc_info=True,
    )


# ==================== DEPENDENCY INJECTION ====================
def get_db() -> Session:
    """
    Inyección de dependencia para la sesión de BD.

    FastAPI llama esto automáticamente para cada request.
    La sesión se abre ANTES del endpoint y se cierra DESPUÉS.

    Uso en endpoints:
        @app.get("/endpoint")
        async def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== UTILIDADES ====================
def init_db():
    """Inicializa la base de datos (crea tablas)"""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Elimina todas las tablas (PELIGROSO - solo desarrollo)"""
    Base.metadata.drop_all(bind=engine)


def get_connection_info() -> dict:
    """Retorna información de conexión (para debug)"""
    pool = engine.pool
    try:
        pool_size = pool.size()
        checked_out = pool.checkedout()
    except Exception:
        pool_size = None
        checked_out = None
    return {
        "database_url": DATABASE_URL,
        "engine": str(engine),
        "pool_size": pool_size,
        "checked_out": checked_out,
    }
