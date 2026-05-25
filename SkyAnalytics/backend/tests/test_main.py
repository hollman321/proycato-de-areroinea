"""Pruebas básicas de salud, autenticación y pasajeros."""

import uuid


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "SkyAnalytics Backend" in response.json()["message"]


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_login_success(client):
    response = client.post(
        "/auth/login",
        json={"email": "admin@skyanalytics.com", "password": "admin123", "remember_me": False},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_failure(client):
    response = client.post(
        "/auth/login",
        json={"email": "admin@skyanalytics.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_listar_pasajeros_requires_auth(client):
    r = client.get("/pasajeros?limit=10")
    assert r.status_code == 401


def test_create_pasajero(client):
    login_response = client.post(
        "/auth/login",
        json={"email": "admin@skyanalytics.com", "password": "admin123"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    uid = uuid.uuid4().hex[:8]
    pasajero_data = {
        "nombre_completo": "Juan Pérez",
        "correo": f"juan.perez.{uid}@example.com",
        "tarjeta_credito": "4111111111111111",
        "tarjeta_debito": "5555555555554444",
        "direccion": "Calle Falsa 123",
        "ciudad": "Madrid",
        "pais": "España",
        "fecha_registro": "2023-01-01",
    }

    response = client.post("/pasajeros", json=pasajero_data, headers=headers)
    assert response.status_code == 201
    assert response.json()["correo"] == pasajero_data["correo"]


def test_listar_pasajeros(client):
    login_response = client.post(
        "/auth/login",
        json={"email": "admin@skyanalytics.com", "password": "admin123"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/pasajeros?limit=10", headers=headers)
    assert response.status_code == 200
    assert "items" in response.json()
    assert "pagination" in response.json()


def _auth_headers(client):
    login_response = client.post(
        "/auth/login",
        json={"email": "admin@skyanalytics.com", "password": "admin123"},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_enterprise_ai_recommendations(client):
    response = client.get(
        "/admin/enterprise/ai/recommendations",
        headers=_auth_headers(client),
    )
    assert response.status_code == 200
    body = response.json()
    assert "recommendations" in body
    assert len(body["recommendations"]) >= 1


def test_enterprise_module_action_creates_operational_result(client):
    response = client.post(
        "/admin/enterprise/modules/finance/actions",
        json={"action_id": "simulate_revenue", "payload": {"scenario": "base"}},
        headers=_auth_headers(client),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "executed"
    assert response.json()["module"] == "finance"


def test_enterprise_module_workbench(client):
    response = client.get(
        "/admin/enterprise/modules/finance",
        headers=_auth_headers(client),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["module"] == "finance"
    assert "metrics" in body
    assert "actions" in body


def test_live_operational_feed(client):
    response = client.get(
        "/admin/enterprise/live-feed",
        headers=_auth_headers(client),
    )
    assert response.status_code == 200
    assert "data" in response.json()
