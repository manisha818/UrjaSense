from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.app.db.models import Base, Device, Reading
from backend.app.services.anomaly_service import (
    detect_reading,
    get_training_readings,
    train_detector,
)


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        device = Device(name="ML Test Device", status="online")
        session.add(device)
        session.flush()
        device_id = device.id

        for index in range(20):
            voltage = 230.0 + (index % 3)
            current = 1.0 + (index % 4) * 0.1

            session.add(
                Reading(
                    device_id=device_id,
                    recorded_at=datetime.now(timezone.utc),
                    voltage=voltage,
                    current=current,
                    power_w=round(voltage * current, 2),
                    energy_kwh=0.001,
                )
            )

        session.commit()
        yield session, device_id

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_get_training_readings_from_database(db_session):
    session, device_id = db_session

    readings = get_training_readings(session, device_id=device_id)

    assert len(readings) == 20
    assert set(readings[0]) == {"voltage", "current", "power_w"}


def test_train_detector_from_database(db_session):
    session, device_id = db_session

    detector = train_detector(session, device_id=device_id)

    result = detect_reading(
        detector,
        {"voltage": 231, "current": 1.1, "power_w": 254.1},
    )

    assert result["label"] in (-1, 1)
    assert isinstance(result["is_anomaly"], bool)
    assert isinstance(result["anomaly_score"], float)


def test_training_fails_with_too_few_readings(db_session):
    session, device_id = db_session

    session.query(Reading).filter(
        Reading.device_id == device_id
    ).delete()
    session.commit()

    with pytest.raises(ValueError, match="At least 5"):
        train_detector(session, device_id=device_id)


def test_device_filter_returns_only_selected_device(db_session):
    session, first_device_id = db_session

    second_device = Device(name="Another Device", status="online")
    session.add(second_device)
    session.flush()

    session.add(
        Reading(
            device_id=second_device.id,
            voltage=230,
            current=2,
            power_w=460,
            energy_kwh=0.001,
        )
    )
    session.commit()

    readings = get_training_readings(
        session,
        device_id=first_device_id,
    )

    assert len(readings) == 20
