from typing import Literal

from pydantic import BaseModel, Field

Goal = Literal["water_saving", "soil_health", "yield", "climate_resilience"]


class SoilData(BaseModel):
    ph: float | None = None
    ec: float | None = Field(None, description="الملوحة dS/m")
    organic_matter: float | None = None
    texture: str | None = None
    sample_date: str | None = None


class FieldCreate(BaseModel):
    farmer_name: str | None = None
    region: str | None = Field(None, description="اسم المحافظة بالعربي، بديل عن الإحداثيات")
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    area_feddan: float | None = Field(None, gt=0)
    current_crop: str | None = Field(None, description="id أو اسم عربي للمحصول الحالي")
    previous_crops: list[str] = Field(default_factory=list, description="الأقدم أولًا")
    goal: Goal | None = None
    water_availability: Literal["low", "medium", "high"] = "medium"
    soil: SoilData | None = None
    preferred_crops: list[str] = Field(default_factory=list)
    avoid_crops: list[str] = Field(default_factory=list)


class FieldOut(BaseModel):
    id: str
    farmer_name: str | None
    region_ar: str | None
    latitude: float
    longitude: float
    area_feddan: float | None
    current_crop: str | None
    previous_crops: list[str]
    goal: str | None
    water_availability: str
    soil: dict

    model_config = {"from_attributes": True}


class CropHistoryAdd(BaseModel):
    crops: list[str] = Field(description="الأقدم أولًا")


class VoiceTextTurn(BaseModel):
    session_id: str
    text: str


class VoiceSpeak(BaseModel):
    text: str = Field(max_length=1500)
