"""توليد دورات زراعية (٣ مواسم متتالية) → فلترة بالقيود → تقييم → اختيار A/B/C."""
from itertools import product

from ..services import knowledge as kb
from .suitability_engine import crop_climate

HORIZON = 3
OBJECTIVES = ("water", "soil", "climate")
GOAL_OBJECTIVE = {"water_saving": "water", "soil_health": "soil", "yield": "climate", "climate_resilience": "climate"}
NEXT_OBJECTIVE = {"water": "soil", "soil": "climate", "climate": "water"}


def build_seasons(current: dict | None, n: int = HORIZON) -> list[str]:
    first = "summer" if (current or {"season": "summer"})["season"] == "winter" else "winter"
    seq = [first]
    for _ in range(n - 1):
        seq.append("summer" if seq[-1] == "winter" else "winter")
    return seq


def violations(seq, prev, rules) -> list[tuple[str, dict, dict]]:
    out = []
    chain = ([prev] if prev else []) + list(seq)
    for a, b in zip(chain, chain[1:]):
        if a["id"] == b["id"]:
            out.append(("same_crop", a, b))
        elif a["family"] == b["family"] and a["family"] in rules["hard_no_consecutive_family"]:
            out.append(("same_family", a, b))
    return out


def metrics(seq, prev, rules, cidx) -> dict:
    water = sum(c["water_mm"] for c in seq)
    climate = sum(cidx[c["id"]]["index"] for c in seq) / len(seq) * 100
    fams = len({c["family"] for c in seq})
    soil = sum(c["soil_effect"] for c in seq) / len(seq) + 0.1 * (fams - 1)
    chain = ([prev] if prev else []) + list(seq)
    for a, b in zip(chain, chain[1:]):
        if a["family"] == b["family"]:
            soil -= rules["soft_penalty_consecutive_family"].get(a["family"], 0)
    soil_idx = max(0.0, min(100.0, (soil + 1) / 2 * 100))
    return {"water": water, "climate": climate, "soil": soil_idx, "families": fams}


def _candidates_by_season(seasons, profile):
    avoid = set(profile.get("avoid_crops") or [])
    pools, notes = {}, []
    for s in set(seasons):
        pool = [c for c in kb.crops() if c["season"] == s and c["id"] not in avoid]
        if profile.get("water_availability") == "low":
            filtered = [c for c in pool if c["water_class"] != "high"]
            if filtered:
                pool = filtered
            else:
                notes.append("water_filter_relaxed")
        pools[s] = pool
    return pools, notes


def _hamming(a, b):
    return sum(x != y for x, y in zip(a, b))


def _pick(cands, objective, exclude, far_from=None):
    rng = {k: (min(c["m"][k] for c in cands), max(c["m"][k] for c in cands)) for k in OBJECTIVES}
    weights = {k: (0.6 if k == objective else 0.2) for k in OBJECTIVES}

    def score(c):
        s = 0.0
        for k, w in weights.items():
            lo, hi = rng[k]
            n = 1.0 if hi == lo else (c["m"][k] - lo) / (hi - lo)
            if k == "water" and hi != lo:
                n = 1 - n
            s += w * n
        return s

    pool = [c for c in cands if c["ids"] not in exclude]
    if far_from is not None:
        far = [c for c in pool if _hamming(c["ids"], far_from) >= 2]
        pool = far or [c for c in pool if _hamming(c["ids"], far_from) >= 1]
    return max(pool, key=score) if pool else None


def baseline_sequence(profile, seasons):
    by_id = kb.crops_by_id()
    ids = list(profile.get("previous_crops") or []) + ([profile["current_crop"]] if profile.get("current_crop") else [])
    last = {}
    for i in ids:
        if i in by_id:
            last[by_id[i]["season"]] = by_id[i]
    defaults = kb.rules()["default_crop_by_season"]
    seq, assumed = [], []
    for s in seasons:
        c = last.get(s)
        assumed.append(c is None)
        seq.append(c or by_id[defaults[s]])
    return seq, assumed


def generate(profile: dict, climate: dict) -> dict:
    rules = kb.rules()
    by_id = kb.crops_by_id()
    current = by_id.get(profile.get("current_crop") or "")
    seasons = build_seasons(current)
    cidx = {c["id"]: crop_climate(c, climate) for c in kb.crops()}

    base_seq, base_assumed = baseline_sequence(profile, seasons)
    base_m = metrics(base_seq, current, rules, cidx)
    base_viol = violations(base_seq, current, rules)

    pools, notes = _candidates_by_season(seasons, profile)
    cands = []
    for combo in product(*[pools[s] for s in seasons]):
        if len({c['id'] for c in combo}) < len(combo) or violations(combo, current, rules):
            continue  # ممنوع تكرار نفس المحصول داخل الدورة + قواعد التناوب
        cands.append({"ids": tuple(c["id"] for c in combo), "seq": combo, "m": metrics(combo, current, rules, cidx)})

    base_ids = tuple(c["id"] for c in base_seq)
    goal = profile.get("goal") or "water_saving"
    obj_b = GOAL_OBJECTIVE[goal]
    b = _pick(cands, obj_b, {base_ids}) if cands else None
    c = None
    obj_c = NEXT_OBJECTIVE[obj_b]
    if b:
        c = _pick(cands, obj_c, {base_ids, b["ids"]}, far_from=b["ids"])

    scenarios = [{"id": "A", "type": "current_rotation", "focus": None, "seq": base_seq, "assumed": base_assumed,
                  "m": base_m, "violations": base_viol}]
    if b:
        scenarios.append({"id": "B", "type": "alternative_rotation", "focus": obj_b, "seq": list(b["seq"]),
                          "assumed": [False] * len(seasons), "m": b["m"], "violations": []})
    if c:
        scenarios.append({"id": "C", "type": "alternative_rotation", "focus": obj_c, "seq": list(c["seq"]),
                          "assumed": [False] * len(seasons), "m": c["m"], "violations": []})
    return {"seasons": seasons, "scenarios": scenarios, "cidx": cidx, "notes": notes, "goal_assumed": not profile.get("goal"),
            "candidates_count": len(cands)}
