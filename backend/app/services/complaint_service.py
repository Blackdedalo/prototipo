from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Complaint, ComplaintStatus, LostItem
from app.schemas import ComplaintCreate
from app.services.validation_service import derive_police_station, validate_complaint


def generate_complaint_code(db: Session) -> str:
    year = datetime.now().year
    prefix = f"PNP-{year}-"
    count = db.scalar(select(func.count()).select_from(Complaint).where(Complaint.code.like(f"{prefix}%"))) or 0
    return f"{prefix}{count + 1:06d}"


def create_complaint(db: Session, payload: ComplaintCreate) -> Complaint:
    errors = validate_complaint(payload.model_dump())
    if errors:
        raise ValueError(str(errors))

    complaint_data = payload.model_dump(exclude={"lost_items"})
    complaint_data["police_station"] = derive_police_station(complaint_data.get("event_district"))
    complaint = Complaint(
        **complaint_data,
        code=generate_complaint_code(db),
        status=ComplaintStatus.PNP_REVISION_POLICIAL,
    )
    complaint.lost_items = [LostItem(**item.model_dump()) for item in payload.lost_items]
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


def get_complaint_by_code(db: Session, code: str) -> Complaint | None:
    return db.scalar(select(Complaint).where(Complaint.code == code.strip().upper()))


def list_complaints(
    db: Session,
    code: str | None = None,
    dni: str | None = None,
    status: ComplaintStatus | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[Complaint]:
    query = select(Complaint).order_by(Complaint.created_at.desc())
    if code:
        query = query.where(Complaint.code.contains(code.strip().upper()))
    if dni:
        query = query.where(Complaint.dni.contains(dni.strip()))
    if status:
        query = query.where(Complaint.status == status)
    if date_from:
        query = query.where(func.date(Complaint.created_at) >= date_from)
    if date_to:
        query = query.where(func.date(Complaint.created_at) <= date_to)
    return list(db.scalars(query).all())
