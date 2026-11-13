import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.services import knowledge as kb
from app.services import nasa_service
from app.services import voice_service as vs


@pytest.fixture(autouse=True)
def offline_nasa(monkeypatch):
    async def boom(lat, lon):
        raise RuntimeError("offline")
    monkeypatch.setattr(nasa_service, "fetch_power", boom)
    nasa_service._memory.clear()
    monkeypatch.setattr(nasa_service, "CACHE_DIR", nasa_service.CACHE_DIR / "_nonexistent")


@pytest.fixture
def api_mode(monkeypatch):
    monkeypatch.setattr(get_settings(), "voice_mode", "api")
    monkeypatch.setattr(get_settings(), "tts_provider", "openai")


@pytest.fixture
def browser_mode(monkeypatch):
    monkeypatch.setattr(get_settings(), "voice_mode", "browser")
    monkeypatch.setattr(get_settings(), "tts_provider", "browser")
    monkeypatch.setattr(vs, "llm_enabled", lambda: False)   # اختبار الفهم المحلي أوفلاين حتى لو فيه مفاتيح


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_matching():
    assert kb.resolve_governorate("أرضي في المنوفية")["id"] == "menoufia"
    assert kb.resolve_governorate("بالمنوفيه")["id"] == "menoufia"
    assert kb.resolve_governorate("الإسكندرية")["id"] == "alexandria"
    assert kb.match_crop("بازرع القمح") == "wheat"
    assert kb.match_crop("ذرة رفيعة") == "sorghum"
    assert kb.match_crop("ذرة شامية") == "maize"
    assert kb.match_crop("فول سوداني") == "peanut"
    assert kb.match_crop("فول") == "faba_bean"
    assert kb.match_goal("عايز أوفر المياه") == "water_saving"
    assert kb.match_goal("تحسين التربة") == "soil_health"


def test_quick_analysis(client):
    r = client.post("/api/quick-analysis", json={"farmer_name": "محمد", "region": "المنوفية", "current_crop": "قمح", "goal": "water_saving"})
    assert r.status_code == 200, r.text
    j = r.json()
    ids = [s["scenario_id"] for s in j["scenarios"]]
    assert ids == ["A", "B", "C"]
    assert j["data_status"]["nasa_data_available"] is False
    seqs = [tuple(c["crop_id"] for c in s["crops"]) for s in j["scenarios"]]
    assert len(set(seqs)) == 3
    for s in j["scenarios"]:
        assert s["risks"] and s["limitations"]
        assert len(s["crops"]) == 3
    assert j["spoken_summary_ar"]


def test_constraints_hold(client):
    j = client.post("/api/quick-analysis", json={"region": "الغربية", "current_crop": "potato", "goal": "soil_health",
                                                 "water_availability": "low"}).json()
    for s in j["scenarios"][1:]:
        ids = ["potato"] + [c["crop_id"] for c in s["crops"]]
        fams = [kb.crops_by_id()[i]["family"] for i in ids]
        assert all(a != b or a not in kb.rules()["hard_no_consecutive_family"] for a, b in zip(fams, fams[1:]))
        assert "rice" not in ids


def test_field_flow(client):
    f = client.post("/api/fields", json={"region": "الدقهلية", "current_crop": "ذرة شامية", "goal": "yield"}).json()
    a = client.post(f"/api/analysis/{f['id']}").json()
    assert client.get(f"/api/analysis/{a['analysis_id']}/scenarios").status_code == 200
    assert client.get(f"/api/analysis/{a['analysis_id']}/scenarios/b/explanation").json()["benefits"]
    assert client.get(f"/api/environment/{f['id']}").status_code == 200


def test_bad_inputs(client):
    assert client.post("/api/fields", json={"current_crop": "قمح"}).status_code == 422
    assert client.post("/api/fields", json={"region": "المنوفية", "current_crop": "شيء غريب"}).status_code == 422


def test_voice_flow(client, monkeypatch, api_mode):
    replies = iter([
        {"extracted": {"name": "محمد", "location": None, "current_crop": None, "goal": None}, "action": "ask_missing", "reply": "أهلاً يا محمد. أرضك في أنهي محافظة؟"},
        {"extracted": {"name": None, "location": "المنوفية", "current_crop": "القمح", "goal": None}, "action": "ask_missing", "reply": "المنوفية والقمح، تمام. إيه هدفك؟"},
        {"extracted": {"name": None, "location": None, "current_crop": None, "goal": "توفير المياه"}, "action": "confirm", "reply": "يعني المنوفية والقمح وتوفير المياه، صح؟"},
        {"extracted": {}, "intent": "confirm_yes", "action": "finish", "reply": "تمام يا محمد، هحلل أرضك دلوقتي."},
    ])

    async def fake_chat(messages, temperature=0.3):
        return next(replies)

    async def fake_tts(text):
        return b"ID3fake-mp3"

    async def fake_stt(audio, ct="audio/webm"):
        return "كلام"

    monkeypatch.setattr(vs, "chat_json", fake_chat)
    monkeypatch.setattr(vs, "synthesize", fake_tts)
    monkeypatch.setattr(vs, "transcribe", fake_stt)

    st = client.post("/api/voice/start").json()
    sid = st["session_id"]
    assert st["audio_base64"] and not st["done"]
    r1 = client.post("/api/voice/text-turn", json={"session_id": sid, "text": "اسمي محمد"}).json()
    assert r1["profile"]["name"] == "محمد"
    r2 = client.post("/api/voice/turn", data={"session_id": sid}, files={"audio": ("a.webm", b"x" * 2000, "audio/webm")}).json()
    assert r2["profile"]["location"] == "menoufia" and r2["profile"]["current_crop"] == "wheat"
    assert client.post(f"/api/voice/session/{sid}/analyze").status_code == 409
    r3 = client.post("/api/voice/text-turn", json={"session_id": sid, "text": "توفير المياه"}).json()
    assert r3["done"] is False and r3["profile"]["goal"] == "water_saving"   # لازم تأكيد الأول
    r4 = client.post("/api/voice/text-turn", json={"session_id": sid, "text": "ايوه صح"}).json()
    assert r4["done"] is True
    out = client.post(f"/api/voice/session/{sid}/analyze?speak=true").json()
    assert len(out["analysis"]["scenarios"]) == 3 and out["speech"]["audio_base64"]


