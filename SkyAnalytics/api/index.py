import os
import sys

# Permite importar el backend como modulo en el runtime de Vercel.
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app  # noqa: E402,F401
