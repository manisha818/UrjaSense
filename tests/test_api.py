
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.db.session import Base
from backend.app.db import models
from backend.app.api.v1 import devices, readings


@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[devices.get_db] = override_get_db
    app.dependency_overrides[readings.get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


def test_health_endpoint(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_device(client):
    response = client.post(
        "/api/v1/devices/",
        json={"name": "Automated Test Device"},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Automated Test Device"
    assert response.json()["status"] == "offline"


def test_create_reading_for_unknown_device(client):
    response = client.post(
        "/api/v1/readings/",
        json={
            "device_id": 999999,
            "voltage": 230,
            "current": 2.5,
            "power_w": 575,
            "energy_kwh": 0.25,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Device not found"


def test_reading_rejects_negative_energy(client):
    response = client.post(
        "/api/v1/readings/",
        json={
            "device_id": 7,
            "voltage": 230,
            "current": 2.5,
            "power_w": 575,
            "energy_kwh": -1,
        },
    )

    assert response.status_code == 422
    

def test_daily_consumption_endpoint(client):
    response = client.get("/api/v1/consumption/daily/1")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    if data:
        assert "date" in data[0]
        assert "total_consumption_kwh" in data[0]
        assert "reading_count" in data[0]
        
def test_consumption_trends_endpoint(client):
    response = client.get("/api/v1/consumption/trends/1")

    assert response.status_code == 200

    data = response.json()

    assert data["device_id"] == 1
    assert data["trend"] in {
        "increasing",
        "decreasing",
        "stable",
        "insufficient_data",
        "no_data",
    }
    assert isinstance(data["daily_data"], list)
    assert "message" in data


