import uuid
from datetime import datetime, timezone

from ..ai import explainability as ex
from ..ai import rotation_generator as rg
from . import nasa_service
from . import knowledge as kb


async def run_analysis(profile: dict) -> dict:
    """profile: latitude, longitude, current_crop(id|None), previous_crops, goal, water_availability, soil, ..."""
    climate = await nasa_service.get_climate(profile["latitude"], profile["longitude"])
    gen = rg.generate(profile, climate)
    base = gen["scenarios"][0]
    scenarios = []
    for sc in gen["scenarios"]:
        e = ex.explain(sc, base, profile, climate, gen["seasons"])
        crops = [{
            "season_order": i + 1, "season": kb.SEASON_AR[c["season"]], "crop_id": c["id"],
            "name_ar": c["name_ar"], "name_en": c["name_en"], "family": c["family"],
            "assumed_default": sc["assumed"][i], "needs_expert_review": c["needs_expert_review"],
        } for i, c in enumerate(sc["seq"])]
        scenarios.append({
            "scenario_id": sc["id"], "type": sc["type"],
            "focus": ex.FOCUS_AR.get(sc["focus"]) if sc["focus"] else None,
            "crops": crops,
            "metrics": {
                "water_mm_total_estimate": round(sc["m"]["water"]),
                "water_change_vs_current_pct": e["water_change_pct"],
                "climate_index": round(sc["m"]["climate"], 1),
                "soil_index": round(sc["m"]["soil"], 1),
                "note": "مؤشرات نسبية للمقارنة بين البدائل، مش توقعات إنتاجية.",
            },
            "benefits": e["benefits"], "risks": e["risks"], "evidence": e["evidence"], "limitations": e["limitations"],
        })

    missing = []
    if not profile.get("soil"):
        missing.append("soil_nutrients")
    if not profile.get("current_crop"):
        missing.append("current_crop")
    if not profile.get("previous_crops"):
        missing.append("crop_history")
    if not profile.get("goal"):
        missing.append("goal")
    notes = []
    if gen["goal_assumed"]:
        notes.append("الهدف غير محدد؛ افترضنا توفير المياه.")
    if "water_filter_relaxed" in gen["notes"]:
        notes.append("خففنا فلتر المياه المنخفضة لعدم وجود بدائل.")
    if climate["note"]:
        notes.append(climate["note"])

    result = {
        "analysis_id": uuid.uuid4().hex,
        "field_id": profile.get("field_id"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_status": {
            "nasa_data_available": climate["available"],
            "nasa_source": climate["source"],
            "soil_test_available": bool(profile.get("soil")),
            "missing_information": missing,
            "notes": notes,
        },
        "scenarios": scenarios,
        "disclaimer": "نتائج مبدئية لدعم القرار، ومش بديل عن مهندس زراعي.",
    }
    result["spoken_summary_ar"] = ex.spoken_summary(profile.get("farmer_name"), scenarios)
    return result
