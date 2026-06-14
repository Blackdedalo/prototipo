from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ComplaintStatus(StrEnum):
    PNP_REVISION_POLICIAL = "PNP_REVISION_POLICIAL"
    PNP_REGISTRO_SIDPOL = "PNP_REGISTRO_SIDPOL"
    PNP_DERIVADO_DIRECCION = "PNP_DERIVADO_DIRECCION"
    PNP_DERIVADO_FISCALIA = "PNP_DERIVADO_FISCALIA"
    FISCALIA_CARPETA_FISCAL = "FISCALIA_CARPETA_FISCAL"
    FISCALIA_RESOLUCION = "FISCALIA_RESOLUCION"
    JUDICIAL_DETENCION = "JUDICIAL_DETENCION"
    JUDICIAL_PENALIDAD = "JUDICIAL_PENALIDAD"
    OBSERVADO = "OBSERVADO"
    # Legacy values kept so existing prototype records can still be read.
    REGISTRADA = "REGISTRADA"
    EN_REVISION = "EN_REVISION"
    OBSERVADA = "OBSERVADA"
    APROBADA = "APROBADA"
    CONSTANCIA_GENERADA = "CONSTANCIA_GENERADA"
    ARCHIVADA = "ARCHIVADA"


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    status: Mapped[ComplaintStatus] = mapped_column(
        Enum(ComplaintStatus), default=ComplaintStatus.PNP_REVISION_POLICIAL, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    dni: Mapped[str] = mapped_column(String(8), index=True, nullable=False)
    first_names: Mapped[str] = mapped_column(String(120), nullable=False)
    paternal_last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    maternal_last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    civil_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    phone_primary: Mapped[str] = mapped_column(String(9), nullable=False)
    phone_secondary: Mapped[str | None] = mapped_column(String(9), nullable=True)
    email: Mapped[str] = mapped_column(String(160), nullable=False)
    father_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    mother_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    home_department: Mapped[str] = mapped_column(String(80), nullable=False)
    home_province: Mapped[str] = mapped_column(String(80), nullable=False)
    home_district: Mapped[str] = mapped_column(String(80), nullable=False)
    home_address: Mapped[str] = mapped_column(String(180), nullable=False)
    occupation: Mapped[str] = mapped_column(String(100), nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    event_hour: Mapped[int] = mapped_column(Integer, nullable=False)
    event_minute: Mapped[int] = mapped_column(Integer, nullable=False)
    event_department: Mapped[str] = mapped_column(String(80), nullable=False)
    event_province: Mapped[str] = mapped_column(String(80), nullable=False)
    event_district: Mapped[str] = mapped_column(String(80), nullable=False)
    event_address: Mapped[str] = mapped_column(String(180), nullable=False)
    event_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    event_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    police_station: Mapped[str] = mapped_column(String(120), nullable=False)
    complaint_type: Mapped[str] = mapped_column(String(40), default="DENUNCIA", nullable=False)
    narrative: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    lost_items: Mapped[list["LostItem"]] = relationship(
        back_populates="complaint", cascade="all, delete-orphan", lazy="selectin"
    )


class LostItem(Base):
    __tablename__ = "lost_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), nullable=False)
    modality: Mapped[str] = mapped_column(String(40), nullable=False)
    item_type: Mapped[str] = mapped_column(String(80), nullable=False)
    item_number: Mapped[str | None] = mapped_column(String(80), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model: Mapped[str | None] = mapped_column(String(80), nullable=True)
    operator: Mapped[str | None] = mapped_column(String(80), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    complaint: Mapped[Complaint] = relationship(back_populates="lost_items")
