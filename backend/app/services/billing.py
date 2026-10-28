
from dataclasses import dataclass


@dataclass(frozen=True)
class BillingEstimate:
    consumption_kwh: float
    energy_charge: float
    estimated_total: float


def estimate_bill(
    consumption_kwh: float,
    rate_per_kwh: float,
) -> BillingEstimate:
    if consumption_kwh < 0:
        raise ValueError("Consumption cannot be negative")

    if rate_per_kwh < 0:
        raise ValueError("Rate cannot be negative")

    energy_charge = consumption_kwh * rate_per_kwh

    return BillingEstimate(
        consumption_kwh=round(consumption_kwh, 3),
        energy_charge=round(energy_charge, 2),
        estimated_total=round(energy_charge, 2),
    )
