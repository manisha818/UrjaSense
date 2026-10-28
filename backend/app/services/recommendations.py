from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.models import Reading


def get_energy_recommendations(
    db: Session,
    device_id: int,
) -> dict:
    """Generate basic recommendations from current and historical readings."""

    if device_id <= 0:
        raise ValueError("device_id must be greater than zero")

    statement = (
        select(Reading)
        .where(
            Reading.device_id == device_id,
            Reading.power_w.is_not(None),
            Reading.energy_kwh >= 0,
        )
        .order_by(Reading.recorded_at.desc(), Reading.id.desc())
        .limit(31)
    )

    readings = db.scalars(statement).all()

    if not readings:
        return {
            "device_id": device_id,
            "data_status": "insufficient_data",
            "recommendations": [
                {
                    "time_horizon": "present",
                    "priority": "info",
                    "title": "No consumption data available",
                    "message": (
                        "Add valid electricity readings before generating "
                        "personalized recommendations."
                    ),
                }
            ],
        }

    latest = readings[0]
    historical = readings[1:]
    recommendations = []

    # Present: flag unusually high power using a conservative,
    # fixed screening threshold. This is not a device safety limit.
    if latest.power_w is not None and latest.power_w > 2000:
        recommendations.append({
            "time_horizon": "present",
            "priority": "high",
            "title": "High power usage",
            "message": (
                "Power usage is above 2000 W. Check which appliances "
                "are operating and compare with their rated power."
            ),
        })

    # Past: compare the latest reading with the median of previous readings.
    past_powers = [
        float(item.power_w)
        for item in historical
        if item.power_w is not None and item.power_w >= 0
    ]

    if len(past_powers) >= 5 and latest.power_w is not None:
        sorted_powers = sorted(past_powers)
        middle = len(sorted_powers) // 2

        if len(sorted_powers) % 2:
            median_power = sorted_powers[middle]
        else:
            median_power = (
                sorted_powers[middle - 1] + sorted_powers[middle]
            ) / 2

        if median_power > 0 and latest.power_w > median_power * 1.5:
            recommendations.append({
                "time_horizon": "past",
                "priority": "medium",
                "title": "Usage above historical baseline",
                "message": (
                    "The latest power reading is more than 50% above "
                    "the median of previous readings. Check the active "
                    "appliances and monitor whether this pattern repeats."
                ),
            })

    # Future: only provide a cautious trend warning when sufficient data
    # exists. This is not a trained forecast or a bill prediction.
    if len(readings) >= 20:
        recent = readings[:10]
        older = readings[10:20]

        recent_values = [
            float(item.power_w)
            for item in recent
            if item.power_w is not None and item.power_w >= 0
        ]
        older_values = [
            float(item.power_w)
            for item in older
            if item.power_w is not None and item.power_w >= 0
        ]

        if recent_values and older_values:
            recent_average = sum(recent_values) / len(recent_values)
            older_average = sum(older_values) / len(older_values)

            if older_average > 0 and recent_average > older_average * 1.2:
                recommendations.append({
                    "time_horizon": "future",
                    "priority": "medium",
                    "title": "Rising usage trend",
                    "message": (
                        "Recent readings average more than 20% above "
                        "the preceding group. If this trend continues, "
                        "consumption may increase. Collect readings over "
                        "consistent time intervals before forecasting."
                    ),
                })

    if not recommendations:
        recommendations.append({
            "time_horizon": "present",
            "priority": "info",
            "title": "Continue monitoring",
            "message": (
                "No recommendation rule was triggered. Keep collecting "
                "readings to improve historical analysis."
            ),
        })

    return {
        "device_id": device_id,
        "data_status": (
            "limited_history" if len(readings) < 20 else "history_available"
        ),
        "readings_analyzed": len(readings),
        "latest_power_w": latest.power_w,
        "recommendations": recommendations,
    }
