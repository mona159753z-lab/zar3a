import base64

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session as DbSession

from ..config import get_settings
from ..database.connection import get_db
from ..database.models import AnalysisRecord
from ..schemas.field import FieldCreate, VoiceSpeak, VoiceTextTurn
from ..services import analysis_service, conversation as conv, field_service
from ..services import knowledge as kb
from ..services import voice_service as vs

router = APIRouter(prefix="/api/voice", tags=["voice"])


async def _speak(text: str) -> dict:
    """نطق الرد: صوت مصري من الباك لو متاح، ولو فشل الواجهة بتنطق بصوت المتصفح كبديل."""
    audio, err = await vs.speak(text)
    if audio:
        return {"audio_base64": base64.b64encode(audio).decode(), "audio_mime": "audio/wav" if audio[:4] == b"RIFF" else "audio/mpeg", "tts_error": None,
                "speak_in_browser": False}
    return {"audio_base64": None, "audio_mime": None, "tts_error": err, "speak_in_browser": True}


def _state(s: conv.Session) -> dict:
    return {"session_id": s.id, "profile": s.profile, "missing": s.missing, "done": s.done}


async def _handle(s: conv.Session, transcript: str) -> dict:
    if not transcript.strip():
        return {**_state(s), "transcript": "", "reply_text": conv.NO_HEAR, **await _speak(conv.NO_HEAR)}
    try:
        out = await conv.process_text(s, transcript)
    except vs.VoiceServiceError as e:
        raise HTTPException(e.status_code, e.message) from e
    extra = {k: out[k] for k in ("engine", "llm_error", "intent", "action", "regenerated") if k in out}
    return {**_state(s), "transcript": transcript, "reply_text": out["reply"], **extra, **await _speak(out["reply"])}


@router.post("/start")
async def start():
    s, greeting = conv.start()
    return {**_state(s), "reply_text": greeting, **await _speak(greeting)}


@router.post("/turn")
async def turn(audio: UploadFile = File(...), session_id: str | None = Form(None)):
    if not vs.api_enabled():
        raise HTTPException(400, "الوضع الحالي بيستخدم صوت المتصفح؛ ابعت النص على /api/voice/text-turn")
    data = await audio.read()
    if len(data) > get_settings().max_audio_mb * 1024 * 1024:
        raise HTTPException(413, "التسجيل كبير أوي")
    if len(data) < 500:
        raise HTTPException(400, "التسجيل فاضي")
    s = conv.get_session(session_id)
    try:
        transcript = await vs.transcribe(data, audio.content_type or "audio/webm")
    except vs.VoiceServiceError as e:
        raise HTTPException(e.status_code, e.message) from e
    return await _handle(s, transcript)


@router.post("/text-turn")
async def text_turn(body: VoiceTextTurn):
    """بديل بدون ميكروفون (أزرار/كتابة) — نفس المنطق."""
    return await _handle(conv.get_session(body.session_id), body.text)


@router.get("/llm-check")
async def llm_check():
    """تشخيص سريع: هل الـ LLM شغال فعلًا، وإيه آخر خطأ لو فيه."""
    s = get_settings()
    info = {"llm_enabled": vs.llm_enabled(), "model": s.llm_model, "base_url": s.llm_base_url or s.openai_base_url,
            "last_error": vs.last_error}
    if not info["llm_enabled"]:
        return {**info, "ok": False, "error": "مفيش مفتاح LLM"}
    try:
        out = await vs.chat_json([{"role": "system", "content": 'رد بـ JSON فقط: {"ok": true}'}, {"role": "user", "content": "اختبار"}])
        return {**info, "ok": True, "sample": out}
    except vs.VoiceServiceError as e:
        return {**info, "ok": False, "error": e.message}


@router.get("/tts-check")
async def tts_check():
    """تشخيص الصوت: بيرجع حجم الصوت المصري أو سبب الفشل."""
    s = get_settings()
    audio, err = await vs.speak("أهلاً يا فرحة، أنا زرعة")
    return {"provider": s.tts_provider, "edge_voice": s.edge_voice, "ok": bool(audio), "bytes": len(audio or b""), "error": err}


@router.post("/tts")
async def tts(body: VoiceSpeak):
    return {"text": body.text, **await _speak(body.text)}


@router.get("/session/{session_id}")
def session_state(session_id: str):
    s = conv.find_session(session_id)
    if not s:
        raise HTTPException(404, "الجلسة مش موجودة أو انتهت")
    return _state(s)


@router.post("/session/{session_id}/analyze")
async def analyze(session_id: str, speak: bool = False, db: DbSession = Depends(get_db)):
    """بعد ما done=true: يعمل الأرض ويشغّل التحليل ويرجّع النتيجة (+ صوت الملخص لو speak=true)."""
    s = conv.find_session(session_id)
    if not s:
        raise HTTPException(404, "الجلسة مش موجودة أو انتهت")
    if not s.done:
        raise HTTPException(409, f"لسه ناقص: {', '.join(s.missing)}")
    payload = FieldCreate(farmer_name=s.profile["name"], region=s.profile["location_ar"],
                          current_crop=s.profile["current_crop"], goal=s.profile["goal"])
    rec = field_service.save(db, field_service.resolve(payload))
    result = await analysis_service.run_analysis(field_service.to_profile(rec))
    db.add(AnalysisRecord(id=result["analysis_id"], field_id=rec.id, status="completed", result=result))
    db.commit()
    out = {"field_id": rec.id, "analysis": result}
    if speak:
        out["speech"] = await _speak(result["spoken_summary_ar"])
    return out
