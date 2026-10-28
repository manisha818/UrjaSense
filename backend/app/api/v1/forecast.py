
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.v1.readings import get_db
from backend.app.services.forecast_service import (
    forecast_next_day_consumption,
    get_forecast_accuracy,
)

router = APIRouter()


@router.get("/{device_id}/accuracy")
def get_device_forecast_accuracy(
    device_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_forecast_accuracy(
            db=db,
            device_id=device_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("/{device_id}")
def get_next_day_forecast(
    device_id: int,
    db: Session = Depends(get_db),
):
    try:
        return forecast_next_day_consumption(
            db=db,
            device_id=device_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
