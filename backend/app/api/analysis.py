from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..database.models import AnalysisRecord, FieldRecord
from ..schemas.field import FieldCreate
from ..services import analysis_service, field_service

router = APIRouter(prefix="/api", tags=["analysis"])


def _analysis(db: Session, analysis_id: str) -> dict:
    rec = db.get(AnalysisRecord, analysis_id)
    if not rec:
        raise HTTPException(404, "التحليل مش موجود")
    return rec.result


@router.post("/quick-analysis")
async def quick_analysis(payload: FieldCreate):
    """تحليل مباشر من غير تخزين — مفيد لتجربة الواجهة بسرعة."""
    data = field_service.resolve(payload)
    return await analysis_service.run_analysis({**data, "field_id": None})


@router.post("/analysis/{field_id}")
async def run(field_id: str, db: Session = Depends(get_db)):
    rec = db.get(FieldRecord, field_id)
    if not rec:
        raise HTTPException(404, "الأرض مش موجودة")
    result = await analysis_service.run_analysis(field_service.to_profile(rec))
    db.add(AnalysisRecord(id=result["analysis_id"], field_id=field_id, status="completed", result=result))
    db.commit()
    return result


@router.get("/analysis/{analysis_id}")
def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    return _analysis(db, analysis_id)


@router.get("/analysis/{analysis_id}/scenarios")
def scenarios(analysis_id: str, db: Session = Depends(get_db)):
    return _analysis(db, analysis_id)["scenarios"]


@router.get("/analysis/{analysis_id}/scenarios/{scenario_id}/explanation")
def explanation(analysis_id: str, scenario_id: str, db: Session = Depends(get_db)):
    sc = next((s for s in _analysis(db, analysis_id)["scenarios"] if s["scenario_id"] == scenario_id.upper()), None)
    if not sc:
        raise HTTPException(404, "السيناريو مش موجود")
    return {k: sc[k] for k in ("scenario_id", "benefits", "risks", "evidence", "limitations")}
