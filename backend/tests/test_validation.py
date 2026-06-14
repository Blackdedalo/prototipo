from datetime import date, timedelta

from app.models import ComplaintStatus
from app.services.validation_service import validate_complaint, validate_status_transition


def valid_payload() -> dict:
    return {
        "dni": "73078001",
        "first_names": "GIOHAN IBSEN",
        "paternal_last_name": "TORRES",
        "maternal_last_name": "ORIHUELA",
        "birth_date": "1999-01-31",
        "civil_status": "SOLTERO",
        "phone_primary": "987747990",
        "phone_secondary": "987747990",
        "email": "giohan@example.com",
        "father_name": "IBSEN JUAN",
        "mother_name": "CONNIE MARGOT",
        "home_department": "JUNIN",
        "home_province": "HUANCAYO",
        "home_district": "EL TAMBO",
        "home_address": "JR. HUAYTAPALLANA 940",
        "occupation": "INGENIERO",
        "event_date": date.today().isoformat(),
        "event_hour": 4,
        "event_minute": 5,
        "event_department": "JUNIN",
        "event_province": "HUANCAYO",
        "event_district": "CARHUAMAYO",
        "event_address": "JR. HUAYTAPALLANA 940",
        "event_latitude": -12.0408131,
        "event_longitude": -75.2237432,
        "police_station": "CPNP EL TAMBO",
        "complaint_type": "DENUNCIA",
        "narrative": "",
        "ai_summary": "",
        "lost_items": [
            {
                "modality": "PÉRDIDA",
                "item_type": "D.N.I",
                "item_number": "73078001",
                "brand": "",
                "model": "",
                "operator": "",
                "description": "",
            }
        ],
    }


def test_valid_payload_has_no_errors():
    assert validate_complaint(valid_payload()) == {}


def test_invalid_dni_is_reported():
    payload = valid_payload()
    payload["dni"] = "123"
    assert "dni" in validate_complaint(payload)


def test_invalid_email_is_reported():
    payload = valid_payload()
    payload["email"] = "correo-invalido"
    assert "email" in validate_complaint(payload)


def test_invalid_phone_is_reported():
    payload = valid_payload()
    payload["phone_primary"] = "987"
    assert "phone_primary" in validate_complaint(payload)


def test_future_event_date_is_reported():
    payload = valid_payload()
    payload["event_date"] = (date.today() + timedelta(days=1)).isoformat()
    assert "event_date" in validate_complaint(payload)


def test_empty_lost_items_is_reported():
    payload = valid_payload()
    payload["lost_items"] = []
    assert "lost_items" in validate_complaint(payload)


def test_hurto_modality_is_not_allowed():
    payload = valid_payload()
    payload["lost_items"][0]["modality"] = "HURTO"
    assert "lost_items.0.modality" in validate_complaint(payload)


def test_dni_or_carnet_requires_number():
    payload = valid_payload()
    payload["lost_items"][0]["item_type"] = "CARNET UNIVERSITARIO"
    payload["lost_items"][0]["item_number"] = ""
    payload["lost_items"][0]["description"] = "Carnet sin numero"
    assert "lost_items.0.item_number" in validate_complaint(payload)


def test_status_validation():
    assert validate_status_transition(ComplaintStatus.PNP_REVISION_POLICIAL.value)
    assert validate_status_transition(ComplaintStatus.OBSERVADO.value)
    assert not validate_status_transition("INVALIDO")
