import argparse
import os

import httpx

from backend.app.simulator.generator import generate_reading


def main():
    parser = argparse.ArgumentParser(
        description="Send simulated electricity readings to UrjaSense."
    )
    parser.add_argument("--device-id", type=int, required=True)
    parser.add_argument(
        "--scenario",
        choices=["normal", "high_consumption"],
        default="normal",
    )
    args = parser.parse_args()

    api_url = os.getenv(
        "URJASENSE_API_URL",
        "http://127.0.0.1:8000/api/v1/readings/",
    )

    reading = generate_reading(
        device_id=args.device_id,
        scenario=args.scenario,
    )

    try:
        response = httpx.post(api_url, json=reading, timeout=10)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print(f"API returned HTTP {exc.response.status_code}:")
        print(exc.response.text)
        raise SystemExit(1) from exc
    except httpx.HTTPError as exc:
        print(f"Could not connect to UrjaSense API: {exc}")
        print("Check that the FastAPI server is running.")
        raise SystemExit(1) from exc

    print("Reading saved successfully!")
    print(response.json())


if __name__ == "__main__":
    main()
