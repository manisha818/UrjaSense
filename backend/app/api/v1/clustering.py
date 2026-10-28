
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.v1.readings import get_db
from backend.app.services.clustering_service import get_usage_patterns

router = APIRouter()


@router.get("/usage-patterns/{device_id}")
def usage_patterns(
    device_id: int,
    db: Session = Depends(get_db),
):
    if device_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="device_id must be greater than zero",
        )

    try:
        return get_usage_patterns(
            db=db,
            device_id=device_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
