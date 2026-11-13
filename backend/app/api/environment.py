from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..database.models import FieldRecord
from ..services import nasa_service
from ..services.feature_engineering import annual_precip_mm

router = APIRouter(prefix="/api/environment", tags=["environment"])


@router.get("/{field_id}")
async def environment(field_id: str, db: Session = Depends(get_db)):
    rec = db.get(FieldRecord, field_id)
    if not rec:
        raise HTTPException(404, "الأرض مش موجودة")
    c = await nasa_service.get_climate(rec.latitude, rec.longitude)
    return {"field_id": field_id, "nasa_data_available": c["available"], "source": c["source"], "note": c["note"],
            "monthly": {"t2m_c": c["t2m"], "precip_mm_per_day": c["precip"], "solar_kwh_m2_day": c["solar"]},
            "annual_precip_mm": annual_precip_mm(c)}
