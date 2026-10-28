from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_bill_estimate_success():
    response = client.post(
        "/api/v1/bills/estimate",
        json={
            "consumption_kwh": 100,
            "rate_per_kwh": 5,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "consumption_kwh": 100.0,
        "energy_charge": 500.0,
        "estimated_total": 500.0,
    }


def test_bill_estimate_zero_consumption():
    response = client.post(
        "/api/v1/bills/estimate",
        json={
            "consumption_kwh": 0,
            "rate_per_kwh": 5,
        },
    )

    assert response.status_code == 200
    assert response.json()["estimated_total"] == 0


def test_bill_estimate_rejects_negative_consumption():
    response = client.post(
        "/api/v1/bills/estimate",
        json={
            "consumption_kwh": -10,
            "rate_per_kwh": 5,
        },
    )

    assert response.status_code == 422


def test_bill_estimate_rejects_negative_rate():
    response = client.post(
        "/api/v1/bills/estimate",
        json={
            "consumption_kwh": 100,
            "rate_per_kwh": -5,
        },
    )

    assert response.status_code == 422
