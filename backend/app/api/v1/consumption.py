from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.api.v1.readings import get_db
from backend.app.services.aggregation import (
    get_consumption_summary,
    get_consumption_analytics,
    get_daily_consumption,
    get_consumption_trend,
)

router = APIRouter()


class ConsumptionSummaryResponse(BaseModel):
    total_consumption_kwh: float
    reading_count: int


@router.get("/summary", response_model=ConsumptionSummaryResponse)
def consumption_summary(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    device_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date must be before or equal to end_date",
        )

    return get_consumption_summary(
        db=db,
        start_date=start_date,
        end_date=end_date,
        device_id=device_id,
    )

@router.get("/analytics/{device_id}")
def consumption_analytics(
    device_id: int,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: Session = Depends(get_db),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date must be before or equal to end_date",
        )

    try:
        return get_consumption_analytics(
            db=db,
            device_id=device_id,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.get("/daily/{device_id}")
def daily_consumption(
    device_id: int,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: Session = Depends(get_db),
):
    if device_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="device_id must be greater than zero",
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date must be before or equal to end_date",
        )

    return get_daily_consumption(
        db=db,
        device_id=device_id,
        start_date=start_date,
        end_date=end_date,
    )

@router.get("/trends/{device_id}")
def consumption_trends(
    device_id: int,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: Session = Depends(get_db),
):
    if device_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="device_id must be greater than zero",
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date must be before or equal to end_date",
        )

    return get_consumption_trend(
        db=db,
        device_id=device_id,
        start_date=start_date,
        end_date=end_date,
    )



