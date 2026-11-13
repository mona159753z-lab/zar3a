"""STT + LLM + TTS عن طريق APIs متوافقة مع OpenAI. غيّر المزوّد من .env (OPENAI_BASE_URL والموديلات)."""
import asyncio
import json
import logging
import re

import httpx

from ..config import get_settings

_EXT = {"webm": "webm", "mp4": "mp4", "m4a": "m4a", "ogg": "ogg", "wav": "wav", "wave": "wav",
        "mpeg": "mp3", "mp3": "mp3", "x-m4a": "m4a", "aac": "m4a"}

STT_PROMPT = "حوار بالعامية المصرية مع مزارع. أسماء محافظات ومحاصيل مصرية: المنوفية، الغربية، الدقهلية، قمح، ذرة، برسيم، أرز، قطن، فول، بصل، طماطم."
TTS_INSTRUCTIONS = "تكلم بالعربية بلهجة مصرية دافئة وهادئة، بسرعة معتدلة ووضوح، كأنك بتكلم مزارع."

last_error: str | None = None   # آخر خطأ من الـ LLM (للتشخيص)
log = logging.getLogger("zar3a.voice")


def llm_enabled() -> bool:
    s = get_settings()
    return api_enabled() or bool(s.llm_api_key or s.openai_api_key)

def api_enabled() -> bool:
    s = get_settings()
    return s.voice_mode == "api" or (s.voice_mode == "auto" and bool(s.openai_api_key))


class VoiceServiceError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _headers() -> dict:
    s = get_settings()
    if not s.openai_api_key:
        raise VoiceServiceError("OPENAI_API_KEY مش متظبط في ملف .env", 503)
    return {"Authorization": f"Bearer {s.openai_api_key}"}


def _raise_http(resp: httpx.Response, what: str) -> None:
    if resp.status_code >= 400:
        raise VoiceServiceError(f"{what} فشل ({resp.status_code}): {resp.text[:300]}", 502)


async def transcribe(audio: bytes, content_type: str = "audio/webm") -> str:
    s = get_settings()
    sub = content_type.split(";")[0].split("/")[-1].strip().lower()
    filename = f"audio.{_EXT.get(sub, 'webm')}"
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            r = await client.post(
                f"{s.openai_base_url}/audio/transcriptions", headers=_headers(),
                files={"file": (filename, audio, content_type.split(";")[0] or "audio/webm")},
                data={"model": s.stt_model, "language": s.stt_language, "prompt": STT_PROMPT},
            )
        except httpx.HTTPError as e:
            raise VoiceServiceError(f"تعذر الاتصال بخدمة STT: {e}") from e
    _raise_http(r, "STT")
    return (r.json().get("text") or "").strip()


def _extract_json(text: str) -> dict:
    text = (text or "").strip()
    try:
        return json.loads(text)
    except ValueError:
        a, b = text.find("{"), text.rfind("}")
        if a != -1 and b > a:
            return json.loads(text[a:b + 1])
        raise


def _retry_after(text: str) -> float:
    """بيقرا 'try again in 5.33s' أو '952ms' من رسالة 429، ويرجع ثواني الانتظار (بحد أقصى 8)."""
    m = re.search(r"in\s+([\d.]+)\s*(ms|s)", text or "")
    if not m:
        return 3.0
    sec = float(m.group(1)) / (1000 if m.group(2) == "ms" else 1)
    return min(sec + 0.3, 8.0)


async def chat_json(messages: list[dict], temperature: float = 0.3) -> dict:
    s = get_settings()
    key = s.llm_api_key or s.openai_api_key
    if not key:
        raise VoiceServiceError("مفيش مفتاح LLM في ملف .env", 503)
    base = (s.llm_base_url or s.openai_base_url).rstrip("/")
    headers = {"Authorization": f"Bearer {key}"}
    models = [s.llm_model] + ([s.llm_fallback_model] if s.llm_fallback_model and s.llm_fallback_model != s.llm_model else [])

    async def call(client, model):
        body = {"model": model, "messages": messages, "temperature": temperature}
        if "gpt-oss" in model:
            body["reasoning_effort"] = "low"   # أسرع بكتير في الحوار الصوتي
        r = await client.post(f"{base}/chat/completions", headers=headers, json={**body, "response_format": {"type": "json_object"}})
        if r.status_code == 400:   # بعض الوسطاء مبيدعموش response_format
            r = await client.post(f"{base}/chat/completions", headers=headers, json=body)
        return r

    async with httpx.AsyncClient(timeout=45) as client:
        try:
            r = None
            for attempt in range(2):
                for m in models:           # لو 429 على الموديل الأساسي نجرب الاحتياطي فورًا
                    r = await call(client, m)
                    if r.status_code != 429:
                        break
                if r.status_code != 429 or attempt == 1:
                    break
                log.warning("LLM 429 على كل الموديلات، هستنى وأعيد: %s", r.text[:120])
                await asyncio.sleep(_retry_after(r.text))
        except httpx.HTTPError as e:
            raise VoiceServiceError(f"تعذر الاتصال بخدمة LLM: {e}") from e
    _raise_http(r, "LLM")
    try:
        return _extract_json(r.json()["choices"][0]["message"]["content"])
    except (KeyError, ValueError, IndexError, TypeError) as e:
        raise VoiceServiceError("رد الـ LLM مش JSON صالح") from e


