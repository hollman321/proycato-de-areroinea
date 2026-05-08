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
import dotenv

# Cargar variables de entorno
dotenv.load_dotenv()

# ==================== CONFIGURACIÓN ====================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:secretpassword@db:5432/skyanalytics"
)

# Importer modelos AQUÍ para evitar circular imports
from models import Base

# ==================== ENGINE Y SESIONES ====================
# echo=True muestra SQL en logs (desactiva en producción)
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a True para debug
    pool_size=20,  # Conexiones simultáneas
    max_overflow=0,  # No crear conexiones extras
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Crear tablas
Base.metadata.create_all(bind=engine)


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
    return {
        "database_url": DATABASE_URL,
        "engine": str(engine),
        "pool_size": engine.pool.size(),
        "checked_out": engine.pool.checkedout(),
    }
