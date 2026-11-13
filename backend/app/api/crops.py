from fastapi import APIRouter

from ..services import knowledge as kb

router = APIRouter(prefix="/api", tags=["knowledge"])


@router.get("/crops")
def list_crops(season: str | None = None):
    return [c for c in kb.crops() if season in (None, c["season"])]


@router.get("/governorates")
def list_governorates():
    return kb.governorates()
