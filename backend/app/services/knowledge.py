"""قاعدة المعرفة: محاصيل، محافظات، قواعد التناوب + مطابقة النصوص العربية."""
import json
import re
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

GOALS_AR = {
    "water_saving": "توفير المياه",
    "soil_health": "تحسين التربة",
    "yield": "تحسين المحصول",
    "climate_resilience": "مواجهة المناخ",
}
SEASON_AR = {"winter": "شتوي", "summer": "صيفي"}

_DIACRITICS = re.compile(r"[\u0617-\u061A\u064B-\u0652\u0640]")
_PREFIX3 = ("بال", "وال", "فال", "كال")


def normalize_ar(text: str) -> str:
    t = _DIACRITICS.sub("", (text or "").strip().lower())
    t = re.sub("[أإآٱ]", "ا", t)
    t = t.replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي")
    t = re.sub(r"[^\w\s]", " ", t)
    words = []
    for w in t.split():
        if len(w) > 5 and w[:3] in _PREFIX3:
            w = w[3:]
        elif len(w) > 4 and w.startswith("لل"):
            w = w[2:]
        elif len(w) > 3 and w.startswith("ال"):
            w = w[2:]
        words.append(w)
    return " ".join(words)


@lru_cache
def _load(name: str) -> dict:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


@lru_cache
def crops() -> list[dict]:
    return _load("crops.json")["crops"]


@lru_cache
def crops_by_id() -> dict[str, dict]:
    return {c["id"]: c for c in crops()}


@lru_cache
def rules() -> dict:
    return _load("rotation_rules.json")


@lru_cache
def governorates() -> list[dict]:
    return _load("governorates.json")["governorates"]


def _search(text: str, pairs: list[tuple[str, str]]) -> str | None:
    nt = normalize_ar(text)
    if not nt:
        return None
    for alias, ident in pairs:
        if re.search(rf"(?<!\w)[بولفك]?{re.escape(alias)}(?!\w)", nt):
            return ident
    return None


@lru_cache
def _crop_pairs() -> list[tuple[str, str]]:
    pairs = []
    for c in crops():
        for a in c["aliases_ar"] + [c["name_ar"], c["name_en"].lower()]:
            pairs.append((normalize_ar(a), c["id"]))
    return sorted(set(pairs), key=lambda p: -len(p[0]))


@lru_cache
def _gov_pairs() -> list[tuple[str, str]]:
    pairs = []
    for g in governorates():
        for a in g["aliases"] + [g["name_ar"]]:
            pairs.append((normalize_ar(a), g["id"]))
    return sorted(set(pairs), key=lambda p: -len(p[0]))


def match_crop(text: str | None) -> str | None:
    if not text:
        return None
    if text in crops_by_id():
        return text
    return _search(text, _crop_pairs())


def resolve_governorate(text: str | None) -> dict | None:
    if not text:
        return None
    gid = _search(text, _gov_pairs())
    return next((g for g in governorates() if g["id"] == gid), None) if gid else None


_GOAL_KEYWORDS = [
    ("water_saving", ["ميه", "مياه", "مايه", "توفير", "وفر", "اوفر", "نوفر", "ري"]),
    ("soil_health", ["تربه", "خصوبه"]),
    ("climate_resilience", ["مناخ", "حراره", "جفاف", "طقس"]),
    ("yield", ["محصول", "انتاج", "ربح", "كميه", "ازيد", "زياده"]),
]


def match_goal(text: str | None, allow_yield: bool = True) -> str | None:
    if not text:
        return None
    if text in GOALS_AR:
        return text
    nt = normalize_ar(text)
    for goal, kws in _GOAL_KEYWORDS:
        if goal == "yield" and not allow_yield:
            continue
        if any(re.search(rf"(?<!\w){k}(?!\w)", nt) for k in kws):
            return goal
    return None
