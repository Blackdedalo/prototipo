from ast import literal_eval

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ComplaintCreate, ComplaintRead, ValidationResponse
from app.services.complaint_service import create_complaint, get_complaint_by_code
from app.services.validation_service import validate_complaint


router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.post("/validate", response_model=ValidationResponse)
def validate(payload: dict) -> ValidationResponse:
    errors = validate_complaint(payload)
    return ValidationResponse(valid=not errors, errors=errors)


@router.post("", response_model=ComplaintRead, status_code=201)
def create(payload: ComplaintCreate, db: Session = Depends(get_db)) -> ComplaintRead:
    try:
        return create_complaint(db, payload)
    except ValueError as exc:
        try:
            detail = literal_eval(str(exc))
        except (ValueError, SyntaxError):
            detail = str(exc)
        raise HTTPException(status_code=422, detail=detail) from exc


@router.get("/{code}", response_model=ComplaintRead)
def get_by_code(code: str, db: Session = Depends(get_db)) -> ComplaintRead:
    complaint = get_complaint_by_code(db, code)
    if not complaint:
        raise HTTPException(status_code=404, detail="Denuncia no encontrada.")
    return complaint
