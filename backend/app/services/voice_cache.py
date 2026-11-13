"""كاش الصوت المصري المولّد مسبقًا (VoiceTut-TTS).

الفكرة: الرد بيتقسّم لمقاطع (جملة جملة)، ولو كل مقطع له ملف wav جاهز بنركّبهم ورا بعض ونرجّعهم فورًا.
لو ولا مقطع ناقص → بنرجّع None وسلسلة الـ TTS العادية (Edge ← المتصفح) بتكمل.
الملفات بيولّدها scripts/pregen_voice.py وبتتحفظ في data/voice_cache/ مع manifest.json.
"""
import hashlib
import io
import json
import logging
import re
import wave
from pathlib import Path

log = logging.getLogger("zar3a.voice_cache")

CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "voice_cache"
MANIFEST = CACHE_DIR / "manifest.json"
GAP_SECONDS = 0.15   # سكتة بين المقاطع

_DIAC = re.compile(r"[\u064B-\u0652\u0640]")
_SPLIT = re.compile(r"(?<=[.؟!?])\s+")

_manifest: dict = {}
_manifest_mtime: float = -1.0


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", _DIAC.sub("", text or "")).strip()


def key_for(segment: str) -> str:
    return hashlib.sha1(normalize(segment).encode("utf-8")).hexdigest()[:16]


def split_segments(text: str) -> list[str]:
    """تقسيم الرد لجمل. نفس الدالة بيستخدمها سكريبت التوليد عشان المفاتيح تتطابق."""
    return [p.strip() for p in _SPLIT.split(normalize(text)) if p.strip()]


def load_manifest() -> dict:
    """بيعيد القراءة تلقائيًا لو الملف اتغيّر (يعني تقدري تولّدي وإنتي السيرفر شغال)."""
    global _manifest, _manifest_mtime
    try:
        mtime = MANIFEST.stat().st_mtime
    except OSError:
        _manifest, _manifest_mtime = {}, -1.0
        return _manifest
    if mtime != _manifest_mtime:
        try:
            _manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
            _manifest_mtime = mtime
        except ValueError:
            log.warning("voice_cache manifest تالف")
            _manifest = {}
    return _manifest


def _read(path: Path) -> tuple[tuple, bytes] | None:
    try:
        with wave.open(str(path), "rb") as w:
            return (w.getnchannels(), w.getsampwidth(), w.getframerate()), w.readframes(w.getnframes())
    except (OSError, wave.Error, EOFError):
        return None


def lookup(text: str) -> bytes | None:
    """wav كامل للنص لو كل مقاطعه متخزّنة، غير كده None."""
    man = load_manifest()
    if not man:
        return None
    segs = split_segments(text)
    if not segs:
        return None
    parts = []
    for seg in segs:
        entry = man.get(key_for(seg))
        if not entry:
            return None
        got = _read(CACHE_DIR / entry["file"])
        if not got:
            return None
        parts.append(got)
    params = parts[0][0]
    if any(p[0] != params for p in parts):
        log.warning("voice_cache: ملفات بمواصفات مختلفة، تجاهل الكاش")
        return None
    ch, width, rate = params
    gap = b"\x00" * (int(rate * GAP_SECONDS) * ch * width)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(width)
        w.setframerate(rate)
        for i, (_, frames) in enumerate(parts):
            if i:
                w.writeframes(gap)
            w.writeframes(frames)
    return buf.getvalue()
