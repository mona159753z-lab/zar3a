"""فهم الكلام محليًا من غير أي API أو مفتاح.

مش LLM. دي حاجتين صغيرتين بنشتغل بيهم جوه الباك نفسه:
1) مطابقة تقريبية (fuzzy) للمحافظات والمحاصيل: بتتحمل أخطاء التعرف على الصوت زي "منوفيا" أو "قمحه".
2) مصنّف هدف (Naive Bayes على حروف الكلام) بيتدرب في أقل من ثانية من data/goal_examples.json،
   فبيفهم جمل زي "الميه مش بتوصل لآخر الأرض" حتى لو الكلمة المفتاحية مش موجودة.
"""
import json
import math
from collections import Counter
from difflib import SequenceMatcher
from functools import lru_cache

from . import knowledge as kb

FUZZY_RATIO = 0.80   # كل ما زاد، الغلط أقل بس التسامح أقل
MIN_FUZZY_LEN = 4
GOAL_MIN_CONF = 0.55


# ---------------- مطابقة تقريبية ----------------
def _windows(tokens: list[str], n: int):
    for i in range(len(tokens) - n + 1):
        yield " ".join(tokens[i:i + n])


def _fuzzy(text: str, pairs: list[tuple[str, str]]) -> str | None:
    tokens = kb.normalize_ar(text).split()
    best, best_r = None, 0.0
    for n in (2, 1):
        for win in _windows(tokens, n):
            if len(win) < MIN_FUZZY_LEN:
                continue
            for alias, ident in pairs:
                if alias.count(" ") + 1 != n or abs(len(alias) - len(win)) > 2:
                    continue
                r = SequenceMatcher(None, win, alias).ratio()
                if r > best_r:
                    best, best_r = ident, r
    return best if best_r >= FUZZY_RATIO else None


def find_crop(text: str, fuzzy: bool = False) -> str | None:
    return kb.match_crop(text) or (_fuzzy(text, kb._crop_pairs()) if fuzzy else None)


def find_governorate(text: str, fuzzy: bool = False) -> dict | None:
    if (g := kb.resolve_governorate(text)):
        return g
    if fuzzy and (gid := _fuzzy(text, kb._gov_pairs())):
        return next((g for g in kb.governorates() if g["id"] == gid), None)
    return None


# ---------------- مصنّف الهدف ----------------
def _grams(text: str, ns=(2, 3, 4)) -> list[str]:
    out = []
    for w in kb.normalize_ar(text).split():
        w = f" {w} "
        for n in ns:
            out += [w[i:i + n] for i in range(max(1, len(w) - n + 1))]
    return out


class _NB:
    def __init__(self, data: dict[str, list[str]], alpha: float = 0.5):
        self.alpha = alpha
        self.counts = {c: Counter(g for s in sents for g in _grams(s)) for c, sents in data.items()}
        self.totals = {c: sum(cnt.values()) for c, cnt in self.counts.items()}
        self.vocab = len(set().union(*self.counts.values()))
        n_docs = sum(len(s) for s in data.values())
        self.prior = {c: math.log(len(s) / n_docs) for c, s in data.items()}

    def predict(self, text: str) -> tuple[str, float]:
        grams = _grams(text)
        if not grams:
            return "other", 0.0
        scores = {}
        for c in self.counts:
            denom = self.totals[c] + self.alpha * self.vocab
            scores[c] = self.prior[c] + sum(math.log((self.counts[c][g] + self.alpha) / denom) for g in grams)
        m = max(scores.values())
        exp = {c: math.exp(v - m) for c, v in scores.items()}
        z = sum(exp.values())
        label = max(exp, key=exp.get)
        return label, exp[label] / z


@lru_cache
def _goal_model() -> _NB:
    raw = json.loads((kb.DATA_DIR / "goal_examples.json").read_text(encoding="utf-8"))
    return _NB({k: v for k, v in raw.items() if not k.startswith("_")})


def classify_goal(text: str) -> str | None:
    """الهدف من كلام حر، أو None لو مش واثق (والحوار يسأل تاني)."""
    if (g := kb.match_goal(text)):          # كلمة صريحة أسرع وأضمن
        return g
    label, conf = _goal_model().predict(text)
    return label if label != "other" and conf >= GOAL_MIN_CONF else None