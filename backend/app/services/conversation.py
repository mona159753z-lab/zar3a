"""حوار بالأدوار: جمع ٤ معلومات (الاسم، المحافظة، المحصول الحالي، الهدف) بسؤال واحد في كل مرة."""
import json
import logging
import random
import re
import time
import uuid
from dataclasses import dataclass, field
from functools import lru_cache

from ..config import get_settings
from . import knowledge as kb
from . import nlu_local as nlu
from . import voice_service as vs

log = logging.getLogger("zar3a.conversation")

SLOTS = ["name", "location", "current_crop", "goal"]
GREETING = "أهلاً بيك في زرعة! أنا هساعدك تعرف أنسب دورة زراعية لأرضك. اسمك إيه؟"
QUESTIONS = {
    "name": "اسمك إيه؟",
    "location": "أرضك في أنهي محافظة؟",
    "current_crop": "بتزرع إيه في الأرض دلوقتي؟",
    "goal": "إيه أهم حاجة عايزها: توفير المياه، ولا تحسين التربة، ولا تحسين المحصول، ولا مواجهة المناخ؟",
}
RETRY = {
    "name": "ما فهمتش اسمك، ممكن تعيد؟",
    "location": "ما عرفتش المحافظة. قولي اسم المحافظة اللي فيها أرضك، زي المنوفية أو الغربية.",
    "current_crop": "ما عرفتش المحصول ده. قولي اسم المحصول اللي في أرضك دلوقتي، زي القمح أو الذرة أو البرسيم.",
    "goal": "ما فهمتش هدفك. قولي: توفير المياه، أو تحسين التربة، أو تحسين المحصول، أو مواجهة المناخ.",
}
NO_HEAR = "ما سمعتكش كويس، ممكن تعيد تاني؟"

DIALECT = """اللهجة (مهم جدًا): اتكلم عامية مصرية بس، زي ما فلاح أو جار مصري بيتكلم. ممنوع الفصحى خالص.
- قول: بتتكلم، فهمت إنك، دلوقتي، إيه، إزاي، ليه، عايز، مش، ده، دي، اللي، فيه، مفيش، كويس، تقدر، هحلل/هجيب (مثلا)، لسه.
- متقولش: تتحدث، أفهم أنك، الآن، حاليًا، ماذا، كيف، لماذا، هل، أريد، ليس، هذا، هذه، الذي، التي، هناك، لا يوجد، جيد، يمكنك، سوف.
- ابدأ السؤال بكلمة سؤال مصرية (إيه، فين، أنهي، بتزرع إيه) مش بـ"هل".
- مفيش تشكيل ومفيش كلام رسمي. أمثلة على الشكل المطلوب:
  "أهلاً يا فرحة! أرضك في أنهي محافظة؟"
  "ألف سلامة على الأرض. وبتزرع إيه فيها دلوقتي؟"
  "تمام، قمح. وإيه أكتر حاجة تاعباك في الأرض؟"
  "فهمت، الميه مش بتكفي. خليني أتأكد معاك: ..."
  "تمام يا فرحة، هحلل أرضك دلوقتي وأرجعلك."
- متفترضش إن المزارع راجل أو ست لو مش عارف؛ اتكلم بصيغة تنفع للاتنين."""

