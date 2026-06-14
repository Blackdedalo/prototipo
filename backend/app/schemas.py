from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import ComplaintStatus


class LostItemBase(BaseModel):
    modality: str = Field(default="PÉRDIDA")
    item_type: str
    item_number: str | None = None
    brand: str | None = None
    model: str | None = None
    operator: str | None = None
    description: str | None = None


class LostItemCreate(LostItemBase):
    pass


class LostItemRead(LostItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ComplaintBase(BaseModel):
    dni: str
    first_names: str
    paternal_last_name: str
    maternal_last_name: str
    birth_date: date | None = None
    civil_status: str | None = None
    phone_primary: str
    phone_secondary: str | None = None
    email: EmailStr
    father_name: str | None = None
    mother_name: str | None = None
    home_department: str
    home_province: str
    home_district: str
    home_address: str
    occupation: str
    event_date: date
    event_hour: int
    event_minute: int
    event_department: str
    event_province: str
    event_district: str
    event_address: str
    event_latitude: float | None = None
    event_longitude: float | None = None
    police_station: str
    complaint_type: str = "DENUNCIA"
    narrative: str | None = None
    ai_summary: str | None = None
    lost_items: list[LostItemCreate]


class ComplaintCreate(ComplaintBase):
    pass


class ComplaintRead(ComplaintBase):
    id: int
    code: str
    status: ComplaintStatus
    created_at: datetime
    updated_at: datetime
    lost_items: list[LostItemRead]
    model_config = ConfigDict(from_attributes=True)


class ValidationResponse(BaseModel):
    valid: bool
    errors: dict[str, str]


class StatusUpdate(BaseModel):
    status: ComplaintStatus


class TrackingResponse(BaseModel):
    code: str
    status: ComplaintStatus
    created_at: datetime
    updated_at: datetime
    complainant: str
    dni: str
    police_station: str
    event_location: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    context: dict[str, Any] = Field(default_factory=dict)
    provider: str | None = None
    current_step: int = 0


class ChatResponse(BaseModel):
    provider: str
    reply: str
    suggested_fields: dict[str, Any] = Field(default_factory=dict)
