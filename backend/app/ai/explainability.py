"""تحويل الأرقام لشرح عربي بسيط: فوائد، مخاطر، أدلة، حدود."""
from ..services import knowledge as kb
from ..services.feature_engineering import annual_precip_mm, mean_temp

FOCUS_AR = {"water": "توفير المياه", "soil": "تحسين التربة", "climate": "الملاءمة للمناخ"}


def _names(seq):
    return " وبعدها ".join(c["name_ar"] for c in seq)


def explain(sc: dict, base: dict, profile: dict, climate: dict, seasons: list[str]) -> dict:
    m, bm = sc["m"], base["m"]
    water_pct = round((m["water"] - bm["water"]) / bm["water"] * 100) if bm["water"] else 0
    d_soil = m["soil"] - bm["soil"]
    d_clim = m["climate"] - bm["climate"]
    is_base = sc["id"] == "A"
    benefits, risks = [], []

    if not is_base:
        if water_pct <= -5:
            benefits.append(f"استهلاك المياه التقديري أقل بحوالي {abs(water_pct)}٪ من نظامك الحالي.")
        fixers = [c["name_ar"] for c in sc["seq"] if c["nitrogen_fixer"]]
        if d_soil >= 5:
            benefits.append(f"فيها محصول بقولي ({'، '.join(fixers)}) بيثبّت النيتروجين، وده مفيد للتربة." if fixers
                            else "تنوع أكبر في العائلات النباتية، وده بيساعد التربة وبيقلل تراكم الآفات.")
        if d_clim >= 5:
            benefits.append("متوسط الحرارة التاريخي في موقعك أقرب للمدى المناسب للمحاصيل دي.")
        if not benefits:
            benefits.append("مفيش ميزة واضحة على النظام الحالي في المؤشرات دي، لكنها بديل للمقارنة.")
        if water_pct >= 5:
            risks.append(f"استهلاك المياه التقديري أعلى بحوالي {water_pct}٪ من نظامك الحالي.")
        if d_soil <= -5:
            risks.append("تأثيرها على التربة أضعف من النظام الحالي حسب التقدير.")
        if d_clim <= -5:
            risks.append("ملاءمتها للحرارة في موقعك أقل من النظام الحالي.")
    else:
        benefits.append("ده نظامك الحالي، وبنستخدمه كنقطة مقارنة.")
        for kind, a, b in sc["violations"]:
            risks.append(f"التتابع {b['name_ar']} بعد {a['name_ar']} مخالف لقاعدة التناوب (نفس المحصول أو نفس العائلة).")
        if any(sc["assumed"]):
            risks.append("بعض المواسم افترضنا فيها محصول شائع لأنك ما ذكرتش محصول سابق ليها.")

    if profile.get("water_availability") != "high":
        for c in sc["seq"]:
            if c["water_class"] == "high":
                risks.append(f"{c['name_ar']} محصول عالي الاحتياج للمياه.")
    risks.append("التوصية تحتاج مراجعة مهندس زراعي قبل التنفيذ.")

    evidence = []
    for s in dict.fromkeys(seasons):
        months = next(c["growing_months"] for c in sc["seq"] if c["season"] == s) if any(c["season"] == s for c in sc["seq"]) else []
        t = mean_temp(climate, months) if months else None
        if t is not None:
            evidence.append(f"متوسط حرارة الموسم ال{kb.SEASON_AR[s]} في موقعك حوالي {t:.1f}°م ({climate['source']}).")
    for c in sc["seq"]:
        lo, hi = c["temp_opt_c"]
        evidence.append(f"{c['name_ar']}: مدى الحرارة المناسب {lo}-{hi}°م (قيمة مبدئية).")
    precip = annual_precip_mm(climate)
    if precip is not None:
        evidence.append(f"متوسط الأمطار السنوي في موقعك حوالي {precip} مم (NASA POWER)، يعني الري هو المصدر الأساسي للمياه.")

    limitations = ["قيم احتياجات المحاصيل مبدئية وتحتاج مراجعة مرجع زراعي.",
                   "بيانات المناخ متوسطات تاريخية، مش توقع للموسم الجاي."]
    if not profile.get("soil"):
        limitations.append("ما قدمتش تحليل للتربة.")
    if not climate["available"]:
        limitations.append(climate["note"])

    return {"benefits": benefits, "risks": [r for r in risks if r], "evidence": evidence[:6], "limitations": limitations,
            "water_change_pct": water_pct}


def spoken_summary(name: str | None, scenarios: list[dict]) -> str:
    ordinals = {"A": "الأول", "B": "التاني", "C": "التالت"}
    parts = [f"{name}، " if name else "", "عندك اختيارات لأرضك. "]
    for s in scenarios:
        crops = " وبعدها ".join(c["name_ar"] for c in s["crops"])
        line = f"الاختيار {ordinals[s['scenario_id']]}، {'نظامك الحالي' if s['scenario_id'] == 'A' else 'بديل'}: {crops}. "
        if s["scenario_id"] != "A":
            line += s["benefits"][0].replace("٪", " في المية") + " "
        parts.append(line)
    parts.append("دي تقديرات مبدئية، ومحتاجة مراجعة مهندس زراعي.")
    return "".join(parts)
