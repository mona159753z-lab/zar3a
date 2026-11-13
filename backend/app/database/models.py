import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _uuid() -> str:
    return uuid.uuid4().hex


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class FieldRecord(Base):
    __tablename__ = "fields"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    farmer_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    region_ar: Mapped[str | None] = mapped_column(String(80), nullable=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    area_feddan: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_crop: Mapped[str | None] = mapped_column(String(40), nullable=True)
    previous_crops: Mapped[list] = mapped_column(JSON, default=list)   # oldest -> newest
    goal: Mapped[str | None] = mapped_column(String(40), nullable=True)
    water_availability: Mapped[str] = mapped_column(String(10), default="medium")
    soil: Mapped[dict] = mapped_column(JSON, default=dict)
    preferred_crops: Mapped[list] = mapped_column(JSON, default=list)
    avoid_crops: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AnalysisRecord(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    field_id: Mapped[str] = mapped_column(ForeignKey("fields.id"))
    status: Mapped[str] = mapped_column(String(20), default="completed")
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
