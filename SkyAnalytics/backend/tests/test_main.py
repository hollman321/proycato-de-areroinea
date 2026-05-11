import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db
import os

# Configuración de BD de pruebas
TEST_DATABASE_URL = "postgresql://admin:secretpassword@db:5432/skyanalytics_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_root():
    """Test endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    assert "SkyAnalytics Backend" in response.json()["message"]

def test_health():
    """Test endpoint de salud"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_login_success():
    """Test login exitoso"""
    response = client.post("/auth/login", json={
        "email": "admin@skyanalytics.com",
        "password": "admin123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure():
    """Test login fallido"""
    response = client.post("/auth/login", json={
        "email": "admin@skyanalytics.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_create_pasajero():
    """Test crear pasajero"""
    # Primero obtener token
    login_response = client.post("/auth/login", json={
        "email": "admin@skyanalytics.com",
        "password": "admin123"
    })
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    pasajero_data = {
        "nombre_completo": "Juan Pérez",
        "correo": "juan.perez@example.com",
        "tarjeta_credito": "4111111111111111",
        "tarjeta_debito": "5111111111111111",
        "direccion": "Calle Falsa 123",
        "ciudad": "Madrid",
        "pais": "España",
        "fecha_registro": "2023-01-01"
    }
    
    response = client.post("/pasajeros", json=pasajero_data, headers=headers)
    assert response.status_code == 201
    assert response.json()["correo"] == "juan.perez@example.com"

def test_listar_pasajeros():
    """Test listar pasajeros"""
    response = client.get("/pasajeros?limit=10")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "pagination" in response.json()