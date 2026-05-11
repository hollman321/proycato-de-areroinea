FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Migraciones + usuario demo + API (ajusta si no usas Alembic en tu entorno).
CMD ["sh", "-c", "alembic upgrade head && python scripts/seed_admin.py && uvicorn main:app --host 0.0.0.0 --port 8000"]