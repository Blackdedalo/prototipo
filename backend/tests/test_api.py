from datetime import date

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def payload() -> dict:
    return {
        "dni": "73078001",
        "first_names": "GIOHAN IBSEN",
        "paternal_last_name": "TORRES",
        "maternal_last_name": "ORIHUELA",
        "birth_date": "1999-01-31",
        "civil_status": "SOLTERO",
        "phone_primary": "987747990",
        "phone_secondary": "",
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
        "narrative": "Perdida de documentos.",
        "ai_summary": "",
        "lost_items": [
            {
                "modality": "PÉRDIDA",
                "item_type": "CARNET UNIVERSITARIO",
                "item_number": "73078001",
                "brand": "",
                "model": "",
                "operator": "",
                "description": "",
            }
        ],
    }


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_get_track_and_admin_status():
    response = client.post("/api/complaints", json=payload())
    assert response.status_code == 201
    created = response.json()
    assert created["code"].startswith("PNP-")
    assert created["police_station"] == "COMISARIA DE CARHUAMAYO"

    get_response = client.get(f"/api/complaints/{created['code']}")
    assert get_response.status_code == 200
    assert get_response.json()["dni"] == "73078001"

    track_response = client.get(f"/api/tracking/{created['code']}")
    assert track_response.status_code == 200
    assert track_response.json()["status"] == "PNP_REVISION_POLICIAL"

    admin_response = client.patch(f"/api/admin/complaints/{created['id']}/status", json={"status": "PNP_REGISTRO_SIDPOL"})
    assert admin_response.status_code == 200
    assert admin_response.json()["status"] == "PNP_REGISTRO_SIDPOL"


def test_missing_complaint_returns_404():
    response = client.get("/api/tracking/PNP-2099-000000")
    assert response.status_code == 404
