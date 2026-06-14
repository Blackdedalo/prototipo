import re
from datetime import date

from pydantic import ValidationError

from app.models import ComplaintStatus
from app.schemas import ComplaintCreate


def normalize_modality(value: str | None) -> str:
    text = str(value or "").strip().upper()
    return text.replace("Ã‰", "E").replace("É", "E")


def derive_police_station(event_district: str | None) -> str:
    district = str(event_district or "").strip()
    if not district:
        return ""
    district = re.sub(r"\s+", " ", district).upper()
    return f"COMISARIA DE {district}"


NAME_RE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{2,}$")


def _required(value: object) -> bool:
    return value is not None and str(value).strip() != ""


def validate_complaint(data: dict) -> dict[str, str]:
    errors: dict[str, str] = {}
    try:
        if _required(data.get("event_district")):
            data = {**data, "police_station": derive_police_station(data.get("event_district"))}
        complaint = ComplaintCreate.model_validate(data)
    except ValidationError as exc:
        for error in exc.errors():
            field = ".".join(str(part) for part in error["loc"])
            errors[field] = error["msg"]
        return errors

    if not re.fullmatch(r"\d{8}", complaint.dni):
        errors["dni"] = "El DNI debe tener exactamente 8 dígitos."

    for field in ("first_names", "paternal_last_name", "maternal_last_name"):
        value = getattr(complaint, field)
        if not NAME_RE.fullmatch(value.strip()):
            errors[field] = "Debe contener solo letras y espacios, mínimo 2 caracteres."

    if not re.fullmatch(r"\d{9}", complaint.phone_primary):
        errors["phone_primary"] = "El teléfono principal debe tener 9 dígitos."

    if complaint.phone_secondary and not re.fullmatch(r"\d{9}", complaint.phone_secondary):
        errors["phone_secondary"] = "El teléfono secundario debe tener 9 dígitos."

    required_text_fields = [
        "home_department",
        "home_province",
        "home_district",
        "home_address",
        "occupation",
        "event_department",
        "event_province",
        "event_district",
        "event_address",
        "police_station",
    ]
    for field in required_text_fields:
        if not _required(getattr(complaint, field)):
            errors[field] = "Campo requerido."

    if complaint.event_date > date.today():
        errors["event_date"] = "La fecha del hecho no puede ser futura."

    if not 0 <= complaint.event_hour <= 23:
        errors["event_hour"] = "La hora debe estar entre 00 y 23."

    if not 0 <= complaint.event_minute <= 59:
        errors["event_minute"] = "Los minutos deben estar entre 00 y 59."

    if complaint.event_latitude is not None and not -90 <= complaint.event_latitude <= 90:
        errors["event_latitude"] = "Latitud inválida."

    if complaint.event_longitude is not None and not -180 <= complaint.event_longitude <= 180:
        errors["event_longitude"] = "Longitud inválida."

    if len(complaint.lost_items) == 0:
        errors["lost_items"] = "Debe registrar al menos una especie o documento perdido."

    for index, item in enumerate(complaint.lost_items):
        prefix = f"lost_items.{index}"
        if not _required(item.modality):
            errors[f"{prefix}.modality"] = "La modalidad es requerida."
        elif normalize_modality(item.modality) not in {"PERDIDA", "ROBO"}:
            errors[f"{prefix}.modality"] = "La modalidad solo puede ser PÉRDIDA o ROBO."

        if not _required(item.item_type):
            errors[f"{prefix}.item_type"] = "La especie es requerida."

        if item.item_type in {"D.N.I", "CARNET UNIVERSITARIO"}:
            if not _required(item.item_number):
                errors[f"{prefix}.item_number"] = "Para DNI o carnet debe ingresar solo el número."
        elif not _required(item.item_number) and not _required(item.description):
            errors[f"{prefix}.item_number"] = "Ingrese número o descripción."

    return errors


def validate_status_transition(status: str) -> bool:
    return status in {state.value for state in ComplaintStatus}
