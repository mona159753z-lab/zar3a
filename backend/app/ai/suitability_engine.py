"""ملاءمة المناخ: قائمة على قواعد (مدى الحرارة المناسب للمحصول مقابل متوسط حرارة موسمه)."""
from ..services.feature_engineering import mean_temp


def crop_climate(crop: dict, climate: dict) -> dict:
    t = mean_temp(climate, crop["growing_months"])
    if t is None:
        return {"index": 0.5, "mean_temp": None}
    lo, hi = crop["temp_opt_c"]
    delta = 0 if lo <= t <= hi else (lo - t if t < lo else t - hi)
    return {"index": max(0.0, 1 - delta / crop.get("temp_tol_c", 8)), "mean_temp": round(t, 1)}
