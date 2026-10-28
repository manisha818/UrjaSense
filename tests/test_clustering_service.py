
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db.models import Device, Reading
from backend.app.db.session import Base
from backend.app.services.clustering_service import get_usage_patterns


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        db.add(Device(id=1, name="Test Device", status="online"))
        db.commit()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def add_daily_readings(db, day_offset, energy, power):
    day = datetime.now(timezone.utc).date() - timedelta(
        days=day_offset
    )
    recorded_at = datetime(
        day.year,
        day.month,
        day.day,
        12,
        tzinfo=timezone.utc,
    )

    db.add(
        Reading(
            device_id=1,
            recorded_at=recorded_at,
            voltage=230.0,
            current=power / 230.0,
            power_w=power,
            energy_kwh=energy,
        )
    )


def test_insufficient_data_returns_clear_status(db_session):
    add_daily_readings(db_session, 1, 2.0, 200.0)
    add_daily_readings(db_session, 2, 3.0, 250.0)
    db_session.commit()

    result = get_usage_patterns(db_session, device_id=1)

    assert result["status"] == "insufficient_data"
    assert result["days_available"] == 2
    assert result["clusters"] == []


def test_invalid_device_id_is_rejected(db_session):
    with pytest.raises(
        ValueError,
        match="device_id must be greater than zero",
    ):
        get_usage_patterns(db_session, device_id=0)


def test_usage_patterns_are_generated(db_session):
    daily_values = [
        (1, 1.0, 100.0),
        (2, 1.2, 110.0),
        (3, 1.1, 105.0),
        (4, 5.0, 500.0),
        (5, 5.5, 550.0),
        (6, 5.2, 520.0),
    ]

    for offset, energy, power in daily_values:
        add_daily_readings(
            db_session,
            offset,
            energy,
            power,
        )

    db_session.commit()

    result = get_usage_patterns(db_session, device_id=1)

    assert result["status"] == "success"
    assert result["days_available"] == 6
    assert len(result["clusters"]) >= 2
    assert len(result["daily_patterns"]) == 6

    patterns = {
        item["usage_pattern"]
        for item in result["daily_patterns"]
    }
    assert "Low" in patterns
    assert "High" in patterns

    for item in result["clusters"]:
        assert item["days_count"] > 0
        assert item["average_daily_consumption_kwh"] >= 0


def test_identical_usage_returns_insufficient_variation(db_session):
    for offset in range(1, 6):
        add_daily_readings(
            db_session,
            offset,
            2.0,
            200.0,
        )

    db_session.commit()

    result = get_usage_patterns(db_session, device_id=1)

    assert result["status"] == "insufficient_variation"
    assert result["clusters"] == []
