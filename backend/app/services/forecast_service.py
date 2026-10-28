
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.models import EnergyForecast
from backend.app.services.aggregation import get_daily_consumption


def forecast_next_day_consumption(
    db: Session,
    device_id: int,
    min_days: int = 3,
) -> dict:
    """
    Forecast next-day energy consumption using the average
    of recent completed daily consumption totals.

    Save successful forecasts for later accuracy tracking.
    """

    if device_id <= 0:
        raise ValueError("device_id must be greater than zero")

    if min_days < 2:
        raise ValueError("min_days must be at least 2")

    daily_data = get_daily_consumption(
        db=db,
        device_id=device_id,
    )

    today = date.today().isoformat()

    completed_days = [
        day
        for day in daily_data
        if day["date"] < today
    ]

    if len(completed_days) < min_days:
        return {
            "device_id": device_id,
            "forecast_date": None,
            "predicted_consumption_kwh": None,
            "days_used": len(completed_days),
            "method": "recent_daily_average",
            "status": "insufficient_data",
            "message": (
                f"At least {min_days} completed days of consumption "
                "data are required for forecasting. Today's data "
                "is excluded."
            ),
        }

    recent_days = completed_days[-7:]

    average_consumption = sum(
        day["total_consumption_kwh"]
        for day in recent_days
    ) / len(recent_days)

    predicted_consumption = round(
        max(0.0, average_consumption),
        3,
    )
    forecast_date = date.today() + timedelta(days=1)

    try:
        statement = select(EnergyForecast).where(
            EnergyForecast.device_id == device_id,
            EnergyForecast.forecast_date == forecast_date,
        )
        forecast_record = db.scalar(statement)

        if forecast_record is None:
            forecast_record = EnergyForecast(
                device_id=device_id,
                forecast_date=forecast_date,
                predicted_consumption_kwh=predicted_consumption,
            )
            db.add(forecast_record)
        else:
            forecast_record.predicted_consumption_kwh = (
                predicted_consumption
            )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "device_id": device_id,
        "forecast_date": forecast_date.isoformat(),
        "predicted_consumption_kwh": predicted_consumption,
        "days_used": len(recent_days),
        "method": "recent_daily_average",
        "status": "success",
        "message": (
            "Forecast is based on the average of recent completed "
            "daily consumption totals. It is an estimate, not a "
            "guaranteed prediction."
        ),
    }

def get_forecast_accuracy(
    db: Session,
    device_id: int,
) -> dict:
    """
    Compare saved forecasts with actual daily consumption
    for completed dates and calculate Mean Absolute Error (MAE).
    """

    if device_id <= 0:
        raise ValueError("device_id must be greater than zero")

    statement = (
        select(EnergyForecast)
        .where(EnergyForecast.device_id == device_id)
        .order_by(EnergyForecast.forecast_date)
    )

    forecasts = db.scalars(statement).all()

    today = date.today()
    daily_data = get_daily_consumption(
        db=db,
        device_id=device_id,
    )

    actual_by_date = {
        item["date"]: item["total_consumption_kwh"]
        for item in daily_data
        if item["date"] < today.isoformat()
    }

    comparisons = []

    for forecast in forecasts:
        forecast_date = forecast.forecast_date

        if forecast_date >= today:
            continue

        actual = actual_by_date.get(forecast_date.isoformat())

        if actual is None:
            continue

        predicted = forecast.predicted_consumption_kwh
        absolute_error = abs(predicted - actual)

        comparisons.append(
            {
                "date": forecast_date.isoformat(),
                "predicted_consumption_kwh": round(predicted, 3),
                "actual_consumption_kwh": round(actual, 3),
                "absolute_error_kwh": round(absolute_error, 3),
            }
        )

    if not comparisons:
        return {
            "device_id": device_id,
            "status": "insufficient_data",
            "matched_days": 0,
            "mae_kwh": None,
            "comparisons": [],
            "message": (
                "No completed forecast dates have matching actual "
                "consumption data yet."
            ),
        }

    mae = sum(
        item["absolute_error_kwh"]
        for item in comparisons
    ) / len(comparisons)

    return {
        "device_id": device_id,
        "status": "success",
        "matched_days": len(comparisons),
        "mae_kwh": round(mae, 3),
        "comparisons": comparisons,
        "message": (
            "MAE measures the average absolute difference between "
            "predicted and recorded daily consumption. Lower is better."
        ),
    }

