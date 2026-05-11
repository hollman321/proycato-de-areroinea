"""
Fixtures compartidas: BD de prueba y usuario admin para JWT.

`autouse` asegura tablas y admin antes de importar escenarios que llaman a la API.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-only")

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://admin:secretpassword@db:5432/skyanalytics_test",
)
# `database.py` lee DATABASE_URL al importar; alinear con la BD de pruebas.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from models import Base, User  # noqa: E402
from database import get_db  # noqa: E402
from core.security import get_password_hash  # noqa: E402
from main import app  # noqa: E402

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def _setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        if db.query(User).filter(User.email == "admin@skyanalytics.com").first() is None:
            db.add(
                User(
                    email="admin@skyanalytics.com",
                    hashed_password=get_password_hash("admin123"),
                    full_name="Admin Test",
                    role="admin",
                    is_active=True,
                )
            )
            db.commit()
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)
