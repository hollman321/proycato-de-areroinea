import os
import sys

# Entrada serverless (Vercel) y local: asegurar raíz del monorepo SkyAnalytics y backend en sys.path.
_HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
BACKEND_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "backend"))

# Orden: primero PROJECT_ROOT, luego BACKEND insertado al inicio => [BACKEND_DIR, PROJECT_ROOT, ...]
for _path in (PROJECT_ROOT, BACKEND_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from main import app  # noqa: E402
