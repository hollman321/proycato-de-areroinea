#!/bin/sh
set -e

python - <<'PY'
import os
import time

import psycopg2

database_url = os.getenv("DATABASE_URL", "postgresql://admin:secretpassword@db:5432/skyanalytics")

for attempt in range(60):
    try:
        conn = psycopg2.connect(database_url)
        conn.close()
        print("database: ready")
        break
    except Exception as exc:
        if attempt == 59:
            raise
        print(f"database: waiting ({exc})")
        time.sleep(2)
PY

alembic upgrade head
python scripts/seed_admin.py

exec uvicorn main:app --host 0.0.0.0 --port 8000
