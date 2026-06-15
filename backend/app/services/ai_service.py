import json
import re
from typing import Any, Protocol

import httpx

from app.config import get_settings


BASE_SYSTEM_PROMPT = (
    "Eres un asistente para un prototipo de denuncia virtual PNP en Peru. "
    "Ayudas a completar datos personales, domicilio, datos del hecho y especies perdidas. "
    "Tambien puedes orientar, de forma general y dentro del marco peruano, sobre como realizar "
    "una denuncia presencial ante la PNP, que documentos o datos llevar y que pasos suelen seguirse. "
    "No brindas asesoria legal definitiva, no reemplazas a un abogado ni a una autoridad, no inventas "
    "datos personales y preguntas con claridad cuando falte informacion. Si la consulta sale del ambito "
    "de denuncias virtuales o presenciales en Peru, redirige amablemente al tema de denuncias."
)

FORM_FIELDS = {
    "dni",
    "first_names",
    "paternal_last_name",
    "maternal_last_name",
    "birth_date",
    "civil_status",
    "phone_primary",
    "phone_secondary",
    "email",
    "father_name",
    "mother_name",
    "home_department",
    "home_province",
    "home_district",
    "home_address",
    "occupation",
    "event_date",
    "event_hour",
    "event_minute",
    "event_department",
    "event_province",
    "event_district",
    "event_address",
    "event_latitude",
    "event_longitude",
    "police_station",
    "narrative",
    "lost_items",
}

DEFAULT_CONTEXT_VALUES = {
    "civil_status": {"SOLTERO"},
    "home_department": {"JUNIN"},
    "home_province": {"HUANCAYO"},
    "home_district": {"EL TAMBO"},
    "event_department": {"JUNIN"},
    "event_province": {"HUANCAYO"},
    "event_district": {"EL TAMBO"},
    "event_hour": {8, "8", "08"},
    "event_minute": {0, "0", "00"},
    "police_station": {"CPNP EL TAMBO"},
    "complaint_type": {"DENUNCIA"},
}

ITEM_TYPES = {
    "dni": "D.N.I",
    "d.n.i": "D.N.I",
    "documento": "D.N.I",
    "celular": "CELULAR",
    "telefono": "CELULAR",
    "teléfono": "CELULAR",
    "carnet": "CARNET UNIVERSITARIO",
    "licencia": "LICENCIA",
    "tarjeta": "TARJETA",
}

STEP_FIELDS = {
    0: {
        "dni",
        "first_names",
        "paternal_last_name",
        "maternal_last_name",
        "birth_date",
        "civil_status",
        "phone_primary",
        "phone_secondary",
        "email",
        "father_name",
        "mother_name",
    },
    1: {"home_department", "home_province", "home_district", "home_address", "occupation"},
    2: {
        "event_date",
        "event_hour",
        "event_minute",
        "event_department",
        "event_province",
        "event_district",
        "event_address",
        "event_latitude",
        "event_longitude",
        "police_station",
    },
    3: {"lost_items", "narrative"},
}

STEP_NAMES = {
    0: "Datos Generales",
    1: "Datos Domicilio",
    2: "Datos del Hecho",
    3: "Denuncia",
}

REQUIRED_STEP_FIELDS = {
    0: {
        "dni": "DNI",
        "first_names": "nombres",
        "paternal_last_name": "apellido paterno",
        "maternal_last_name": "apellido materno",
        "phone_primary": "teléfono principal",
        "email": "correo electrónico",
    },
    1: {
        "home_department": "departamento de domicilio",
        "home_province": "provincia de domicilio",
        "home_district": "distrito de domicilio",
        "home_address": "dirección de domicilio",
        "occupation": "ocupación",
    },
    2: {
        "event_date": "fecha del hecho",
        "event_hour": "hora del hecho",
        "event_minute": "minutos del hecho",
        "event_department": "departamento del hecho",
        "event_province": "provincia del hecho",
        "event_district": "distrito del hecho",
        "event_address": "dirección del hecho",
        "police_station": "comisaría",
    },
    3: {"lost_items": "especie perdida o robada"},
}


