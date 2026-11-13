from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..database.models import FieldRecord
from ..schemas.field import FieldCreate
from . import knowledge as kb


def _crop_or_422(text: str, label: str) -> str:
    cid = kb.match_crop(text)
    if not cid:
        raise HTTPException(422, f"محصول غير معروف ({label}): {text}")
    return cid


def resolve(payload: FieldCreate) -> dict:
    lat, lon, region_ar = payload.latitude, payload.longitude, None
    if payload.region:
        g = kb.resolve_governorate(payload.region)
        if g:
            region_ar = g["name_ar"]
            if lat is None or lon is None:
                lat, lon = g["lat"], g["lon"]
    if lat is None or lon is None:
        raise HTTPException(422, "لازم تبعت إحداثيات أو اسم محافظة معروف.")
    return {
        "farmer_name": payload.farmer_name, "region_ar": region_ar, "latitude": lat, "longitude": lon,
        "area_feddan": payload.area_feddan,
        "current_crop": _crop_or_422(payload.current_crop, "current_crop") if payload.current_crop else None,
        "previous_crops": [_crop_or_422(c, "previous_crops") for c in payload.previous_crops],
        "goal": payload.goal, "water_availability": payload.water_availability,
        "soil": payload.soil.model_dump(exclude_none=True) if payload.soil else {},
        "preferred_crops": [_crop_or_422(c, "preferred") for c in payload.preferred_crops],
        "avoid_crops": [_crop_or_422(c, "avoid") for c in payload.avoid_crops],
    }


def save(db: Session, data: dict) -> FieldRecord:
    rec = FieldRecord(**data)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def to_profile(rec: FieldRecord) -> dict:
    return {
        "field_id": rec.id, "farmer_name": rec.farmer_name, "latitude": rec.latitude, "longitude": rec.longitude,
        "current_crop": rec.current_crop, "previous_crops": rec.previous_crops or [], "goal": rec.goal,
        "water_availability": rec.water_availability, "soil": rec.soil or {},
        "preferred_crops": rec.preferred_crops or [], "avoid_crops": rec.avoid_crops or [],
    }
