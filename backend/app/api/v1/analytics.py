from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.api.v1.readings import get_db
from backend.app.services.anomaly_service import (
    detect_reading,
    train_detector,
)
from backend.app.services.recommendations import get_energy_recommendations


router = APIRouter()


class AnomalyCheckRequest(BaseModel):
    device_id: int = Field(gt=0)
    voltage: float = Field(ge=0)
    current: float = Field(ge=0)
    power_w: float = Field(ge=0)


@router.post("/anomalies/check")
def check_anomaly(
    payload: AnomalyCheckRequest,
    db: Annotated[Session, Depends(get_db)],
):
    try:
        detector = train_detector(
            db,
            device_id=payload.device_id,
        )

        result = detect_reading(
            detector,
            {
                "voltage": payload.voltage,
                "current": payload.current,
                "power_w": payload.power_w,
            },
        )

        return {
            "device_id": payload.device_id,
            **result,
            "message": (
                "Unusual electricity reading detected."
                if result["is_anomaly"]
                else "No unusual pattern detected."
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.get("/recommendations/{device_id}")
def get_recommendations(
    device_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    if device_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="device_id must be greater than zero",
        )

    try:
        return get_energy_recommendations(
            db,
            device_id=device_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
