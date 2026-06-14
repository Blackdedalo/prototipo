from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Complaint, ComplaintStatus
from app.schemas import ComplaintRead, StatusUpdate
from app.services.complaint_service import list_complaints


router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/complaints", response_model=list[ComplaintRead])
def list_all(
    code: str | None = None,
    dni: str | None = None,
    status: ComplaintStatus | None = None,
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ComplaintRead]:
    return list_complaints(db, code=code, dni=dni, status=status, date_from=date_from, date_to=date_to)


@router.patch("/complaints/{complaint_id}/status", response_model=ComplaintRead)
def update_status(complaint_id: int, payload: StatusUpdate, db: Session = Depends(get_db)) -> ComplaintRead:
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Denuncia no encontrada.")
    complaint.status = payload.status
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint
