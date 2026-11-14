"""تقدير التربة من SoilGrids (نقاط محفوظة في data/soil_points.csv).

ده تقدير على مستوى المنطقة (بكسل ~250م)، مش تحليل لأرض المزارع.
"""
import csv
import math
from functools import lru_cache
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "soil_points.csv"
MAX_DISTANCE_KM = 35.0   # أبعد من كده مفيش تقدير؛ أحسن من تقدير مضلل


@lru_cache
def _points() -> list[dict]:
    if not CSV_PATH.exists():
        return []
    out = []
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            try:
                out.append({k: (float(v) if k != "region" else v) for k, v in row.items()})
            except (TypeError, ValueError):
                continue   # صف ناقص: نتجاهله
    return out


def _km(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))


def usda_texture(clay: float, sand: float, silt: float) -> str:
    """قوام التربة حسب مثلث USDA (بالإنجليزي)."""
    if silt + 1.5 * clay < 15:
        return "sand"
    if silt + 1.5 * clay >= 15 and silt + 2 * clay < 30:
        return "loamy sand"
    if (7 <= clay < 20 and sand > 52 and silt + 2 * clay >= 30) or (clay < 7 and silt < 50 and silt + 2 * clay >= 30):
        return "sandy loam"
    if 7 <= clay < 27 and 28 <= silt < 50 and sand <= 52:
        return "loam"
    if (silt >= 50 and 12 <= clay < 27) or (50 <= silt < 80 and clay < 12):
        return "silt loam"
    if silt >= 80 and clay < 12:
        return "silt"
    if 20 <= clay < 35 and silt < 28 and sand > 45:
        return "sandy clay loam"
    if 27 <= clay < 40 and 20 < sand <= 45:
        return "clay loam"
    if 27 <= clay < 40 and sand <= 20:
        return "silty clay loam"
    if clay >= 35 and sand > 45:
        return "sandy clay"
    if clay >= 40 and silt >= 40:
        return "silty clay"
    if clay >= 40:
        return "clay"
    return "loam"


TEXTURE_AR = {
    "sand": "رملية", "loamy sand": "رملية طميية", "sandy loam": "طميية رملية", "loam": "طميية",
    "silt loam": "طميية سلتية", "silt": "سلتية", "sandy clay loam": "طميية طينية رملية",
    "clay loam": "طميية طينية", "silty clay loam": "طميية طينية سلتية", "sandy clay": "طينية رملية",
    "silty clay": "طينية سلتية", "clay": "طينية",
}


def estimate(lat: float | None, lon: float | None) -> dict | None:
    """أقرب نقطة تربة في حدود MAX_DISTANCE_KM، أو None."""
    if lat is None or lon is None:
        return None
    best, best_d = None, None
    for p in _points():
        d = _km(lat, lon, p["lat"], p["lon"])
        if best_d is None or d < best_d:
            best, best_d = p, d
    if best is None or best_d > MAX_DISTANCE_KM:
        return None
    tex = usda_texture(best["clay"], best["sand"], best["silt"])
    return {
        "source": "SoilGrids (تقدير، مش تحليل فعلي)",
        "point": best["region"], "distance_km": round(best_d),
        "ph": best["phh2o"], "clay_pct": best["clay"], "sand_pct": best["sand"], "silt_pct": best["silt"],
        "cec": best["cec"], "texture": tex, "texture_ar": TEXTURE_AR.get(tex, tex),
    }
