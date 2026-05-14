FROM python:3.9-slim

WORKDIR /app

# Copiar requirements desde dashboard
COPY dashboard/requirements.txt .
RUN pip install -r requirements.txt

# Copiar el .env desde la raíz del proyecto
COPY .env* ./

# Copiar código del dashboard
COPY dashboard/ ./

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]