def test_voice_unrecognized_location(client, monkeypatch, api_mode):
    async def fake_chat(messages, temperature=0.3):
        return {"extracted": {"location": "المريخ"}, "action": "clarify", "reply": "ما عرفتش المحافظة، قولها تاني."}

    async def fake_tts(text):
        raise vs.VoiceServiceError("tts down")

    monkeypatch.setattr(vs, "chat_json", fake_chat)
    monkeypatch.setattr(vs, "synthesize", fake_tts)
    sid = client.post("/api/voice/start").json()["session_id"]
    r = client.post("/api/voice/text-turn", json={"session_id": sid, "text": "المريخ"}).json()
    assert "المحافظة" in r["reply_text"] and r["audio_base64"] is None and r["tts_error"]


def test_voice_no_key(client, api_mode):
    r = client.post("/api/voice/turn", files={"audio": ("a.webm", b"x" * 2000, "audio/webm")})
    assert r.status_code == 503


def test_browser_mode_step_by_step(client, browser_mode):
    st = client.post("/api/voice/start").json()
    sid = st["session_id"]
    assert st["speak_in_browser"] and st["audio_base64"] is None
    r = client.post("/api/voice/text-turn", json={"session_id": sid, "text": "السلام عليكم انا محمد"}).json()
    assert r["profile"]["name"] == "محمد" and "محافظة" in r["reply_text"]
    r = client.post("/api/voice/text-turn", json={"session_id": sid, "text": "في المنوفية"}).json()
    assert r["profile"]["location"] == "menoufia"
    r = client.post("/api/voice/text-turn", json={"session_id": sid, "text": "بزرع القمح"}).json()
    assert r["profile"]["current_crop"] == "wheat" and not r["done"]
    r = client.post("/api/voice/text-turn", json={"session_id": sid, "text": "عايز أوفر المياه"}).json()
    assert not r["done"] and r["profile"]["goal"] == "water_saving"
    assert client.post("/api/voice/text-turn", json={"session_id": sid, "text": "ايوه صح"}).json()["done"]
    out = client.post(f"/api/voice/session/{sid}/analyze?speak=true").json()
    assert len(out["analysis"]["scenarios"]) == 3 and out["speech"]["speak_in_browser"]


def test_browser_mode_all_in_one_and_retry(client, browser_mode):
    sid = client.post("/api/voice/start").json()["session_id"]
    r = client.post("/api/voice/text-turn", json={"session_id": sid, "text": "انا محمد من المنوفية بزرع قمح وعايز اوفر المياه"}).json()
    assert not r["done"] and r["profile"]["name"] == "محمد"
    assert client.post("/api/voice/text-turn", json={"session_id": sid, "text": "تمام"}).json()["done"]
    sid2 = client.post("/api/voice/start").json()["session_id"]
    r = client.post("/api/voice/text-turn", json={"session_id": sid2, "text": "اسمي منى"}).json()
    r = client.post("/api/voice/text-turn", json={"session_id": sid2, "text": "في المريخ"}).json()
    assert "المحافظة" in r["reply_text"] and "location" in r["missing"]
    # كلمة "أرض" مش لازم تتفهم كهدف
    r = client.post("/api/voice/text-turn", json={"session_id": sid2, "text": "أرضي في الغربية والمحصول قمح"}).json()
    assert r["profile"].get("goal") is None and r["profile"]["location"] == "gharbia"


def test_browser_mode_rejects_audio_and_health(client, browser_mode):
    assert client.post("/api/voice/turn", files={"audio": ("a.webm", b"x" * 2000, "audio/webm")}).status_code == 400
    assert client.get("/health").json()["voice_mode"] == "browser"


def test_demo_page(client):
    r = client.get("/demo/")
    assert r.status_code == 200 and "زرعة" in r.text
    assert client.get("/demo/browserVoice.js").status_code == 200


def test_browser_mode_yield_goal_when_asked(client, browser_mode):
    sid = client.post("/api/voice/start").json()["session_id"]
    client.post("/api/voice/text-turn", json={"session_id": sid, "text": "اسمي منى من الغربية بزرع قمح"})
    r = client.post("/api/voice/text-turn", json={"session_id": sid, "text": "عايزة أحسن المحصول"}).json()
    assert not r["done"] and r["profile"]["goal"] == "yield"
    assert client.post("/api/voice/text-turn", json={"session_id": sid, "text": "ايوه"}).json()["done"]


def test_hf_tts_falls_back_to_edge_when_server_down(monkeypatch):
    """لو سيرفر الصوت المصري وقع، الحوار مش بيقف: بنجرّب Edge بعده."""
    import asyncio
    from app.config import get_settings
    from app.services import voice_service as vs
    s = get_settings()
    monkeypatch.setattr(s, "tts_provider", "hf")
    monkeypatch.setattr(s, "hf_tts_url", "http://127.0.0.1:9")   # بورت مقفول
    async def fake_edge(text): return b"EDGE"
    monkeypatch.setattr(vs, "synthesize_edge", fake_edge)
    audio, err = asyncio.run(vs.speak("أهلا"))
    assert audio == b"EDGE" and err is None
