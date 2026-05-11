"""
Crea el usuario admin por defecto si la tabla está vacía.

Ejecutar tras migraciones: `python scripts/seed_admin.py` (desde el directorio backend/).
"""

import os
import sys

# Permite ejecutar sin instalar el paquete como módulo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal  # noqa: E402
from services.auth_service import ensure_default_admin  # noqa: E402


def main() -> None:
    db = SessionLocal()
    try:
        ensure_default_admin(db)
        print("seed_admin: OK (admin asegurado si hacía falta)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
