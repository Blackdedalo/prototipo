import re
import unicodedata
from datetime import date

from pydantic import ValidationError

from app.models import ComplaintStatus
from app.schemas import ComplaintCreate


DOCUMENT_NUMBER_ONLY_TYPES = {"D.N.I", "CARNET UNIVERSITARIO", "LICENCIA", "TARJETA"}
ALLOWED_MODALITIES = {"PERDIDA", "ROBO", "HURTO"}


def normalize_text(value: str | None) -> str:
    text = str(value or "").strip().upper()
    text = unicodedata.normalize("NFD", text)
    return "".join(char for char in text if unicodedata.category(char) != "Mn")


def normalize_modality(value: str | None) -> str:
    text = normalize_text(value)
    return text.replace("Ã‰", "E").replace("Ãƒâ€°", "E")


def derive_police_station(event_district: str | None) -> str:
    district = str(event_district or "").strip()
    if not district:
        return ""
    district = re.sub(r"\s+", " ", district).upper()
    return f"COMISARIA DE {district}"


def _required(value: object) -> bool:
    return value is not None and str(value).strip() != ""


def _valid_name(value: str) -> bool:
    clean = value.strip()
    return len(clean) >= 2 and all(char.isalpha() or char.isspace() for char in clean)


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
        errors["dni"] = "El DNI debe tener exactamente 8 digitos."

    for field in ("first_names", "paternal_last_name", "maternal_last_name"):
        value = getattr(complaint, field)
        if not _valid_name(value):
            errors[field] = "Debe contener solo letras y espacios, minimo 2 caracteres."

    if not re.fullmatch(r"\d{9}", complaint.phone_primary):
        errors["phone_primary"] = "El telefono principal debe tener 9 digitos."

    if complaint.phone_secondary and not re.fullmatch(r"\d{9}", complaint.phone_secondary):
        errors["phone_secondary"] = "El telefono secundario debe tener 9 digitos."

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
        errors["event_latitude"] = "Latitud invalida."

    if complaint.event_longitude is not None and not -180 <= complaint.event_longitude <= 180:
        errors["event_longitude"] = "Longitud invalida."

    if len(complaint.lost_items) == 0:
        errors["lost_items"] = "Debe registrar al menos una especie o documento."

    for index, item in enumerate(complaint.lost_items):
        prefix = f"lost_items.{index}"
        if not _required(item.modality):
            errors[f"{prefix}.modality"] = "La modalidad es requerida."
        elif normalize_modality(item.modality) not in ALLOWED_MODALITIES:
            errors[f"{prefix}.modality"] = "La modalidad solo puede ser PERDIDA, ROBO o HURTO."

        if not _required(item.item_type):
            errors[f"{prefix}.item_type"] = "La especie es requerida."

        if item.item_type in DOCUMENT_NUMBER_ONLY_TYPES:
            if not _required(item.item_number):
                errors[f"{prefix}.item_number"] = "Para documentos debe ingresar solo el numero."
        elif item.item_type == "OTRO":
            if not _required(item.item_number):
                errors[f"{prefix}.item_number"] = "Para otra especie debe ingresar el nombre."
            if not _required(item.description):
                errors[f"{prefix}.description"] = "Para otra especie debe ingresar una descripcion."
        elif not _required(item.item_number) and not _required(item.description):
            errors[f"{prefix}.item_number"] = "Ingrese numero o descripcion."

    return errors


def validate_status_transition(status: str) -> bool:
    return status in {state.value for state in ComplaintStatus}
