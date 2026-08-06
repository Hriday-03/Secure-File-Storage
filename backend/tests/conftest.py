"""Shared fixtures for API tests: isolated database, storage, and client."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base, get_db
from app.main import app
from app.middleware.rate_limit_middleware import _AUTH_LIMITER, _GENERAL_LIMITER
from app.services.storage_service import StorageService


@pytest.fixture()
def db_engine(tmp_path):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session_factory(db_engine):
    return sessionmaker(bind=db_engine, autocommit=False, autoflush=False)


@pytest.fixture()
def client(db_session_factory, tmp_path, monkeypatch):
    test_storage = StorageService(tmp_path / "storage")
    monkeypatch.setattr("app.services.file_service.storage", test_storage)
    monkeypatch.setattr("app.api.files.storage", test_storage)

    def override_get_db():
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        _AUTH_LIMITER.clear("testclient")
        _GENERAL_LIMITER.clear("testclient")
        yield test_client

    app.dependency_overrides.clear()
    _AUTH_LIMITER.clear("testclient")
    _GENERAL_LIMITER.clear("testclient")


@pytest.fixture()
def auth_headers(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Test User", "email": "test@example.com", "password": "securepass123"},
    )
    assert response.status_code == 201
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
