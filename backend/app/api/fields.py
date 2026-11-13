from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..database.models import FieldRecord
from ..schemas.field import CropHistoryAdd, FieldCreate, FieldOut, SoilData
from ..services import field_service
from ..services import knowledge as kb

router = APIRouter(prefix="/api/fields", tags=["fields"])


def _get(db: Session, field_id: str) -> FieldRecord:
    rec = db.get(FieldRecord, field_id)
    if not rec:
        raise HTTPException(404, "الأرض مش موجودة")
    return rec


@router.post("", response_model=FieldOut)
def create_field(payload: FieldCreate, db: Session = Depends(get_db)):
    return field_service.save(db, field_service.resolve(payload))


@router.get("/{field_id}", response_model=FieldOut)
def get_field(field_id: str, db: Session = Depends(get_db)):
    return _get(db, field_id)


@router.post("/{field_id}/crop-history", response_model=FieldOut)
def add_crop_history(field_id: str, body: CropHistoryAdd, db: Session = Depends(get_db)):
    rec = _get(db, field_id)
    ids = []
    for c in body.crops:
        cid = kb.match_crop(c)
        if not cid:
            raise HTTPException(422, f"محصول غير معروف: {c}")
        ids.append(cid)
    rec.previous_crops = list(rec.previous_crops or []) + ids
    db.commit()
    db.refresh(rec)
    return rec


@router.post("/{field_id}/soil-data", response_model=FieldOut)
def add_soil(field_id: str, body: SoilData, db: Session = Depends(get_db)):
    rec = _get(db, field_id)
    rec.soil = body.model_dump(exclude_none=True)
    db.commit()
    db.refresh(rec)
    return rec