SYSTEM = """أنت "زرعة"، مساعد صوتي بيتكلم مع مزارعين في مصر. اتكلم بعامية مصرية بسيطة ودافية، زي ما بنتكلم مع جار أو قريب، مش زي روبوت.
شغلتك تتعرف على المزارع وأرضه في حوار طبيعي، وتجمع 4 معلومات:
1) name: اسم المزارع
2) location: المحافظة اللي فيها الأرض (id من القايمة تحت)
3) current_crop: المحصول المزروع حاليًا (id من القايمة تحت)
4) goal: هدفه، واحد من: water_saving (توفير المياه) / soil_health (تحسين التربة) / yield (تحسين المحصول) / climate_resilience (مواجهة المناخ)

المحافظات (id=الاسم): __GOVS__
المحاصيل (id=الاسم): __CROPS__

الوضع دلوقتي:
- المعلومات اللي معانا: __PROFILE__
- لسه ناقص: __MISSING__
- مرحلة الحوار: __STAGE__  (collecting = لسه بنجمع | confirming = قلنا الملخص وبنستنى تأكيده)

__DIALECT__

أسلوب الكلام:
- جملة أو اتنين بالكتير، وسؤال واحد بس في الرد.
- نوّع في صيغتك: متكررش نفس الترحيب أو نفس صيغة السؤال كل مرة. تفاعل مع اللي المزارع قاله بشكل طبيعي (لو اشتكى من حاجة قوله كلمة مواساة قصيرة قبل ما تكمل).
- متكتبش أرقام ولا رموز ولا إيموجي، لأن الرد هيتنطق بصوت.

الفهم:
- كلام المزارع جاي من تعرف صوتي وممكن فيه أخطاء أو لهجة (مثلا: منوفيا = المنوفية، قمحه = قمح، درة = ذرة، بندورة = طماطم). اختار أقرب id من القايمة.
- فول لوحده = faba_bean، وفول سوداني = peanut. ذرة لوحدها = maize.
- افهم الهدف من المشكلة اللي بيحكيها من غير ما تطلب منه يختار من قايمة:
  water_saving: الميه مش بتكفي أو مش بتوصل، الترعة ناشفة، تكلفة الري، عايز أوفر في الري
  soil_health: الأرض تعبت أو ضعفت أو مالحة، الأسمدة كتير، عايز أريّح الأرض، خصوبة
  yield: عايز المحصول يطلع أكتر، إنتاج، ربح، أكسب أكتر، جودة المحصول
  climate_resilience: الحر أو البرد أو الصقيع، الجو متقلب، الزرع بيتحرق من الحر، جفاف، مناخ
  لو ذكر هدفين، خد اللي شاكي منه أكتر. لو مش واضح خالص، اسأله بسؤال بسيط من غير قايمة طويلة.
- استخرج بس اللي المزارع قاله في ردّه ده. اللي مقالهوش خليه null. متخمنش ومتكملش من عندك. المزارع ممكن يقول كل المعلومات في جملة واحدة.
- لو صحّح معلومة قالها قبل كده (مثلا: لا مش الجيزة، المنوفية)، حط القيمة الجديدة في extracted. التصحيح ينفع لأي معلومة بما فيها الاسم.
- لو ذكر محافظة أو محصول مش في القايمة، حط اسمه زي ما قاله في الحقل.

المراحل والـ action:
- ask_missing: لسه فيه معلومة ناقصة بعد ردّه. اسأل عن أول ناقصة (بعد ما تتفاعل مع كلامه).
- confirm: بعد ردّه الأربع معلومات كملوا، أو اتغيرت معلومة وإحنا في confirming. قول ملخص بالأربع معلومات واسأله صح كده؟
- finish: إحنا في confirming وهو وافق (ايوه، صح، تمام) من غير ما يغيّر حاجة. اشكره باسمه وقوله إنك هتحلل أرضه دلوقتي. متسألش سؤال.
- ask_fix: إحنا في confirming وهو قال لأ من غير ما يقول إيه الغلط. اسأله إيه المعلومة اللي غلط.
- clarify: ما فهمتش معلومة قالها. اطلب منه يعيدها بطريقة تانية.
- intent: info (بيدي معلومات) / confirm_yes / confirm_no / question (سؤال) / smalltalk / unclear
- لو سأل سؤال عام عن الزراعة أو عن زرعة، جاوب بجملة قصيرة وصادقة من غير أرقام أو وعود، وبعدين كمّل بالسؤال الناقص أو التأكيد.

رد بـ JSON فقط بالشكل ده، واللي مش موجود يبقى null:
{"extracted": {"name": null, "location": null, "current_crop": null, "goal": null}, "intent": "info", "action": "ask_missing", "reply": "..."}"""

REGEN_SYSTEM = """أنت "زرعة"، مساعد صوتي بيتكلم مع مزارع مصري بعامية مصرية بسيطة ودافية. اكتب رد واحد قصير (جملة أو اتنين) من غير أرقام أو رموز أو إيموجي، لأنه هيتنطق بصوت. نوّع في الصيغة ومتكررش كلام الرد اللي فات.
__DIALECT__

المطلوب منك في الرد ده: __DIRECTIVE__
رد بـ JSON فقط: {"reply": "..."}"""

YES_WORDS = {kb.normalize_ar(w) for w in ["ايوه", "ايوا", "اه", "آه", "صح", "صحيح", "تمام", "مظبوط", "ماشي", "اكيد", "أكيد", "ظبط", "نعم", "اجل", "اوكي", "بالظبط", "طبعا", "yes", "ok", "okay"]}
NO_WORDS = {kb.normalize_ar(w) for w in ["لا", "لأ", "لاا", "لالا", "مش", "غلط", "ماشيش", "خطأ", "no"]}


