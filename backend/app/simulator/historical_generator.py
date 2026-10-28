
import argparse
import random
from datetime import datetime, timedelta, timezone

import httpx


def generate_historical_readings(
    device_id: int,
    days: int = 7,
    readings_per_day: int = 24,
) -> list[dict]:
    if device_id <= 0:
        raise ValueError("device_id must be greater than zero")

    if days <= 0 or readings_per_day <= 0:
        raise ValueError("days and readings_per_day must be positive")

    now = datetime.now(timezone.utc)
    readings = []

    for day_offset in range(days - 1, -1, -1):
        day_start = (now - timedelta(days=day_offset)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        for index in range(readings_per_day):
            recorded_at = day_start + timedelta(
                seconds=(index * 86400 / readings_per_day)
            )

            # Skip future timestamps for today's data.
            if recorded_at > now:
                continue

            voltage = round(random.uniform(225, 235), 2)

            # Simulate a daily pattern: lower usage at night,
            # higher usage during morning/evening.
            hour = recorded_at.hour
            if 6 <= hour < 9 or 18 <= hour < 22:
                current = random.uniform(2.0, 5.0)
            else:
                current = random.uniform(0.4, 2.0)

            current = round(current, 2)
            power_w = round(voltage * current, 2)

            # Each sample represents the energy used during its interval.
            interval_seconds = 86400 / readings_per_day
            energy_kwh = round(
                power_w * interval_seconds / 3_600_000,
                8,
            )

            readings.append({
                "device_id": device_id,
                "recorded_at": recorded_at.isoformat(),
                "voltage": voltage,
                "current": current,
                "power_w": power_w,
                "energy_kwh": energy_kwh,
            })

    return readings


def main():
    parser = argparse.ArgumentParser(
        description="Generate historical UrjaSense sample readings."
    )
    parser.add_argument("--device-id", type=int, required=True)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--readings-per-day", type=int, default=24)
    parser.add_argument(
        "--api-url",
        default="http://127.0.0.1:8000/api/v1/readings/",
    )
    args = parser.parse_args()

    try:
        readings = generate_historical_readings(
            device_id=args.device_id,
            days=args.days,
            readings_per_day=args.readings_per_day,
        )
    except ValueError as exc:
        parser.error(str(exc))

    saved_count = 0

    with httpx.Client(timeout=10) as client:
        for reading in readings:
            try:
                response = client.post(args.api_url, json=reading)
                response.raise_for_status()
                saved_count += 1
            except httpx.HTTPError as exc:
                print(f"Failed to save reading: {exc}")

    print(f"Generated readings: {len(readings)}")
    print(f"Successfully saved: {saved_count}")


if __name__ == "__main__":
    main()