class AIProvider(Protocol):
    name: str

    async def chat(self, messages: list[dict[str, str]], context: dict[str, Any]) -> dict[str, Any]:
        ...


class MockProvider:
    name = "mock"

    async def chat(self, messages: list[dict[str, str]], context: dict[str, Any]) -> dict[str, Any]:
        capture_requested = should_capture_data(messages)
        current_step = current_form_step(context)
        suggested_fields = filter_fields_for_step(
            extract_suggested_fields(messages, context), current_step
        ) if capture_requested else {}
        missing = missing_fields_for_step(context, suggested_fields, current_step)

        if capture_requested and suggested_fields:
            reply = (
                f"Listo. Detecté datos para {STEP_NAMES.get(current_step, 'este paso')} "
                "y puedo colocarlos si los confirmas."
            )
            if missing:
                reply += " Para completar este componente todavía necesito: " + ", ".join(missing) + "."
        elif capture_requested:
            reply = (
                f"Aún no encontré datos claros para {STEP_NAMES.get(current_step, 'este paso')}. "
                "Necesito: " + ", ".join(missing) + "."
            )
        else:
            reply = (
                f"Estamos en {STEP_NAMES.get(current_step, 'este paso')}. "
                "Cuéntame los datos de este componente. Cuando quieras que los tome, escribe: toma mis datos."
            )
            if missing:
                reply += " Por ahora necesito: " + ", ".join(missing) + "."
        return {"reply": apply_behavior(reply), "suggested_fields": suggested_fields}


class GoogleProvider:
    name = "google"

    async def chat(self, messages: list[dict[str, str]], context: dict[str, Any]) -> dict[str, Any]:
        settings = get_settings()
        if not settings.google_api_key:
            return await MockProvider().chat(messages, context)
        model_name = settings.google_model.removeprefix("models/")
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model_name}:generateContent?key={settings.google_api_key}"
        )
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json={"contents": [{"parts": [{"text": _messages_to_text(messages, context)}]}]})
            response.raise_for_status()
        data = response.json()
        reply = data["candidates"][0]["content"]["parts"][0]["text"]
        reply, ai_fields = split_ai_response(reply)
        suggested_fields = {}
        if should_capture_data(messages):
            suggested_fields = filter_fields_for_step(
                {**extract_suggested_fields(messages, context), **ai_fields},
                current_form_step(context),
            )
            reply = append_missing_prompt(reply, context, suggested_fields)
        return {"reply": apply_behavior(reply), "suggested_fields": suggested_fields}


