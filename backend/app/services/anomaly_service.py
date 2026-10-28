from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.models import Reading
from backend.app.ml.anomaly_detector import ElectricityAnomalyDetector


FEATURE_COLUMNS = ("voltage", "current", "power_w")


def get_training_readings(
    db: Session,
    device_id: int | None = None,
) -> list[dict]:
    """Fetch historical readings that have all required ML features."""

    statement = select(Reading).where(
        Reading.voltage.is_not(None),
        Reading.current.is_not(None),
        Reading.power_w.is_not(None),
    )

    if device_id is not None:
        statement = statement.where(Reading.device_id == device_id)

    statement = statement.order_by(Reading.recorded_at.asc())
    readings = db.scalars(statement).all()

    result = []

    for reading in readings:
        values = {
            "voltage": reading.voltage,
            "current": reading.current,
            "power_w": reading.power_w,
        }

        # Skip invalid historical records rather than training on bad data.
        if any(value is None for value in values.values()):
            continue

        result.append(values)

    return result


def train_detector(
    db: Session,
    device_id: int | None = None,
    contamination: float = 0.05,
) -> ElectricityAnomalyDetector:
    """Train a detector using historical database readings."""

    readings = get_training_readings(db, device_id=device_id)

    if len(readings) < 5:
        raise ValueError(
            "At least 5 valid historical readings are required to train."
        )

    detector = ElectricityAnomalyDetector(
        contamination=contamination,
    )
    detector.fit(readings)

    return detector


def detect_reading(
    detector: ElectricityAnomalyDetector,
    reading: dict,
) -> dict:
    """Return a JSON-friendly anomaly result for one reading."""

    result = detector.predict(reading)

    return {
        "is_anomaly": result.is_anomaly,
        "label": result.label,
        "anomaly_score": result.anomaly_score,
    }
