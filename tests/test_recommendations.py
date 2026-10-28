from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.app.db.models import Base, Device, Reading
from backend.app.services.recommendations import get_energy_recommendations


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        device = Device(name="Recommendation Test Device", status="online")
        session.add(device)
        session.flush()
        device_id = device.id

        for index in range(20):
            session.add(
                Reading(
                    device_id=device_id,
                    recorded_at=datetime.now(timezone.utc),
                    voltage=230,
                    current=1,
                    power_w=230,
                    energy_kwh=0.001,
                )
            )

        session.commit()
        yield session, device_id

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_recommendations_return_device_and_history(db_session):
    session, device_id = db_session

    result = get_energy_recommendations(session, device_id)

    assert result["device_id"] == device_id
    assert result["readings_analyzed"] == 20
    assert isinstance(result["recommendations"], list)


def test_high_power_generates_present_recommendation(db_session):
    session, device_id = db_session

    session.add(
        Reading(
            device_id=device_id,
            recorded_at=datetime.now(timezone.utc),
            voltage=230,
            current=10,
            power_w=2300,
            energy_kwh=0.01,
        )
    )
    session.commit()

    result = get_energy_recommendations(session, device_id)

    assert any(
        item["time_horizon"] == "present"
        and item["title"] == "High power usage"
        for item in result["recommendations"]
    )


def test_missing_device_data_returns_helpful_message(db_session):
    session, _ = db_session

    result = get_energy_recommendations(session, device_id=999)

    assert result["data_status"] == "insufficient_data"
    assert result["recommendations"]


def test_invalid_device_id_is_rejected(db_session):
    session, _ = db_session

    with pytest.raises(ValueError, match="device_id"):
        get_energy_recommendations(session, device_id=0)
