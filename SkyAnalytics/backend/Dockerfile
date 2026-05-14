FROM python:3.9-slim

WORKDIR /app

# Copiar requirements desde backend
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

# Copiar el .env desde la raíz del proyecto (disponible con context: . en docker-compose)
COPY .env* ./

# Copiar código del backend
COPY backend/ ./

# Migraciones + usuario demo + API
CMD ["sh", "-c", "alembic upgrade head && python scripts/seed_admin.py && uvicorn main:app --host 0.0.0.0 --port 8000"]