def _is_yes(text: str) -> bool:
    toks = kb.normalize_ar(text).split()
    return any(t in YES_WORDS for t in toks) and not any(t in NO_WORDS for t in toks)


def _is_no(text: str) -> bool:
    return any(t in NO_WORDS for t in kb.normalize_ar(text).split())


@lru_cache
def _catalog() -> tuple[str, str]:
    def gov(g):
        extra = [a for a in g["aliases"] if kb.normalize_ar(a) != kb.normalize_ar(g["name_ar"]) and not kb.normalize_ar(a).startswith(kb.normalize_ar(g["name_ar"])[:3])]
        return f"{g['id']}={g['name_ar']}" + (f" ({'، '.join(extra[:2])})" if extra else "")
    govs = "، ".join(gov(g) for g in kb.governorates())
    crops = "، ".join(f"{c['id']}={c['name_ar']}" for c in kb.crops())
    return govs, crops


@dataclass
class Session:
    id: str
    profile: dict = field(default_factory=dict)       # name, location(id), location_ar, current_crop(id), goal
    history: list = field(default_factory=list)
    stage: str = "collecting"                          # collecting | confirming | done
    updated: float = field(default_factory=time.time)

    @property
    def missing(self) -> list[str]:
        return [s for s in SLOTS if not self.profile.get(s)]

    @property
    def done(self) -> bool:
        return self.stage == "done"


_sessions: dict[str, Session] = {}


def get_session(session_id: str | None) -> Session:
    now = time.time()
    ttl = get_settings().session_ttl_seconds
    for sid in [k for k, v in _sessions.items() if now - v.updated > ttl]:
        _sessions.pop(sid, None)
    if session_id and session_id in _sessions:
        s = _sessions[session_id]
        s.updated = now
        return s
    s = Session(id=uuid.uuid4().hex)
    _sessions[s.id] = s
    return s


def find_session(session_id: str) -> Session | None:
    return _sessions.get(session_id)


def start() -> tuple[Session, str]:
    s = get_session(None)
    s.history.append({"role": "assistant", "content": GREETING})
    return s, GREETING


_MSA_TO_EGY = [
    ("أفهم أنك", "فهمت إنك"), ("افهم انك", "فهمت إنك"), ("تتحدث عن", "بتتكلم عن"), ("تتحدث", "بتتكلم"),
    ("لا يوجد", "مفيش"), ("يمكنك", "تقدر"), ("يمكنني", "أقدر"), ("شكراً لك", "شكراً"), ("شكرًا لك", "شكراً"),
    ("حاليًّا", "دلوقتي"), ("حاليًا", "دلوقتي"), ("حالياً", "دلوقتي"), ("الآن", "دلوقتي"), ("ماذا", "إيه"),
    ("كيف", "إزاي"), ("لماذا", "ليه"), ("أريد", "عايز"), ("تريد", "عايز"), ("ليس", "مش"), ("هذا", "ده"),
    ("هذه", "دي"), ("الذي", "اللي"), ("التي", "اللي"), ("هناك", "فيه"), ("جيد", "كويس"), ("سوف", ""),
]
_DIAC = re.compile(r"[\u064B-\u0652\u0640]")


def _egyptianize(text: str) -> str:
    """شبكة أمان: لو الموديل نسي ونطق كلمة فصحى شائعة، نبدّلها بالمصري."""
    out = text
    for msa, egy in _MSA_TO_EGY:
        out = re.sub(rf"(?<!\w){re.escape(msa)}(?!\w)", egy, out)
    return re.sub(r"\s{2,}", " ", out).strip()


def _clean_name(v) -> str | None:
    if not isinstance(v, str):
        return None
    v = v.strip()
    return v[:40] if v else None


def _summary(s: Session) -> str:
    p = s.profile
    crop = kb.crops_by_id().get(p.get("current_crop"), {}).get("name_ar", "")
    return f"اسمك {p.get('name', '')}، وأرضك في {p.get('location_ar', '')}، وبتزرع {crop}، وهدفك {kb.GOALS_AR.get(p.get('goal'), '')}"


def _confirm_text(s: Session) -> str:
    return random.choice([f"يعني {_summary(s)}، صح كده؟", f"خليني أتأكد: {_summary(s)}. صح؟", f"تمام، {_summary(s)}. كده مظبوط؟"])


