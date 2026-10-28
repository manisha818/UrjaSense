import random
from datetime import datetime, timezone


def generate_reading(
    device_id: int,
    scenario: str = "normal",
    duration_seconds: float = 5.0,
) -> dict:
    """Generate one simulated electricity reading."""

    if device_id <= 0:
        raise ValueError("device_id must be greater than zero")

    if scenario not in {"normal", "high_consumption"}:
        raise ValueError(
            "scenario must be 'normal' or 'high_consumption'"
        )

    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be greater than zero")

    voltage = round(random.uniform(225, 235), 2)

    if scenario == "normal":
        current = round(random.uniform(0.5, 3.0), 2)
    else:
        current = round(random.uniform(5.0, 10.0), 2)

    power_w = round(voltage * current, 2)

    energy_kwh = round(
        power_w * duration_seconds / 3_600_000,
        8,
    )

    return {
        "device_id": device_id,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "voltage": voltage,
        "current": current,
        "power_w": power_w,
        "energy_kwh": energy_kwh,
    }
