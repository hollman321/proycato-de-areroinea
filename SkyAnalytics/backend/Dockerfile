FROM python:3.9-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copiar requirements desde backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del backend
COPY backend/ ./

EXPOSE 8000

# Esperar DB, ejecutar migraciones + usuario demo + API
CMD ["sh", "/app/docker-entrypoint.sh"]
