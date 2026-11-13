"""سيرفر الصوت المصري (VoiceTut-TTS من Hugging Face). بيشتغل لوحده على بورت 8001 والباك الرئيسي بيكلمه.
التشغيل (من فولدر backend، وبيئة منفصلة أحسن):
    pip install -r hf_voice_server/requirements.txt
    uvicorn hf_voice_server.server:app --port 8001
أول تشغيل بينزّل الموديل من هاجينج فيس (كام جيجا) فخده وقت.
"""
import asyncio
import os
import tempfile
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import Response

MODEL_ID = os.getenv("HF_TTS_MODEL", "mohammedaly22/VoiceTut-TTS")
app = FastAPI(title="ZAR3A Egyptian TTS")
_tts = None
_lock = asyncio.Lock()   # الموديل بيتنفذ طلب واحد في المرة


class TTSIn(BaseModel):
    text: str = Field(min_length=1, max_length=600)
    speaker: str = "Yasmin"
    num_step: int = Field(16, ge=4, le=64)
    speed: float = Field(1.0, ge=0.7, le=1.3)


@app.on_event("startup")
def load():
    global _tts
    from voicetut_tts import VoiceTutTTS
    t0 = time.time()
    _tts = VoiceTutTTS.from_pretrained(MODEL_ID)
    print(f"model loaded in {time.time() - t0:.1f}s")


def _run(body: TTSIn) -> bytes:
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "out.wav")
        _tts.synthesize(body.text, speaker=body.speaker, num_step=body.num_step, speed=body.speed, output=out)
        with open(out, "rb") as f:
            return f.read()


@app.get("/health")
def health():
    return {"ok": _tts is not None, "model": MODEL_ID}


@app.post("/tts")
async def tts(body: TTSIn):
    if _tts is None:
        raise HTTPException(503, "الموديل لسه بيتحمّل")
    async with _lock:
        t0 = time.time()
        wav = await asyncio.to_thread(_run, body)
    return Response(wav, media_type="audio/wav", headers={"X-Gen-Seconds": f"{time.time() - t0:.2f}"})