def _profile_for_llm(s: Session) -> str:
    p = s.profile
    out = {}
    if p.get("name"):
        out["name"] = p["name"]
    if p.get("location"):
        out["location"] = f"{p['location']} ({p.get('location_ar', '')})"
    if p.get("current_crop"):
        out["current_crop"] = f"{p['current_crop']} ({kb.crops_by_id()[p['current_crop']]['name_ar']})"
    if p.get("goal"):
        out["goal"] = f"{p['goal']} ({kb.GOALS_AR[p['goal']]})"
    return json.dumps(out, ensure_ascii=False) if out else "لسه مفيش حاجة"


def _text_matches(text: str, pairs: list[tuple[str, str]]) -> set[str]:
    """كل id اتذكر صراحة في كلام المزارع (بالأسماء المعروفة)، من غير LLM."""
    nt = kb.normalize_ar(text)
    return {ident for alias, ident in pairs if alias and re.search(rf"(?<!\w)[بولفك]?{re.escape(alias)}(?!\w)", nt)}


def _prefer_local(llm_id: str | None, text: str, pairs) -> str | None:
    """لو الاسم مكتوب صراحة في كلامه ومعاه id واحد بس، ده بيكسب على تخمين الـ LLM. لو الكلام فيه أكتر من واحد (تصحيح) بنثق في الـ LLM."""
    found = _text_matches(text, pairs)
    if llm_id in found or not found:
        return llm_id
    return next(iter(found)) if len(found) == 1 else llm_id


def _apply_extraction(s: Session, ext: dict, text: str, first_missing: str | None) -> tuple[set, list]:
    """بيطبّق اللي الـ LLM استخرجه بعد التحقق منه، وبيرجع (اللي اتغير، المشاكل). التصحيح بيكتب فوق القديم."""
    changed: set[str] = set()
    problems: list[tuple[str, str]] = []
    p = s.profile

    if (n := _clean_name(ext.get("name"))) and n != p.get("name"):
        p["name"] = n
        changed.add("name")

    if (raw := ext.get("location")):
        raw = str(raw)
        g = next((x for x in kb.governorates() if x["id"] == raw), None) or nlu.find_governorate(raw, fuzzy=True) \
            or kb.resolve_governorate(text)
        if g and (gid := _prefer_local(g["id"], text, kb._gov_pairs())) != g["id"]:
            g = next(x for x in kb.governorates() if x["id"] == gid)
        if g:
            if p.get("location") != g["id"]:
                changed.add("location")
            p["location"], p["location_ar"] = g["id"], g["name_ar"]
        else:
            problems.append(("location", raw))

    if (raw := ext.get("current_crop")):
        raw = str(raw)
        cid = kb.match_crop(raw) or nlu.find_crop(raw, fuzzy=True) or kb.match_crop(text)
        if cid:
            cid = _prefer_local(cid, text, kb._crop_pairs())
            if p.get("current_crop") != cid:
                changed.add("current_crop")
            p["current_crop"] = cid
        else:
            problems.append(("current_crop", raw))

    if (raw := ext.get("goal")):
        goal = kb.match_goal(str(raw)) or nlu.classify_goal(text)
        if goal:
            if p.get("goal") != goal:
                changed.add("goal")
            p["goal"] = goal
        else:
            problems.append(("goal", str(raw)))

    # شبكة أمان: لو الـ LLM سابها فاضية وإحنا بنسأل عنها، جرّب الفهم المحلي
    bad = {k for k, _ in problems}
    if first_missing == "location" and not ext.get("location") and "location" not in bad:
        if (g := nlu.find_governorate(text, fuzzy=True)):
            p["location"], p["location_ar"] = g["id"], g["name_ar"]
            changed.add("location")
    if first_missing == "current_crop" and not ext.get("current_crop") and "current_crop" not in bad:
        if (cid := nlu.find_crop(text, fuzzy=True)):
            p["current_crop"] = cid
            changed.add("current_crop")
    if first_missing == "goal" and not ext.get("goal") and "goal" not in bad:
        if (goal := nlu.classify_goal(text)):
            p["goal"] = goal
            changed.add("goal")
    return changed, problems


def _expected_action(s: Session, prev_stage: str, intent: str, text: str, changed: set, problems: list) -> str:
    if problems:
        return "clarify"
    if s.missing:
        return "ask_missing"
    if prev_stage == "confirming" and not changed:
        if (intent == "confirm_yes" or _is_yes(text)) and not _is_no(text):
            return "finish"
        if intent == "confirm_no" or _is_no(text):
            return "ask_fix"
    return "confirm"


