import argparse
import time

import httpx

from backend.app.simulator.generator import generate_reading


def main():
    parser = argparse.ArgumentParser(
        description="Continuously simulate UrjaSense electricity readings."
    )
    parser.add_argument("--device-id", type=int, required=True)
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Seconds between readings (default: 5).",
    )
    parser.add_argument(
        "--scenario",
        choices=["normal", "high_consumption", "mixed"],
        default="mixed",
    )
    args = parser.parse_args()

    if args.device_id <= 0:
        parser.error("--device-id must be greater than zero")

    if args.interval <= 0:
        parser.error("--interval must be greater than zero")

    api_url = "http://127.0.0.1:8000/api/v1/readings/"
    count = 0

    print("UrjaSense continuous simulator started.")
    print(f"Device ID: {args.device_id}")
    print(f"Interval: {args.interval} seconds")
    print("Press Ctrl+C to stop.")

    try:
        with httpx.Client(timeout=10) as client:
            while True:
                scenario = args.scenario

                if scenario == "mixed":
                    # Generate a high-consumption sample every fifth reading.
                    scenario = (
                        "high_consumption"
                        if (count + 1) % 5 == 0
                        else "normal"
                    )

                reading = generate_reading(
                    device_id=args.device_id,
                    scenario=scenario,
                    duration_seconds=args.interval,
                )

                try:
                    response = client.post(api_url, json=reading)
                    response.raise_for_status()
                    saved = response.json()
                    count += 1

                    print(
                        f"Saved reading #{count} | "
                        f"ID={saved['id']} | "
                        f"Power={saved['power_w']} W | "
                        f"Energy={saved['energy_kwh']} kWh | "
                        f"Scenario={scenario}"
                    )
                except httpx.HTTPError as exc:
                    print(f"Could not save reading: {exc}")

                time.sleep(args.interval)

    except KeyboardInterrupt:
        print(f"\nSimulator stopped. Readings saved this run: {count}")


if __name__ == "__main__":
    main()

