
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.db.models import Device, Reading
from backend.app.db.session import Base
from backend.app.api.v1.readings import get_db
from backend.app.api.v1.clustering import get_db as clustering_get_db


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[clustering_get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            db = TestSessionLocal()
            db.add(Device(id=1, name="Clustering Test Device"))
            db.commit()
            db.close()

            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_clustering_endpoint_rejects_invalid_device_id(client):
    response = client.get(
        "/api/v1/clustering/usage-patterns/0"
    )

    assert response.status_code == 422


def test_clustering_endpoint_returns_insufficient_data(client):
    response = client.get(
        "/api/v1/clustering/usage-patterns/1"
    )

    assert response.status_code == 200

    data = response.json()
    assert data["device_id"] == 1
    assert data["status"] == "insufficient_data"
    assert data["days_available"] == 0
    assert data["clusters"] == []


def test_clustering_endpoint_generates_usage_patterns(client):
    from datetime import datetime, timedelta, timezone

    from backend.app.db.session import SessionLocal

    # Use the same database engine as the test client.
    # Obtain the test DB through the overridden dependency instead.
    override = app.dependency_overrides[get_db]
    db = next(override())

    try:
        for offset, energy, power in [
            (1, 1.0, 100.0),
            (2, 1.2, 110.0),
            (3, 1.1, 105.0),
            (4, 5.0, 500.0),
            (5, 5.5, 550.0),
            (6, 5.2, 520.0),
        ]:
            day = datetime.now(timezone.utc).date() - timedelta(
                days=offset
            )
            db.add(
                Reading(
                    device_id=1,
                    recorded_at=datetime(
                        day.year,
                        day.month,
                        day.day,
                        12,
                        tzinfo=timezone.utc,
                    ),
                    voltage=230.0,
                    current=power / 230.0,
                    power_w=power,
                    energy_kwh=energy,
                )
            )

        db.commit()
    finally:
        db.close()

    response = client.get(
        "/api/v1/clustering/usage-patterns/1"
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert data["days_available"] == 6
    assert len(data["clusters"]) >= 2
    assert len(data["daily_patterns"]) == 6