def _directive(action: str, s: Session, problems: list) -> str:
    if action == "clarify":
        slot, raw = problems[0]
        what = {"location": "المحافظة", "current_crop": "المحصول", "goal": "الهدف"}[slot]
        return f"المزارع قال {what} \"{raw}\" وإحنا مش عارفينه. اطلب منه يقولها تاني بطريقة تانية، وإدّيله مثال أو اتنين بس."
    if action == "ask_missing":
        label = {"name": "اسمه", "location": "المحافظة اللي فيها أرضه", "current_crop": "المحصول اللي زارعه دلوقتي",
                 "goal": "أهم حاجة عايزها لأرضه (من غير ما تسرد له قايمة، سيبه يحكي)"}[s.missing[0]]
        return f"تفاعل مع كلامه بجملة قصيرة، وبعدين اسأله عن {label}."
    if action == "confirm":
        return f"قول له الملخص ده واسأله صح كده؟: {_summary(s)}"
    if action == "ask_fix":
        return "اسأله إيه المعلومة اللي غلط عشان تصلحها."
    return f"اشكره باسمه ({s.profile.get('name', '')}) وقوله إنك هتحلل أرضه دلوقتي. متسألش أي سؤال."


def _fallback_reply(action: str, s: Session, problems: list) -> str:
    if action == "clarify":
        return RETRY[problems[0][0]]
    if action == "ask_missing":
        return QUESTIONS[s.missing[0]]
    if action == "confirm":
        return _confirm_text(s)
    if action == "ask_fix":
        return "تمام، إيه المعلومة اللي غلط؟"
    return f"تمام يا {s.profile.get('name', '')}، هحلل أرضك دلوقتي."


async def _regenerate(s: Session, text: str, action: str, problems: list) -> str | None:
    msgs = [{"role": "system", "content": REGEN_SYSTEM.replace("__DIALECT__", DIALECT).replace("__DIRECTIVE__", _directive(action, s, problems))}] \
        + s.history[-4:] + [{"role": "user", "content": text}]
    try:
        data = await vs.chat_json(msgs, temperature=0.7)
    except vs.VoiceServiceError as e:
        log.warning("LLM regenerate failed: %s", e.message)
        return None
    r = data.get("reply") if isinstance(data, dict) else None
    return _egyptianize(r) if isinstance(r, str) and r.strip() else None


async def _process_llm(s: Session, text: str) -> dict:
    """الـ LLM بيفهم ويرد، والباك بيتحقق من المعلومات ويتحكم في مرحلة الحوار. لو الرد مش متسق مع الحالة بنطلب رد تاني."""
    prev_stage = s.stage
    first_missing = s.missing[0] if s.missing else None
    govs, crops = _catalog()
    system = (SYSTEM.replace("__DIALECT__", DIALECT).replace("__GOVS__", govs).replace("__CROPS__", crops)
              .replace("__PROFILE__", _profile_for_llm(s))
              .replace("__MISSING__", ", ".join(s.missing) or "لا شيء")
              .replace("__STAGE__", prev_stage))
    messages = [{"role": "system", "content": system}] + s.history[-10:] + [{"role": "user", "content": text}]
    data = await vs.chat_json(messages, temperature=0.5)
    if not isinstance(data, dict):
        raise vs.VoiceServiceError("رد الـ LLM مش بالشكل المتوقع")
    ext = data.get("extracted") if isinstance(data.get("extracted"), dict) else {}
    intent = str(data.get("intent") or "").strip()
    declared = str(data.get("action") or "").strip()
    reply = _egyptianize(data["reply"]) if isinstance(data.get("reply"), str) else ""

    changed, problems = _apply_extraction(s, ext, text, first_missing)
    expected = _expected_action(s, prev_stage, intent, text, changed, problems)
    s.stage = "done" if expected == "finish" else ("collecting" if s.missing else "confirming")

    regenerated = False
    if not reply or declared != expected:
        regenerated = True
        reply = await _regenerate(s, text, expected, problems) or _fallback_reply(expected, s, problems)

    s.history += [{"role": "user", "content": text}, {"role": "assistant", "content": reply}]
    s.updated = time.time()
    return {"reply": reply, "problems": [k for k, _ in problems], "extracted": ext, "engine": "llm",
            "intent": intent, "action": expected, "regenerated": regenerated}


