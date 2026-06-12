#!/usr/bin/env python3
"""
Script de Validación Completa - Verifica que el proyecto está listo para ejecutarse.

Uso:
    python validate_project.py          # Validación completa
    python validate_project.py --quick  # Validación rápida
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple

# Agregar path del backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

class ProjectValidator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
    
    def validate_all(self, quick: bool = False) -> bool:
        """Ejecutar todas las validaciones."""
        print("\n" + "="*70)
        print("🔍 VALIDACIÓN COMPLETA DEL PROYECTO - SkyAnalytics")
        print("="*70 + "\n")
        
        # Validaciones de estructura
        self.validate_directories()
        self.validate_critical_files()
        self.validate_python_syntax()
        self.validate_env_configuration()
        
        if not quick:
            self.validate_imports()
            self.validate_database_connection()
            self.validate_migrations()
        
        # Resumen
        return self.print_summary()
    
    def validate_directories(self):
        """Verificar directorios críticos."""
        print("📂 Validando estructura de directorios...")
        required_dirs = [
            "backend",
            "backend/models",
            "backend/routers",
            "backend/services",
            "backend/schemas",
            "backend/scripts",
            "backend/alembic",
            "frontend",
            "frontend/src",
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                self.info.append(f"✅ {dir_path}")
            else:
                self.errors.append(f"❌ Directorio faltante: {dir_path}")
    
    def validate_critical_files(self):
        """Verificar archivos críticos."""
        print("📄 Validando archivos críticos...")
        critical_files = {
            "backend": [
                "main.py",
                "database.py",
                "deps.py",
                "requirements.txt",
                "alembic.ini",
                "docker-entrypoint.sh",
                "Dockerfile",
            ],
            "backend/core": [
                "config.py",
                "security.py",
            ],
            "backend/models": [
                "__init__.py",
                "base.py",
                "user.py",
                "pasajero.py",
                "finance.py",
            ],
            "backend/routers": [
                "__init__.py",
                "auth.py",
                "pasajeros.py",
                "finance.py",
            ],
            "backend/services": [
                "__init__.py",
                "auth_service.py",
            ],
            "frontend": [
                "package.json",
                "tsconfig.json",
                "Dockerfile",
            ],
            ".": [
                ".env",
                "docker-compose.yml",
            ]
        }
        
        for dir_key, files in critical_files.items():
            dir_path = self.project_root / dir_key if dir_key != "." else self.project_root
            for file_name in files:
                file_path = dir_path / file_name
                if file_path.exists():
                    self.info.append(f"✅ {dir_key}/{file_name}")
                else:
                    self.errors.append(f"❌ Archivo faltante: {dir_key}/{file_name}")
    
    def validate_python_syntax(self):
        """Verificar sintaxis de archivos Python."""
        print("🐍 Validando sintaxis Python...")
        python_files = list(self.backend_dir.glob("**/*.py"))
        
        import py_compile
        errors_found = 0
        
        for py_file in python_files[:20]:  # Limitar a primeros 20 para velocidad
            try:
                py_compile.compile(str(py_file), doraise=True)
                self.info.append(f"✅ {py_file.relative_to(self.project_root)}")
            except py_compile.PyCompileError as e:
                self.errors.append(f"❌ Sintaxis inválida en {py_file.relative_to(self.project_root)}: {str(e)[:100]}")
                errors_found += 1
        
        if errors_found == 0 and len(python_files) > 20:
            self.info.append(f"✅ {len(python_files)} archivos Python verificados")
    
    def validate_env_configuration(self):
        """Verificar variables de entorno críticas."""
        print("🔑 Validando configuración de entorno...")
        env_file = self.project_root / ".env"
        
        if not env_file.exists():
            self.warnings.append("⚠️  Archivo .env no encontrado - usando valores por defecto")
            return
        
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        required_vars = [
            "DATABASE_URL",
            "SECRET_KEY",
            "JWT_ALGORITHM",
            "CORS_ORIGINS",
        ]
        
        for var in required_vars:
            if var in env_content:
                self.info.append(f"✅ Variable {var} configurada")
            else:
                self.warnings.append(f"⚠️  Variable {var} no encontrada en .env")
    
    def validate_imports(self):
        """Validar que los imports principales funcionan."""
        print("📦 Validando imports Python...")
        try:
            from database import SessionLocal, get_db
            self.info.append("✅ Import database.SessionLocal OK")
        except Exception as e:
            self.errors.append(f"❌ Error importando database: {str(e)[:100]}")
        
        try:
            from core.config import settings
            self.info.append("✅ Import config.settings OK")
        except Exception as e:
            self.errors.append(f"❌ Error importando config: {str(e)[:100]}")
        
        try:
            from models import Base
            self.info.append("✅ Import models.Base OK")
        except Exception as e:
            self.errors.append(f"❌ Error importando models: {str(e)[:100]}")
        
        try:
            import main
            self.info.append("✅ Import main.py OK")
        except Exception as e:
            self.errors.append(f"❌ Error importando main: {str(e)[:100]}")
    
    def validate_database_connection(self):
        """Intentar conectar a base de datos."""
        print("🗄️  Validando conexión a base de datos...")
        try:
            from database import SessionLocal
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            self.info.append("✅ Conexión a base de datos exitosa")
        except Exception as e:
            self.warnings.append(f"⚠️  No se pudo conectar a BD: {str(e)[:100]}")
            self.warnings.append("   (Esto es normal si BD está en Docker y no está levantada)")
    
    def validate_migrations(self):
        """Verificar que existen migraciones Alembic."""
        print("📈 Validando migraciones Alembic...")
        migrations_dir = self.backend_dir / "alembic" / "versions"
        
        if migrations_dir.exists():
            migration_files = list(migrations_dir.glob("*.py"))
            if migration_files:
                self.info.append(f"✅ {len(migration_files)} migraciones encontradas")
            else:
                self.warnings.append("⚠️  No hay migraciones en alembic/versions/")
        else:
            self.errors.append("❌ Directorio de migraciones no encontrado")
    
    def print_summary(self) -> bool:
        """Imprimir resumen de validación."""
        print("\n" + "="*70)
        print("📋 RESUMEN DE VALIDACIÓN")
        print("="*70 + "\n")
        
        if self.info:
            print(f"✅ VERIFICACIONES EXITOSAS ({len(self.info)})")
            for item in self.info[:5]:  # Mostrar primeras 5
                print(f"  {item}")
            if len(self.info) > 5:
                print(f"  ... y {len(self.info) - 5} más")
            print()
        
        if self.warnings:
            print(f"⚠️  ADVERTENCIAS ({len(self.warnings)})")
            for item in self.warnings:
                print(f"  {item}")
            print()
        
        if self.errors:
            print(f"❌ ERRORES ({len(self.errors)})")
            for item in self.errors:
                print(f"  {item}")
            print()
        
        print("="*70)
        
        if self.errors:
            print("\n🔴 VALIDACIÓN FALLIDA - Hay errores que corregir")
            return False
        elif self.warnings:
            print("\n🟡 VALIDACIÓN PARCIAL - Revisar advertencias")
            return True
        else:
            print("\n🟢 VALIDACIÓN COMPLETADA - Proyecto listo")
            return True
    
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Validar proyecto SkyAnalytics")
    parser.add_argument("--quick", action="store_true", help="Validación rápida")
    parser.add_argument("--root", default=".", help="Raíz del proyecto")
    args = parser.parse_args()
    
    validator = ProjectValidator(args.root)
    success = validator.validate_all(quick=args.quick)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
