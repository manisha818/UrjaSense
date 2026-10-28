
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

from backend.app.services.forecast_service import (
    forecast_next_day_consumption,
)


def make_daily_data(number_of_days: int) -> list[dict]:
    today = date.today()

    return [
        {
            "date": (
                today - timedelta(days=number_of_days - i)
            ).isoformat(),
            "total_consumption_kwh": float(10 + i),
            "reading_count": 24,
        }
        for i in range(number_of_days)
    ]


def make_mock_db(existing_forecast=None):
    db = MagicMock()
    db.scalar.return_value = existing_forecast
    return db


def test_forecast_returns_insufficient_data():
    db = make_mock_db()

    with patch(
        "backend.app.services.forecast_service.get_daily_consumption",
        return_value=make_daily_data(2),
    ):
        result = forecast_next_day_consumption(
            db=db,
            device_id=1,
        )

    assert result["status"] == "insufficient_data"
    assert result["predicted_consumption_kwh"] is None
    assert result["days_used"] == 2
    db.commit.assert_not_called()


def test_forecast_calculates_average_and_saves_record():
    db = make_mock_db()

    with patch(
        "backend.app.services.forecast_service.get_daily_consumption",
        return_value=make_daily_data(3),
    ):
        result = forecast_next_day_consumption(
            db=db,
            device_id=1,
        )

    assert result["status"] == "success"
    assert result["predicted_consumption_kwh"] == 11.0
    assert result["days_used"] == 3
    assert result["forecast_date"] == (
        date.today() + timedelta(days=1)
    ).isoformat()

    saved_record = db.add.call_args.args[0]
    assert saved_record.device_id == 1
    assert saved_record.forecast_date == date.today() + timedelta(days=1)
    assert saved_record.predicted_consumption_kwh == 11.0
    db.commit.assert_called_once()


def test_forecast_updates_existing_record():
    existing_forecast = MagicMock()
    db = make_mock_db(existing_forecast)

    with patch(
        "backend.app.services.forecast_service.get_daily_consumption",
        return_value=make_daily_data(3),
    ):
        result = forecast_next_day_consumption(
            db=db,
            device_id=1,
        )

    assert result["status"] == "success"
    assert existing_forecast.predicted_consumption_kwh == 11.0
    db.add.assert_not_called()
    db.commit.assert_called_once()


def test_forecast_excludes_today():
    db = make_mock_db()
    data = make_daily_data(3)
    data.append(
        {
            "date": date.today().isoformat(),
            "total_consumption_kwh": 999.0,
            "reading_count": 1,
        }
    )

    with patch(
        "backend.app.services.forecast_service.get_daily_consumption",
        return_value=data,
    ):
        result = forecast_next_day_consumption(
            db=db,
            device_id=1,
        )

    assert result["status"] == "success"
    assert result["predicted_consumption_kwh"] == 11.0
    assert result["days_used"] == 3


@pytest.mark.parametrize(
    ("device_id", "min_days"),
    [
        (0, 3),
        (-1, 3),
        (1, 1),
        (1, 0),
    ],
)
def test_forecast_rejects_invalid_arguments(device_id, min_days):
    with pytest.raises(ValueError):
        forecast_next_day_consumption(
            db=None,
            device_id=device_id,
            min_days=min_days,
        )

def test_forecast_accuracy_calculates_mae():
    from datetime import date, timedelta
    from types import SimpleNamespace

    from backend.app.services.forecast_service import (
        get_forecast_accuracy,
    )

    yesterday = date.today() - timedelta(days=1)

    forecast = SimpleNamespace(
        device_id=1,
        forecast_date=yesterday,
        predicted_consumption_kwh=12.0,
    )

    db = MagicMock()
    db.scalars.return_value.all.return_value = [forecast]

    with patch(
        "backend.app.services.forecast_service.get_daily_consumption",
        return_value=[
            {
                "date": yesterday.isoformat(),
                "total_consumption_kwh": 10.0,
                "reading_count": 24,
            }
        ],
    ):
        result = get_forecast_accuracy(db=db, device_id=1)

    assert result["status"] == "success"
    assert result["matched_days"] == 1
    assert result["mae_kwh"] == 2.0
    assert result["comparisons"][0]["absolute_error_kwh"] == 2.0


def test_forecast_accuracy_returns_insufficient_data():
    from backend.app.services.forecast_service import (
        get_forecast_accuracy,
    )

    db = MagicMock()
    db.scalars.return_value.all.return_value = []

    with patch(
        "backend.app.services.forecast_service.get_daily_consumption",
        return_value=[],
    ):
        result = get_forecast_accuracy(db=db, device_id=1)

    assert result["status"] == "insufficient_data"
    assert result["matched_days"] == 0
    assert result["mae_kwh"] is None
    assert result["comparisons"] == []


def test_forecast_accuracy_rejects_invalid_device_id():
    from backend.app.services.forecast_service import (
        get_forecast_accuracy,
    )

    with pytest.raises(ValueError):
        get_forecast_accuracy(db=None, device_id=0)