# ---------------- وضع صوت المتصفح: من غير LLM، استخراج بالقواعد ----------------
_FILLERS = {kb.normalize_ar(w) for w in [
    "اسمي", "اسمى", "انا", "أنا", "اسم", "اسمه", "بيقولولي", "بيقولوا", "عليا", "يا", "اهلا", "أهلا", "مرحبا",
    "السلام", "عليكم", "ورحمة", "الله", "وبركاته", "صباح", "الخير", "مساء", "النور", "ايوه", "ايوا", "اه", "نعم", "طيب", "تمام"]}
_STOPS = {kb.normalize_ar(w) for w in [
    "من", "في", "وساكن", "ساكن", "بزرع", "عندي", "وارضي", "ارضي", "واسكن", "اسكن", "وبزرع", "وعايز", "عايز", "وعندي", "عاوز", "وعاوز", "مش", "لا", "لأ", "مو"]}


def _extract_name(text: str) -> str | None:
    toks = re.findall(r"[\u0600-\u06FF]+", text)
    norm = [kb.normalize_ar(t) for t in toks]
    start = norm.index(kb.normalize_ar("اسمي")) + 1 if kb.normalize_ar("اسمي") in norm else 0
    out = []
    for t, n in zip(toks[start:], norm[start:]):
        if n in _FILLERS:
            continue
        if n in _STOPS or kb.resolve_governorate(t) or kb.match_crop(t):
            break
        out.append(t)
        if len(out) == 2:
            break
    return " ".join(out) or None


def _process_rules(s: Session, text: str) -> dict:
    """فهم بالقواعد لما الـ LLM مش متاح. نفس مراحل الحوار (جمع ← تأكيد ← تحليل)."""
    prev_stage = s.stage
    first = s.missing[0] if s.missing else None
    p = s.profile
    acks, changed = [], False

    if (first == "name" or (prev_stage == "confirming" and "اسمي" in kb.normalize_ar(text).split())) and (n := _extract_name(text)):
        if p.get("name") != n:
            changed = True
            acks.append(f"أهلاً يا {n}.")
        p["name"] = n
    if (g := nlu.find_governorate(text, fuzzy=(first == "location"))):
        if p.get("location") != g["id"]:
            changed = True
            acks.append(f"{g['name_ar']}، تمام.")
        p["location"], p["location_ar"] = g["id"], g["name_ar"]
    if (cid := nlu.find_crop(text, fuzzy=(first == "current_crop"))):
        if p.get("current_crop") != cid:
            changed = True
            acks.append(f"{kb.crops_by_id()[cid]['name_ar']}، تمام.")
        p["current_crop"] = cid
    # الهدف بيتقبل بس لما باقي المعلومات كاملة، عشان كلمات زي "أرض" و"محصول" متلخبطش
    if prev_stage == "confirming" or all(p.get(k) for k in ("name", "location", "current_crop")):
        goal = kb.match_goal(text, allow_yield=(first == "goal")) or (nlu.classify_goal(text) if first == "goal" else None)
        if goal and p.get("goal") != goal:
            changed = True
            acks.append(f"{kb.GOALS_AR[goal]}، تمام.")
            p["goal"] = goal

    if s.missing:
        s.stage = "collecting"
        reply = (" ".join(acks) + " " + QUESTIONS[s.missing[0]]) if acks else RETRY[s.missing[0]]
    elif prev_stage == "confirming" and not changed:
        if _is_yes(text):
            s.stage, reply = "done", _fallback_reply("finish", s, [])
        elif _is_no(text):
            s.stage, reply = "confirming", _fallback_reply("ask_fix", s, [])
        else:
            s.stage, reply = "confirming", "قولي صح لو المعلومات تمام، أو قولي إيه اللي غلط."
    else:
        s.stage, reply = "confirming", _confirm_text(s)

    s.history += [{"role": "user", "content": text}, {"role": "assistant", "content": reply}]
    s.updated = time.time()
    return {"reply": reply, "problems": [], "extracted": {}, "engine": "rules"}


async def process_text(s: Session, text: str) -> dict:
    """LLM لو متاح، ولو فشل لأي سبب نرجع للفهم المحلي بدل ما الحوار يقف (والسبب بيتسجل ويرجع في الرد)."""
    err = None
    if vs.llm_enabled():
        try:
            return await _process_llm(s, text)
        except vs.VoiceServiceError as e:
            err = e.message
        except Exception as e:   # رد غريب من الموديل
            err = f"{type(e).__name__}: {e}"
            log.exception("LLM turn failed")
        log.warning("LLM fallback to rules: %s", err)
        vs.last_error = err
    out = _process_rules(s, text)
    if err:
        out["llm_error"] = err
    return out
