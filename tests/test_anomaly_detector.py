import pytest

from backend.app.ml.anomaly_detector import ElectricityAnomalyDetector


@pytest.fixture
def normal_readings():
    return [
        {"voltage": 230, "current": 1.0, "power_w": 230},
        {"voltage": 231, "current": 1.1, "power_w": 254},
        {"voltage": 229, "current": 0.9, "power_w": 206},
        {"voltage": 230, "current": 1.2, "power_w": 276},
        {"voltage": 232, "current": 1.0, "power_w": 232},
        {"voltage": 228, "current": 1.1, "power_w": 251},
        {"voltage": 230, "current": 0.8, "power_w": 184},
        {"voltage": 231, "current": 1.2, "power_w": 277},
        {"voltage": 229, "current": 1.0, "power_w": 229},
        {"voltage": 230, "current": 1.1, "power_w": 253},
        {"voltage": 232, "current": 0.9, "power_w": 209},
        {"voltage": 228, "current": 1.0, "power_w": 228},
        {"voltage": 230, "current": 1.2, "power_w": 276},
        {"voltage": 231, "current": 0.9, "power_w": 208},
        {"voltage": 229, "current": 1.1, "power_w": 252},
        {"voltage": 230, "current": 1.0, "power_w": 230},
        {"voltage": 232, "current": 1.1, "power_w": 255},
        {"voltage": 228, "current": 0.9, "power_w": 205},
        {"voltage": 231, "current": 1.0, "power_w": 231},
        {"voltage": 230, "current": 1.1, "power_w": 253},
    ]


def test_model_can_be_trained(normal_readings):
    detector = ElectricityAnomalyDetector()
    result = detector.fit(normal_readings)

    assert result is detector


def test_prediction_returns_valid_result(normal_readings):
    detector = ElectricityAnomalyDetector()
    detector.fit(normal_readings)

    result = detector.predict(
        {"voltage": 230, "current": 1.0, "power_w": 230}
    )

    assert result.label in (-1, 1)
    assert result.is_anomaly == (result.label == -1)
    assert isinstance(result.anomaly_score, float)


def test_model_can_flag_extreme_reading(normal_readings):
    detector = ElectricityAnomalyDetector(contamination=0.05)
    detector.fit(normal_readings)

    result = detector.predict(
        {"voltage": 230, "current": 50.0, "power_w": 11500.0}
    )

    assert result.is_anomaly is True


def test_prediction_before_training_fails():
    detector = ElectricityAnomalyDetector()

    with pytest.raises(RuntimeError, match="not fitted"):
        detector.predict(
            {"voltage": 230, "current": 1.0, "power_w": 230}
        )


def test_training_requires_at_least_five_readings():
    detector = ElectricityAnomalyDetector()

    with pytest.raises(ValueError, match="At least 5"):
        detector.fit([
            {"voltage": 230, "current": 1.0, "power_w": 230}
        ])


def test_invalid_contamination_is_rejected():
    with pytest.raises(ValueError, match="contamination"):
        ElectricityAnomalyDetector(contamination=0)


def test_negative_measurement_is_rejected():
    detector = ElectricityAnomalyDetector()

    readings = [
        {"voltage": 230, "current": 1.0, "power_w": 230},
        {"voltage": 231, "current": 1.1, "power_w": 254},
        {"voltage": 229, "current": 0.9, "power_w": 206},
        {"voltage": 230, "current": 1.2, "power_w": 276},
        {"voltage": 232, "current": 1.0, "power_w": 232},
    ]
    readings[0]["current"] = -1

    with pytest.raises(ValueError, match="cannot be negative"):
        detector.fit(readings)
