
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.models import Device, Reading
from backend.app.db.session import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ReadingCreate(BaseModel):
    device_id: int = Field(gt=0)
    recorded_at: datetime | None = None
    voltage: float | None = Field(default=None, ge=0)
    current: float | None = Field(default=None, ge=0)
    power_w: float | None = Field(default=None, ge=0)
    energy_kwh: float = Field(ge=0)




class ReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    recorded_at: datetime
    voltage: float | None
    current: float | None
    power_w: float | None
    energy_kwh: float


@router.post("/", response_model=ReadingResponse, status_code=201)
def create_reading(
    payload: ReadingCreate,
    db: Session = Depends(get_db),
):
    device = db.get(Device, payload.device_id)

    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    reading = Reading(**payload.model_dump())
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


@router.get("/", response_model=list[ReadingResponse])
def list_readings(
    device_id: int | None = None,
    db: Session = Depends(get_db),
):
    statement = select(Reading).order_by(Reading.id.desc())

    if device_id is not None:
        statement = statement.where(Reading.device_id == device_id)

    return db.scalars(statement).all()
