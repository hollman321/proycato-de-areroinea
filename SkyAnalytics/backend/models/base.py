"""
Base declarativa de SQLAlchemy.

Todos los modelos heredan de Base para compartir metadata y migraciones Alembic.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
