"""NASA POWER (climatology) — متوسطات شهرية تاريخية لأي إحداثيات. من غير تسجيل."""
import json
import logging
from pathlib import Path

import httpx

from ..config import get_settings

log = logging.getLogger("zar3a.nasa")

POWER_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"

# تقدير تقريبي لدلتا النيل — بيتستخدم فقط لو NASA POWER مش متاح، وبيتعلّم في data_status.
_FALLBACK_T2M = {1: 13.0, 2: 14.0, 3: 17.0, 4: 21.0, 5: 25.0, 6: 27.5, 7: 28.5, 8: 28.5, 9: 26.5, 10: 23.0, 11: 18.0, 12: 14.5}

_memory: dict[str, dict] = {}


def _key(lat: float, lon: float) -> str:
    return f"{round(lat * 2) / 2:.1f}_{round(lon * 2) / 2:.1f}"


async def fetch_power(lat: float, lon: float) -> dict:
    params = {
        "parameters": "T2M,PRECTOTCORR,ALLSKY_SFC_SW_DWN",
        "community": "AG",
        "latitude": lat,
        "longitude": lon,
        "format": "JSON",
    }
    async with httpx.AsyncClient(timeout=get_settings().nasa_timeout) as client:
        r = await client.get(POWER_URL, params=params)
        r.raise_for_status()
        p = r.json()["properties"]["parameter"]

    def series(name: str) -> dict[int, float | None]:
        out = {}
        for i, m in enumerate(MONTHS, 1):
            v = p[name].get(m)
            out[i] = None if v is None or v <= -990 else float(v)
        return out

    return {
        "available": True,
        "source": "NASA POWER (climatology, community=AG)",
        "t2m": series("T2M"),                       # °C
        "precip": series("PRECTOTCORR"),            # mm/day
        "solar": series("ALLSKY_SFC_SW_DWN"),       # kWh/m2/day
        "note": None,
    }


async def get_climate(lat: float, lon: float) -> dict:
    key = _key(lat, lon)
    if key in _memory:
        return _memory[key]
    cache_file = CACHE_DIR / f"power_{key}.json"
    if cache_file.exists():
        try:
            raw = json.loads(cache_file.read_text())
            data = {**raw, **{k: {int(m): v for m, v in raw[k].items()} for k in ("t2m", "precip", "solar")}}
            _memory[key] = data
            return data
        except Exception:  # noqa: BLE001
            pass
    last_err = None
    for _ in range(2):
        try:
            data = await fetch_power(lat, lon)
            _memory[key] = data
            try:
                cache_file.write_text(json.dumps(data))
            except OSError:
                pass
            return data
        except Exception as e:  # noqa: BLE001
            last_err = e
            log.warning("NASA POWER failed: %s", e)
    return {
        "available": False,
        "source": "offline_default_estimate",
        "t2m": dict(_FALLBACK_T2M),
        "precip": {m: None for m in range(1, 13)},
        "solar": {m: None for m in range(1, 13)},
        "note": f"تعذر الاتصال بـ NASA POWER ({type(last_err).__name__}); استُخدم تقدير تقريبي لدلتا النيل.",
    }
