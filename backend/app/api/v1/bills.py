from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.services.billing import estimate_bill


router = APIRouter()


class BillEstimateRequest(BaseModel):
    consumption_kwh: float = Field(ge=0)
    rate_per_kwh: float = Field(ge=0)


class BillEstimateResponse(BaseModel):
    consumption_kwh: float
    energy_charge: float
    estimated_total: float


@router.post("/estimate", response_model=BillEstimateResponse)
def calculate_bill(payload: BillEstimateRequest):
    estimate = estimate_bill(
        consumption_kwh=payload.consumption_kwh,
        rate_per_kwh=payload.rate_per_kwh,
    )

    return {
        "consumption_kwh": estimate.consumption_kwh,
        "energy_charge": estimate.energy_charge,
        "estimated_total": estimate.estimated_total,
    }
