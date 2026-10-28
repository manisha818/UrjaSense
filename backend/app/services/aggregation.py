from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.models import Reading


def get_consumption_summary(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    device_id: int | None = None,
) -> dict:
    statement = select(
        func.coalesce(func.sum(Reading.energy_kwh), 0.0),
        func.count(Reading.id),
    )

    if start_date is not None:
        statement = statement.where(
            Reading.recorded_at >= start_date
        )

    if end_date is not None:
        statement = statement.where(
            Reading.recorded_at <= end_date
        )

    if device_id is not None:
        statement = statement.where(
            Reading.device_id == device_id
        )

    result = db.execute(statement).one()

    return {
        "total_consumption_kwh": float(result[0]),
        "reading_count": result[1],
    }


def get_consumption_analytics(
    db: Session,
    device_id: int,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict:
    if device_id <= 0:
        raise ValueError("device_id must be greater than zero")

    statement = select(
        func.coalesce(func.sum(Reading.energy_kwh), 0.0),
        func.count(Reading.id),
        func.avg(Reading.power_w),
        func.min(Reading.power_w),
        func.max(Reading.power_w),
        func.max(Reading.recorded_at),
    ).where(Reading.device_id == device_id)

    if start_date is not None:
        statement = statement.where(
            Reading.recorded_at >= start_date
        )

    if end_date is not None:
        statement = statement.where(
            Reading.recorded_at <= end_date
        )

    result = db.execute(statement).one()

    total_energy = float(result[0] or 0.0)
    reading_count = int(result[1] or 0)

    return {
        "device_id": device_id,
        "total_consumption_kwh": round(total_energy, 6),
        "reading_count": reading_count,
        "average_energy_per_reading_kwh": (
            round(total_energy / reading_count, 8)
            if reading_count else 0.0
        ),
        "average_power_w": (
            round(float(result[2]), 2)
            if result[2] is not None else None
        ),
        "minimum_power_w": (
            round(float(result[3]), 2)
            if result[3] is not None else None
        ),
        "maximum_power_w": (
            round(float(result[4]), 2)
            if result[4] is not None else None
        ),
        "latest_reading_at": (
            result[5].isoformat()
            if result[5] is not None else None
        ),
    }



def get_daily_consumption(
    db: Session,
    device_id: int,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[dict]:
    statement = select(
        func.date(Reading.recorded_at).label("date"),
        func.coalesce(func.sum(Reading.energy_kwh), 0.0).label(
            "total_consumption_kwh"
        ),
        func.count(Reading.id).label("reading_count"),
    ).where(Reading.device_id == device_id)

    if start_date is not None:
        statement = statement.where(
            Reading.recorded_at >= start_date
        )

    if end_date is not None:
        statement = statement.where(
            Reading.recorded_at <= end_date
        )

    statement = statement.group_by(
        func.date(Reading.recorded_at)
    ).order_by(
        func.date(Reading.recorded_at)
    )

    results = db.execute(statement).all()

    return [
        {
            "date": str(row.date),
            "total_consumption_kwh": round(float(row.total_consumption_kwh), 6),
            "reading_count": int(row.reading_count),
        }
        for row in results
    ]

def get_consumption_trend(
    db: Session,
    device_id: int,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict:
    daily_data = get_daily_consumption(
        db=db,
        device_id=device_id,
        start_date=start_date,
        end_date=end_date,
    )

    if not daily_data:
        return {
            "device_id": device_id,
            "trend": "no_data",
            "daily_data": [],
            "message": "No consumption data available for this device.",
        }

    # Exclude today's incomplete data from trend calculation.
    today = datetime.now().date().isoformat()
    completed_days = [
        day for day in daily_data
        if day["date"] < today
    ]

    if len(completed_days) < 2:
        trend = "insufficient_data"
        message = (
            "At least two completed days are required to calculate "
            "the consumption trend. Today's data is excluded."
        )
    else:
        first_day = completed_days[0]["total_consumption_kwh"]
        last_day = completed_days[-1]["total_consumption_kwh"]

        if last_day > first_day:
            trend = "increasing"
        elif last_day < first_day:
            trend = "decreasing"
        else:
            trend = "stable"

        message = (
            "Trend is based on the first and last available completed "
            "daily totals. Today's data is excluded."
        )

    return {
        "device_id": device_id,
        "trend": trend,
        "daily_data": daily_data,
        "message": message,
    }


