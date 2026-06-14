from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import TrackingResponse
from app.services.complaint_service import get_complaint_by_code


router = APIRouter(prefix="/api/tracking", tags=["tracking"])


@router.get("/{code}", response_model=TrackingResponse)
def track(code: str, db: Session = Depends(get_db)) -> TrackingResponse:
    complaint = get_complaint_by_code(db, code)
    if not complaint:
        raise HTTPException(status_code=404, detail="No existe una denuncia con ese código.")
    return TrackingResponse(
        code=complaint.code,
        status=complaint.status,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at,
        complainant=(
            f"{complaint.paternal_last_name} {complaint.maternal_last_name} {complaint.first_names}"
        ),
        dni=complaint.dni,
        police_station=complaint.police_station,
        event_location=(
            f"{complaint.event_department}/{complaint.event_province}/"
            f"{complaint.event_district} - {complaint.event_address}"
        ),
    )
