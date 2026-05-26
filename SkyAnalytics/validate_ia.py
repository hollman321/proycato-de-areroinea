#!/usr/bin/env python3
"""
Script de Validación del Módulo IA
Verifica que todos los archivos estén presentes y sean válidos
"""

import os
import sys
from pathlib import Path


def check_file_exists(path: str, file_type: str = "backend") -> bool:
    """Verifica que un archivo existe"""
    if os.path.exists(path):
        print(f"✅ {file_type}: {path}")
        return True
    else:
        print(f"❌ {file_type}: {path} - NO ENCONTRADO")
        return False


def check_file_contains(path: str, search_string: str, description: str = "") -> bool:
    """Verifica que un archivo contiene cierto texto"""
    if not os.path.exists(path):
        print(f"❌ {description}: Archivo no existe")
        return False

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            if search_string in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description}: No se encontró el código")
                return False
    except Exception as e:
        print(f"❌ {description}: Error al leer - {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("🔍 VALIDACIÓN DEL MÓDULO IA DE SKYANALYTICS")
    print("=" * 60 + "\n")

    base_path = Path(__file__).parent
    all_good = True

    # ============ VALIDACIÓN DE ARCHIVOS CREADOS ============
    print("📁 ARCHIVOS CREADOS:")
    print("-" * 60)

    backend_files = [
        ("backend/services/ia_service.py", "Service IA"),
        ("backend/routers/ia.py", "Router IA"),
        ("backend/schemas/ia.py", "Schemas IA"),
    ]

    for file_path, desc in backend_files:
        full_path = base_path / file_path
        if not check_file_exists(str(full_path), desc):
            all_good = False

    print()

    frontend_files = [
        ("frontend/src/components/ChatIA.tsx", "Componente ChatIA"),
        ("frontend/src/services/ia.ts", "Servicio IA Frontend"),
        ("frontend/src/hooks/useChatIA.ts", "Hook useChatIA"),
        ("frontend/src/lib/ia-config.ts", "Configuración IA"),
    ]

    for file_path, desc in frontend_files:
        full_path = base_path / file_path
        if not check_file_exists(str(full_path), desc):
            all_good = False

    # ============ VALIDACIÓN DE DOCUMENTACIÓN ============
    print("\n📚 DOCUMENTACIÓN:")
    print("-" * 60)

    docs = [
        ("IA_README.md", "README del módulo IA"),
        ("SETUP_IA.md", "Guía de Setup"),
        ("IMPLEMENTATION_SUMMARY.md", "Resumen de Implementación"),
    ]

    for file_path, desc in docs:
        full_path = base_path / file_path
        if not check_file_exists(str(full_path), desc):
            all_good = False

    # ============ VALIDACIÓN DE MODIFICACIONES ============
    print("\n🔧 ARCHIVOS MODIFICADOS:")
    print("-" * 60)

    # Verificar que main.py contiene la importación de ia
    main_py_path = base_path / "backend" / "main.py"
    if check_file_contains(
        str(main_py_path), "from routers import", "Import en backend/main.py"
    ):
        pass
    else:
        all_good = False

    if check_file_contains(
        str(main_py_path), "include_router(ia.router)", "Router registrado en main.py"
    ):
        pass
    else:
        all_good = False

    # Verificar que DashboardLayout contiene ChatIA
    layout_path = base_path / "frontend" / "src" / "layouts" / "DashboardLayout.tsx"
    if check_file_contains(
        str(layout_path), "import { ChatIA }", "Import de ChatIA en layout"
    ):
        pass
    else:
        all_good = False

    if check_file_contains(
        str(layout_path),
        "<ChatIA currentRoute={pathname} />",
        "Componente ChatIA en layout",
    ):
        pass
    else:
        all_good = False

    # ============ VALIDACIÓN DE CONTENIDO ============
    print("\n📝 VALIDACIÓN DE CONTENIDO:")
    print("-" * 60)

    # Verificar que ia_service tiene la base de conocimiento
    ia_service_path = base_path / "backend" / "services" / "ia_service.py"
    if check_file_contains(
        str(ia_service_path), "SYSTEM_KNOWLEDGE", "Base de conocimiento definida"
    ):
        pass
    else:
        all_good = False

    if check_file_contains(
        str(ia_service_path), "COMMON_QUESTIONS", "Preguntas frecuentes definidas"
    ):
        pass
    else:
        all_good = False

    # Verificar que el router tiene los endpoints
    ia_router_path = base_path / "backend" / "routers" / "ia.py"
    endpoints = [
        ('@router.get("/greeting")', "Endpoint greeting"),
        ('@router.post("/chat")', "Endpoint chat"),
        ('@router.post("/context")', "Endpoint context"),
        ('@router.post("/help")', "Endpoint help"),
    ]

    for endpoint, desc in endpoints:
        if check_file_contains(str(ia_router_path), endpoint, desc):
            pass
        else:
            all_good = False

    # Verificar que ChatIA tiene animaciones
    chat_ia_path = base_path / "frontend" / "src" / "components" / "ChatIA.tsx"
    if check_file_contains(str(chat_ia_path), "motion", "Animaciones de Framer Motion"):
        pass
    else:
        all_good = False

    # ============ RESUMEN ============
    print("\n" + "=" * 60)
    if all_good:
        print("✅ ¡VALIDACIÓN COMPLETADA EXITOSAMENTE!")
        print("   Todos los archivos están presentes y correctamente configurados.")
        print("\n📋 Próximos pasos:")
        print("   1. Verifica que las dependencias estén instaladas")
        print(
            "   2. Inicia el backend: py -m uvicorn main:app --host 0.0.0.0 --port 8001"
        )
        print("   3. Inicia el frontend: npm run dev")
        print("   4. Abre http://localhost:3000 en tu navegador")
        print("   5. Login y busca el botón azul en la esquina inferior derecha")
        return 0
    else:
        print("❌ VALIDACIÓN FALLIDA")
        print("   Algunos archivos están faltando o mal configurados.")
        print("   Revisa los errores arriba e intenta de nuevo.")
        return 1

    print("=" * 60 + "\n")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
