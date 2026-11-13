"""منطق الحوار مع LLM وهمي (من غير إنترنت): تصحيح، تأكيد، ردود متناقضة، وسقوط الـ LLM."""
import asyncio

import pytest

from app.services import conversation as conv
from app.services import voice_service as vs


class FakeLLM:
    def __init__(self, *responses):
        self.queue = list(responses)
        self.calls = 0

    async def __call__(self, messages, temperature=0.3):
        self.calls += 1
        r = self.queue.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def run(s, text, fake, monkeypatch):
    monkeypatch.setattr(vs, "llm_enabled", lambda: True)
    monkeypatch.setattr(vs, "chat_json", fake)
    return asyncio.run(conv.process_text(s, text))


def R(ext=None, intent="info", action="ask_missing", reply="رد"):
    return {"extracted": {"name": None, "location": None, "current_crop": None, "goal": None, **(ext or {})},
            "intent": intent, "action": action, "reply": reply}


def test_everything_in_one_sentence_then_confirm_then_done(monkeypatch):
    s = conv.Session(id="t")
    f = FakeLLM(R({"name": "فرحة", "location": "gharbia", "current_crop": "maize", "goal": "water_saving"}, action="confirm", reply="يعني الغربية والذرة، صح؟"))
    out = run(s, "اسمي فرحة وأرضي في الغربية وزارعة ذرة وعايزة أوفر مياه", f, monkeypatch)
    assert s.stage == "confirming" and not s.done and out["engine"] == "llm" and f.calls == 1
    assert s.profile["location"] == "gharbia" and s.profile["current_crop"] == "maize"
    out = run(s, "ايوه صح", FakeLLM(R(intent="confirm_yes", action="finish", reply="تمام يا فرحة")), monkeypatch)
    assert s.done and out["reply"] == "تمام يا فرحة"


def test_correction_overwrites_and_reconfirms(monkeypatch):
    s = conv.Session(id="t", stage="confirming", profile={"name": "فرحة", "location": "giza", "location_ar": "الجيزة", "current_crop": "wheat", "goal": "yield"})
    out = run(s, "لا مش الجيزة، المنوفية", FakeLLM(R({"location": "menoufia"}, intent="info", action="confirm", reply="المنوفية، صح كده؟")), monkeypatch)
    assert s.profile["location"] == "menoufia" and s.profile["location_ar"] == "المنوفية"
    assert s.stage == "confirming" and not out["regenerated"]


def test_name_can_be_corrected(monkeypatch):
    s = conv.Session(id="t", stage="confirming", profile={"name": "فرح", "location": "giza", "location_ar": "الجيزة", "current_crop": "wheat", "goal": "yield"})
    run(s, "اسمي فرحة مش فرح", FakeLLM(R({"name": "فرحة"}, action="confirm")), monkeypatch)
    assert s.profile["name"] == "فرحة" and s.stage == "confirming"


def test_inconsistent_action_triggers_regeneration(monkeypatch):
    # الـ LLM قال ask_missing بينما الأربع معلومات كملوا → لازم يتطلب رد تاني للتأكيد
    s = conv.Session(id="t", profile={"name": "فرحة", "location": "giza", "location_ar": "الجيزة", "current_crop": "wheat"})
    f = FakeLLM(R({"goal": "soil_health"}, action="ask_missing", reply="طيب إيه الهدف؟"), {"reply": "يعني التربة، صح كده؟"})
    out = run(s, "الأرض تعبت", f, monkeypatch)
    assert f.calls == 2 and out["regenerated"] and out["reply"] == "يعني التربة، صح كده؟" and s.stage == "confirming"


def test_unknown_governorate_asks_again_and_keeps_state(monkeypatch):
    s = conv.Session(id="t", profile={"name": "فرحة"})
    f = FakeLLM(R({"location": "المريخ"}, action="ask_missing", reply="تمام"), {"reply": "ما عرفتش المحافظة، قولها تاني."})
    out = run(s, "أرضي في المريخ", f, monkeypatch)
    assert "location" not in s.profile and out["problems"] == ["location"] and s.stage == "collecting"


def test_llm_yes_not_trusted_when_farmer_changed_something(monkeypatch):
    s = conv.Session(id="t", stage="confirming", profile={"name": "فرحة", "location": "giza", "location_ar": "الجيزة", "current_crop": "wheat", "goal": "yield"})
    run(s, "ايوه بس الأرض في الغربية", FakeLLM(R({"location": "gharbia"}, intent="confirm_yes", action="finish", reply="تمام"), {"reply": "الغربية، صح كده؟"}), monkeypatch)
    assert not s.done and s.profile["location"] == "gharbia"


