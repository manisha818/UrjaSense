from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.models import Device
from backend.app.db.session import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DeviceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: str
    created_at: datetime


@router.post("/", response_model=DeviceResponse, status_code=201)
def create_device(
    payload: DeviceCreate,
    db: Session = Depends(get_db),
):
    device = Device(name=payload.name)
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.get("/", response_model=list[DeviceResponse])
def list_devices(db: Session = Depends(get_db)):
    statement = select(Device).order_by(Device.id)
    return db.scalars(statement).all()


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
):
    device = db.get(Device, device_id)

    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    return device
