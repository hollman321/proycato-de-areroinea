#!/usr/bin/env python3
"""Resetea la contraseña del admin por defecto a la variable DEFAULT_ADMIN_PASSWORD.
Usar sólo en entornos locales de desarrollo.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from services.auth_service import normalize_email, DEFAULT_ADMIN_EMAIL
from core.security import get_password_hash
from models.user import User


def main():
    db = SessionLocal()
    try:
        email = os.getenv("DEFAULT_ADMIN_EMAIL", DEFAULT_ADMIN_EMAIL)
        new_pass = os.getenv("DEFAULT_ADMIN_PASSWORD")
        if not new_pass:
            print("DEFAULT_ADMIN_PASSWORD no está definido en el entorno; abortando.")
            return

        user = db.query(User).filter(User.email == normalize_email(email)).first()
        if not user:
            print(f"Usuario {email} no encontrado; seed_admin normalmente crea uno si la tabla está vacía.")
            return

        user.hashed_password = get_password_hash(new_pass)
        db.add(user)
        db.commit()
        print(f"Contraseña del usuario {email} reseteada correctamente.")
    finally:
        db.close()


if __name__ == '__main__':
    main()