async def synthesize(text: str) -> bytes:
    s = get_settings()
    body = {"model": s.tts_model, "voice": s.tts_voice, "input": text, "response_format": "mp3"}
    if "gpt-4o" in s.tts_model:
        body["instructions"] = TTS_INSTRUCTIONS
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            r = await client.post(f"{s.openai_base_url}/audio/speech", headers=_headers(), json=body)
        except httpx.HTTPError as e:
            raise VoiceServiceError(f"تعذر الاتصال بخدمة TTS: {e}") from e
    _raise_http(r, "TTS")
    return r.content


# ---------------- صوت مصري عصبي (Microsoft Edge TTS، من غير مفتاح) ----------------
def edge_available() -> bool:
    import importlib.util
    return importlib.util.find_spec("edge_tts") is not None


async def synthesize_edge(text: str) -> bytes:
    s = get_settings()
    try:
        import edge_tts
    except ImportError as e:
        raise VoiceServiceError("مكتبة edge-tts مش متسطبة (pip install edge-tts)") from e
    audio = bytearray()
    try:
        async for chunk in edge_tts.Communicate(text, s.edge_voice, rate=s.edge_rate).stream():
            if chunk["type"] == "audio":
                audio += chunk["data"]
    except Exception as e:   # شبكة أو تغيير في الخدمة
        raise VoiceServiceError(f"Edge TTS فشل: {e}") from e
    if not audio:
        raise VoiceServiceError("Edge TTS رجّع صوت فاضي")
    return bytes(audio)


# ---------------- موديل HF مصري (VoiceTut-TTS) عن طريق سيرفر محلي ----------------
async def synthesize_hf(text: str) -> bytes:
    s = get_settings()
    if not s.hf_tts_url:
        raise VoiceServiceError("HF_TTS_URL مش متظبط في .env", 503)
    body = {"text": text, "speaker": s.hf_tts_speaker, "num_step": s.hf_tts_steps}
    async with httpx.AsyncClient(timeout=s.hf_tts_timeout) as client:
        try:
            r = await client.post(f"{s.hf_tts_url.rstrip('/')}/tts", json=body)
        except httpx.HTTPError as e:
            raise VoiceServiceError(f"سيرفر الصوت المصري مش متاح: {type(e).__name__}") from e
    _raise_http(r, "HF TTS")
    if not r.content:
        raise VoiceServiceError("سيرفر الصوت المصري رجّع صوت فاضي")
    return r.content


def clean_for_speech(text: str) -> str:
    return re.sub(r"\s{2,}", " ", text.replace("ـ", "").replace("٪", " في المية")).strip()


async def speak(text: str) -> tuple[bytes | None, str | None]:
    """بيجرّب مصادر الصوت بالترتيب حسب TTS_PROVIDER. بيرجع (audio, error). audio=None يعني الواجهة تنطق بصوت المتصفح."""
    s = get_settings()
    text = clean_for_speech(text)
    prov = (s.tts_provider or "auto").lower()
    chain = {"browser": [], "openai": ["openai"], "edge": ["edge"], "hf": ["hf", "edge"]}.get(
        prov, (["hf"] if s.hf_tts_url else []) + (["openai"] if api_enabled() else []) + ["edge"])
    err = None
    for name in chain:
        try:
            fn = {"openai": synthesize, "edge": synthesize_edge, "hf": synthesize_hf}[name]
            return await fn(text), None
        except VoiceServiceError as e:
            err = e.message
            log.warning("TTS %s failed: %s", name, e.message)
    return None, err
