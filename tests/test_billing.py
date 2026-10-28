
import pytest

from backend.app.services.billing import estimate_bill


def test_estimate_bill():
    result = estimate_bill(
        consumption_kwh=100,
        rate_per_kwh=5,
    )

    assert result.consumption_kwh == 100
    assert result.energy_charge == 500
    assert result.estimated_total == 500


def test_zero_consumption():
    result = estimate_bill(
        consumption_kwh=0,
        rate_per_kwh=5,
    )

    assert result.energy_charge == 0
    assert result.estimated_total == 0


def test_negative_consumption_is_rejected():
    with pytest.raises(ValueError):
        estimate_bill(
            consumption_kwh=-10,
            rate_per_kwh=5,
        )


def test_negative_rate_is_rejected():
    with pytest.raises(ValueError):
        estimate_bill(
            consumption_kwh=100,
            rate_per_kwh=-5,
        )