class OllamaProvider:
    name = "ollama"

    async def chat(self, messages: list[dict[str, str]], context: dict[str, Any]) -> dict[str, Any]:
        settings = get_settings()
        payload = {
            "model": settings.ollama_model,
            "stream": False,
            "messages": [{"role": "system", "content": build_system_prompt()}, *messages],
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{settings.ollama_base_url}/api/chat", json=payload)
            response.raise_for_status()
        data = response.json()
        reply, ai_fields = split_ai_response(data.get("message", {}).get("content", ""))
        suggested_fields = {}
        if should_capture_data(messages):
            suggested_fields = filter_fields_for_step(
                {**extract_suggested_fields(messages, context), **ai_fields},
                current_form_step(context),
            )
            reply = append_missing_prompt(reply, context, suggested_fields)
        return {"reply": apply_behavior(reply), "suggested_fields": suggested_fields}


class LMStudioProvider:
    name = "lmstudio"

    async def chat(self, messages: list[dict[str, str]], context: dict[str, Any]) -> dict[str, Any]:
        settings = get_settings()
        payload = {
            "model": settings.lm_studio_model,
            "messages": [{"role": "system", "content": build_system_prompt()}, *messages],
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{settings.lm_studio_base_url}/chat/completions", json=payload)
            response.raise_for_status()
        data = response.json()
        reply, ai_fields = split_ai_response(data["choices"][0]["message"]["content"])
        suggested_fields = {}
        if should_capture_data(messages):
            suggested_fields = filter_fields_for_step(
                {**extract_suggested_fields(messages, context), **ai_fields},
                current_form_step(context),
            )
            reply = append_missing_prompt(reply, context, suggested_fields)
        return {"reply": apply_behavior(reply), "suggested_fields": suggested_fields}


def get_provider(name: str | None = None) -> AIProvider:
    provider_name = (name or get_settings().ai_provider).lower()
    providers: dict[str, AIProvider] = {
        "google": GoogleProvider(),
        "ollama": OllamaProvider(),
        "lmstudio": LMStudioProvider(),
        "lm_studio": LMStudioProvider(),
        "mock": MockProvider(),
    }
    return providers.get(provider_name, MockProvider())


def _messages_to_text(messages: list[dict[str, str]], context: dict[str, Any]) -> str:
    conversation = "\n".join(f"{message['role']}: {message['content']}" for message in messages)
    step = current_form_step(context)
    allowed_fields = sorted(STEP_FIELDS.get(step, set()))
    if should_capture_data(messages):
        schema_hint = (
            f"El usuario pidió tomar sus datos para el componente activo: {STEP_NAMES.get(step, 'paso actual')}. "
            "Extrae solo datos de este componente activo, aunque la conversación contenga otros datos. "
            "Al final responde obligatoriamente con una linea JSON "
            "válida y sin markdown: "
            '{"suggested_fields":{"dni":"73078001","first_names":"JUAN","event_address":"JR EJEMPLO 123",'
            '"lost_items":[{"modality":"PÉRDIDA","item_type":"D.N.I","item_number":"73078001"}]}}. '
            f"Solo usa estas claves de suggested_fields para este paso: {allowed_fields}."
        )
    else:
        schema_hint = (
            "Conversa normalmente. No devuelvas JSON ni suggested_fields todavía. "
            f"El componente activo es {STEP_NAMES.get(step, 'paso actual')}; si el usuario esta llenando el formulario, "
            "pregunta solo por datos de ese componente. Si pregunta por una denuncia presencial, orienta con informacion "
            "general aplicable en Peru y aclara que no es asesoria legal definitiva. "
            "Si el usuario quiere autollenar, dile que escriba 'toma mis datos' cuando termine de contarte ese componente."
        )
    return f"{build_system_prompt()}\n{schema_hint}\n\nContexto parcial: {context}\n\nConversación:\n{conversation}"


def build_system_prompt() -> str:
    settings = get_settings()
    behavior = settings.assistant_behavior.strip().lower()
    styles = {
        "amable": "Tono amable, paciente y claro. Explica con calma y evita presionar.",
        "directo": "Tono directo y breve. Pide el dato faltante sin rodeos.",
        "agresivo": "Tono muy proactivo e insistente, pero siempre respetuoso. Empuja al usuario a completar el tramite.",
        "muletillas": "Tono conversacional con muletillas naturales, sin exagerar.",
    }
    style = styles.get(behavior, settings.assistant_behavior)
    muletilla = f" Usa ocasionalmente esta muletilla: '{settings.assistant_muletilla}'." if settings.assistant_muletilla else ""
    return f"{BASE_SYSTEM_PROMPT} Comportamiento configurado: {style}.{muletilla}"


def apply_behavior(reply: str) -> str:
    settings = get_settings()
    if settings.assistant_behavior.strip().lower() != "muletillas" or not settings.assistant_muletilla.strip():
        return reply
    muletilla = settings.assistant_muletilla.strip()
    if muletilla.lower() in reply.lower():
        return reply
    return f"{muletilla}, {reply[:1].lower()}{reply[1:]}" if reply else reply


def current_form_step(context: dict[str, Any]) -> int:
    try:
        step = int(context.get("_current_step", 0))
    except (TypeError, ValueError):
        return 0
    return max(0, min(step, 3))


def filter_fields_for_step(fields: dict[str, Any], step: int) -> dict[str, Any]:
    allowed = STEP_FIELDS.get(step, STEP_FIELDS[0])
    return {key: value for key, value in fields.items() if key in allowed}


def missing_fields_for_step(context: dict[str, Any], suggested_fields: dict[str, Any], step: int) -> list[str]:
    missing: list[str] = []
    for field, label in REQUIRED_STEP_FIELDS.get(step, {}).items():
        if field_has_value(field, context.get(field)) or field_has_value(field, suggested_fields.get(field)):
            continue
        missing.append(label)
    return missing


def field_has_value(field: str, value: Any) -> bool:
    if value in (None, "", [], {}):
        return False
    try:
        if value in DEFAULT_CONTEXT_VALUES.get(field, set()):
            return False
    except TypeError:
        pass
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        return len(value) > 0
    return True


def append_missing_prompt(reply: str, context: dict[str, Any], suggested_fields: dict[str, Any]) -> str:
    missing = missing_fields_for_step(context, suggested_fields, current_form_step(context))
    if not missing:
        return reply
    suffix = " Para completar este componente todavía necesito: " + ", ".join(missing) + "."
    return f"{reply.strip()}{suffix}" if reply.strip() else suffix.strip()


def should_capture_data(messages: list[dict[str, str]]) -> bool:
    latest = next((message.get("content", "") for message in reversed(messages) if message.get("role") == "user"), "")
    normalized = latest.lower()
    triggers = (
        "toma mis datos",
        "tomar mis datos",
        "usa mis datos",
        "usar mis datos",
        "aplica mis datos",
        "aplicar mis datos",
        "rellena el formulario",
        "rellenar el formulario",
        "llena el formulario",
        "llenar el formulario",
        "completa el formulario",
        "completar el formulario",
        "pasa mis datos",
        "captura mis datos",
    )
    return any(trigger in normalized for trigger in triggers)


def extract_suggested_fields(messages: list[dict[str, str]], context: dict[str, Any]) -> dict[str, Any]:
    source = "\n".join(message.get("content", "") for message in messages if message.get("role") == "user")
    suggestions: dict[str, Any] = {}

    dni = re.search(r"\b\d{8}\b", source)
    if dni and should_suggest("dni", context):
        suggestions["dni"] = dni.group(0)

    phones = re.findall(r"\b9\d{8}\b", source)
    if phones:
        if should_suggest("phone_primary", context):
            suggestions["phone_primary"] = phones[0]
        if len(phones) > 1 and should_suggest("phone_secondary", context):
            suggestions["phone_secondary"] = phones[1]

    email = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", source)
    if email and should_suggest("email", context):
        suggestions["email"] = email.group(0)

    birth_date = extract_labeled_date(source, ["naci", "nací", "nacimiento", "fecha de nacimiento"])
    if birth_date and should_suggest("birth_date", context):
        suggestions["birth_date"] = birth_date

    event_date = extract_labeled_date(source, ["hecho", "ocurrio", "ocurrió", "perdi", "perdí", "fecha"])
    if event_date and should_suggest("event_date", context):
        suggestions["event_date"] = event_date

    time_match = re.search(r"\b([01]?\d|2[0-3])[:hH]([0-5]\d)\b", source)
    if time_match:
        if should_suggest("event_hour", context):
            suggestions["event_hour"] = int(time_match.group(1))
        if should_suggest("event_minute", context):
            suggestions["event_minute"] = int(time_match.group(2))

    civil_status = re.search(r"\b(soltero|casado|divorciado|viudo)\b", source, flags=re.IGNORECASE)
    if civil_status and should_suggest("civil_status", context):
        suggestions["civil_status"] = civil_status.group(1).upper()

    for field, patterns in {
        "home_address": [r"(?:vivo en|domicilio en|direccion de domicilio|dirección de domicilio|mi direccion es|mi dirección es)\s+([^.\n;]+)"],
        "event_address": [
            r"(?:ocurrio en|ocurrió en|paso en|pasó en|hecho en|lugar del hecho|lo perdi en|lo perdí en)\s+([^.\n;]+)",
            r"(?:ocurrio|ocurrió|paso|pasó|hecho)[^.\n;]{0,90}\s+en\s+([^.\n;]+)",
        ],
        "occupation": [r"(?:ocupacion|ocupación|soy|trabajo como)\s+([A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{3,40})"],
        "police_station": [r"(?:comisaria|comisaría|comisar.a)\s+([A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ ]{3,80})"],
        "father_name": [r"(?:padre|mi padre es)\s+([A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{3,80})"],
        "mother_name": [r"(?:madre|mi madre es)\s+([A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{3,80})"],
    }.items():
        if not should_suggest(field, context):
            continue
        for pattern in patterns:
            match = re.search(pattern, source, flags=re.IGNORECASE)
            if match:
                suggestions[field] = clean_field_value(field, match.group(1))
                break

    for field, value in extract_locations(source).items():
        if should_suggest(field, context):
            suggestions[field] = value

    name_match = re.search(
        r"(?:me llamo|mi nombre es)\s+([A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{3,80})",
        source,
        flags=re.IGNORECASE,
    )
    if name_match:
        name_parts = clean_text(name_match.group(1)).split()
        if len(name_parts) >= 3:
            if should_suggest("paternal_last_name", context):
                suggestions["paternal_last_name"] = name_parts[0].upper()
            if should_suggest("maternal_last_name", context):
                suggestions["maternal_last_name"] = name_parts[1].upper()
            if should_suggest("first_names", context):
                suggestions["first_names"] = " ".join(name_parts[2:]).upper()

    lost_items = detect_lost_items(source)
    if lost_items:
        current_items = context.get("lost_items") or []
        suggestions["lost_items"] = merge_lost_items(current_items, lost_items)

    if source.strip() and should_suggest("narrative", context):
        suggestions["narrative"] = clean_text(source)

    return suggestions


def should_suggest(field: str, context: dict[str, Any]) -> bool:
    value = context.get(field)
    if value in ("", None, [], {}):
        return True
    return value in DEFAULT_CONTEXT_VALUES.get(field, set())


def extract_labeled_date(text: str, labels: list[str]) -> str | None:
    date_re = r"(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})"
    for label in labels:
        match = re.search(rf"{label}[^0-9]{{0,30}}{date_re}", text, flags=re.IGNORECASE)
        if match:
            return normalize_date(match.group(1))
    match = re.search(rf"\b{date_re}\b", text)
    return normalize_date(match.group(1)) if match else None


def normalize_date(value: str) -> str:
    if "/" not in value:
        return value
    day, month, year = value.split("/")
    return f"{year}-{month}-{day}"


def extract_locations(text: str) -> dict[str, str]:
    suggestions: dict[str, str] = {}
    for scope, prefix in {
        "home": r"(?:domicilio|vivo|resido)",
        "event": r"(?:hecho|ocurrio|ocurrió|perdi|perdí|extravie|extravié)",
    }.items():
        scoped = re.search(rf"{prefix}[\s\S]{{0,180}}", text, flags=re.IGNORECASE)
        source = scoped.group(0) if scoped else text
        for target, labels in {
            "department": ["departamento", "dpto"],
            "province": ["provincia", "prov"],
            "district": ["distrito", "dist"],
        }.items():
            label_re = "|".join(labels)
            match = re.search(rf"(?:{label_re})\s+([A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{{3,50}})", source, flags=re.IGNORECASE)
            if match:
                suggestions[f"{scope}_{target}"] = clean_location_value(match.group(1))
    return suggestions


def clean_location_value(value: str) -> str:
    value = re.split(
        r"\b(?:provincia|prov|distrito|dist|direccion|dirección|comisaria|comisaría)\b",
        value,
        flags=re.IGNORECASE,
    )[0]
    return clean_text(value).upper()


def detect_lost_items(text: str) -> list[dict[str, str]]:
    lowered = text.lower()
    if not any(word in lowered for word in ("perd", "pérd", "extrav")):
        return []

    detected_types: list[str] = []
    for needle, item_type in ITEM_TYPES.items():
        if needle in lowered and item_type not in detected_types:
            detected_types.append(item_type)
    if not detected_types:
        return []

    items = []
    for index, item_type in enumerate(detected_types):
        number = item_number_for_type(text, item_type, index)
        brand = re.search(r"(?:marca)\s+([A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ -]{2,30}?)(?:\s+modelo|\s+operador|[.,;]|$)", text, flags=re.IGNORECASE)
        model = re.search(r"(?:modelo)\s+([A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ -]{1,30}?)(?:\s+operador|[.,;]|$)", text, flags=re.IGNORECASE)
        operator = re.search(r"(?:operador)\s+([A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ -]{2,30}?)(?:[.,;]|$)", text, flags=re.IGNORECASE)
        items.append(
            {
                "modality": "PÉRDIDA",
                "item_type": item_type,
                "item_number": number,
                "brand": clean_text(brand.group(1)).upper() if brand and item_type == "CELULAR" else "",
                "model": clean_text(model.group(1)).upper() if model and item_type == "CELULAR" else "",
                "operator": clean_text(operator.group(1)).upper() if operator and item_type == "CELULAR" else "",
                "description": "",
            }
        )
    return items


def item_number_for_type(text: str, item_type: str, fallback_index: int) -> str:
    if item_type == "CELULAR":
        match = re.search(r"(?:celular|telefono|teléfono)[^\d]{0,30}(\d{6,12})", text, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    if item_type == "D.N.I":
        match = re.search(r"(?:dni|d\.n\.i|documento)[^\d]{0,30}(\d{8})", text, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    numbers = re.findall(r"\b\d{6,12}\b", text)
    return numbers[fallback_index] if fallback_index < len(numbers) else ""


def merge_lost_items(current_items: list[dict[str, Any]], new_items: list[dict[str, str]]) -> list[dict[str, Any]]:
    existing = {
        (item.get("item_type"), item.get("item_number"))
        for item in current_items
        if isinstance(item, dict)
    }
    merged = list(current_items)
    for item in new_items:
        key = (item.get("item_type"), item.get("item_number"))
        if key not in existing:
            merged.append(item)
    return merged


def split_ai_response(reply: str) -> tuple[str, dict[str, Any]]:
    match = re.search(r"\{[\s\S]*\"suggested_fields\"[\s\S]*\}\s*$", reply)
    if not match:
        return reply, {}
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return reply, {}
    suggested = payload.get("suggested_fields", {})
    if not isinstance(suggested, dict):
        return reply, {}
    clean_suggestions = {key: value for key, value in suggested.items() if key in FORM_FIELDS}
    return reply[: match.start()].strip(), clean_suggestions


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" ,.;:")


def clean_field_value(field: str, value: str) -> str:
    stop_words = {
        "home_address": ["departamento", "provincia", "distrito", "soy", "ocupacion", "ocupación"],
        "event_address": ["departamento", "provincia", "distrito", "comisaria", "comisaría", "perdi", "perdí"],
        "father_name": [" y mi madre", " madre", " telefono", " teléfono", " correo"],
        "mother_name": [" telefono", " teléfono", " correo", " vivo", " domicilio"],
        "police_station": [" perdi", " perdí", " extravie", " extravié"],
        "occupation": [" el hecho", " ocurrió", " ocurrio", " perdi", " perdí"],
    }
    cleaned = value
    for stop_word in stop_words.get(field, []):
        parts = re.split(stop_word, cleaned, maxsplit=1, flags=re.IGNORECASE)
        cleaned = parts[0]
    return clean_text(cleaned).upper()