def test_local_yes_saves_us_when_llm_misses_intent(monkeypatch):
    s = conv.Session(id="t", stage="confirming", profile={"name": "فرحة", "location": "giza", "location_ar": "الجيزة", "current_crop": "wheat", "goal": "yield"})
    run(s, "ايوه مظبوط", FakeLLM(R(intent="info", action="confirm", reply="..."), {"reply": "تمام يا فرحة، هحلل أرضك."}), monkeypatch)
    assert s.done


def test_llm_failure_falls_back_to_rules_and_reports_error(monkeypatch):
    s = conv.Session(id="t")
    out = run(s, "اسمي فرحة", FakeLLM(vs.VoiceServiceError("LLM فشل (429)")), monkeypatch)
    assert out["engine"] == "rules" and "429" in out["llm_error"] and s.profile["name"] == "فرحة"


def test_garbage_llm_output_falls_back(monkeypatch):
    s = conv.Session(id="t")
    out = run(s, "اسمي فرحة", FakeLLM({"extracted": "oops", "reply": 5}), monkeypatch)
    assert out["engine"] in ("llm", "rules")   # مايقعش الحوار


def test_rules_mode_has_confirmation_too(offline):
    s = conv.Session(id="t", profile={"name": "فرحة", "location": "giza", "location_ar": "الجيزة", "current_crop": "wheat"})
    out = asyncio.run(conv.process_text(s, "الميه مش بتوصل لآخر الأرض"))
    assert s.stage == "confirming" and not s.done
    asyncio.run(conv.process_text(s, "لا، في المنوفية"))
    assert s.profile["location"] == "menoufia" and not s.done
    asyncio.run(conv.process_text(s, "ايوه"))
    assert s.done


def test_local_alias_beats_wrong_llm_guess(monkeypatch):
    # الـ LLM غلط وقال الجيزة لكن المزارع قال طنطا صراحة
    s = conv.Session(id="t", profile={"name": "فرحة"})
    run(s, "أنا من طنطا", FakeLLM(R({"location": "giza"}, action="ask_missing", reply="تمام، بتزرع إيه؟")), monkeypatch)
    assert s.profile["location"] == "gharbia"


def test_llm_trusted_when_text_has_two_governorates(monkeypatch):
    s = conv.Session(id="t", stage="confirming", profile={"name": "فرحة", "location": "giza", "location_ar": "الجيزة", "current_crop": "wheat", "goal": "yield"})
    run(s, "لا مش الجيزة، المنوفية", FakeLLM(R({"location": "menoufia"}, action="confirm")), monkeypatch)
    assert s.profile["location"] == "menoufia"


def test_retry_after_parsing():
    assert vs._retry_after("Please try again in 5.3325s.") == pytest.approx(5.63, abs=0.01)
    assert vs._retry_after("try again in 952.5ms") == pytest.approx(1.25, abs=0.01)
    assert vs._retry_after("no hint") == 3.0
    assert vs._retry_after("try again in 90s") == 8.0


def test_msa_reply_is_converted_to_egyptian(monkeypatch):
    s = conv.Session(id="t")
    out = run(s, "اسمي فرحة", FakeLLM(R({"name": "فرحة"}, reply="أفهم أنك تتحدث عن أرضك. ماذا تزرع الآن؟")), monkeypatch)
    assert "فهمت إنك" in out["reply"] and "بتتكلم" in out["reply"] and "إيه" in out["reply"] and "دلوقتي" in out["reply"]
    assert "تتحدث" not in out["reply"] and "الآن" not in out["reply"]


def test_prompt_contains_dialect_rules():
    g, c = conv._catalog()
    assert "طنطا" in g
    assert "__DIALECT__" not in conv.SYSTEM.replace("__DIALECT__", conv.DIALECT)
    assert "عامية مصرية" in conv.DIALECT and "ممنوع الفصحى" in conv.DIALECT


def test_tts_chain_falls_back_edge_then_browser(monkeypatch):
    from app.config import get_settings
    monkeypatch.setattr(get_settings(), "tts_provider", "auto")
    monkeypatch.setattr(vs, "api_enabled", lambda: False)

    async def edge_ok(text):
        return b"mp3"

    async def edge_bad(text):
        raise vs.VoiceServiceError("down")

    monkeypatch.setattr(vs, "synthesize_edge", edge_ok)
    assert asyncio.run(vs.speak("أهلا")) == (b"mp3", None)
    monkeypatch.setattr(vs, "synthesize_edge", edge_bad)
    audio, err = asyncio.run(vs.speak("أهلا"))
    assert audio is None and "down" in err


def test_clean_for_speech():
    assert vs.clean_for_speech("وفر ٣٠٪ هـ") == "وفر ٣٠ في المية هـ".replace("هـ", "ه")
