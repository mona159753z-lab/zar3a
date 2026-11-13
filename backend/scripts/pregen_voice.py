"""يولّد الجمل الثابتة بصوت VoiceTut-TTS المصري ويحفظها في app/data/voice_cache/.

التشغيل (من فولدر backend، والبيئة .venv مفعّلة، وسيرفر الصوت شغال على 8001):

    python scripts/pregen_voice.py --list                 # يعرض الجمل ومراحلها من غير توليد
    python scripts/pregen_voice.py --tier 1               # الأساسي: الترحيب والأسئلة (الأهم، ابدأي بيه)
    python scripts/pregen_voice.py --tier 2               # الأهداف + أشهر المحاصيل والمحافظات
    python scripts/pregen_voice.py --tier 3               # باقي المحاصيل والمحافظات
    python scripts/pregen_voice.py --names "فرحة,محمد"    # جمل بأسماء مزارعين العرض (مرحلة 4)
    python scripts/pregen_voice.py --profile "فرحة|menoufia|wheat|water_saving"   # جمل التأكيد لحالة عرض
    python scripts/pregen_voice.py --status               # بيقول إيه اتولّد وإيه لسه

السكريبت بيكمّل من حيث وقف (اللي اتولّد قبل كده بيتخطّاه) ويمكن إيقافه بـ Ctrl+C في أي وقت.
"""
import argparse
import io
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services import conversation as conv          # noqa: E402
from app.services import knowledge as kb                # noqa: E402
from app.services import voice_cache as vc              # noqa: E402

TOP_CROPS = ["wheat", "maize", "rice", "berseem", "cotton", "faba_bean", "onion", "tomato", "potato", "sugar_beet"]
TOP_GOVS = ["menoufia", "gharbia", "dakahlia", "sharqia", "beheira", "giza", "kafr_el_sheikh", "faiyum", "minya",
            "asyut", "qalyubia", "cairo", "alexandria"]
EXTRA_FIXED = ["تمام، إيه المعلومة اللي غلط؟", "قولي صح لو المعلومات تمام، أو قولي إيه اللي غلط."]


def phrases(names: list[str], profile: str | None) -> list[tuple[int, str]]:
    """(المرحلة، الجملة الكاملة) — الجملة الكاملة بتتقسّم لمقاطع بعدين."""
    out: list[tuple[int, str]] = []
    # مرحلة 1: الثابت
    out.append((1, conv.GREETING))
    out += [(1, t) for t in conv.QUESTIONS.values()]
    out += [(1, t) for t in conv.RETRY.values()]
    out.append((1, conv.NO_HEAR))
    out += [(1, t) for t in EXTRA_FIXED]
    # مرحلة 2/3: "X، تمام." (نفس الصيغة اللي في _process_rules)
    out += [(2, f"{kb.GOALS_AR[g]}، تمام.") for g in kb.GOALS_AR]
    for g in kb.governorates():
        out.append((2 if g["id"] in TOP_GOVS else 3, f"{g['name_ar']}، تمام."))
    for c in kb.crops():
        out.append((2 if c["id"] in TOP_CROPS else 3, f"{c['name_ar']}، تمام."))
    # مرحلة 4: أسماء العرض
    for n in names:
        out.append((4, f"أهلاً يا {n}."))
        out.append((4, f"تمام يا {n}، هحلل أرضك دلوقتي."))
    # مرحلة 5: جمل التأكيد لحالة عرض (الصيغ بتتعمل random فبنجمع كل الصيغ)
    if profile:
        name, loc, crop, goal = [x.strip() for x in profile.split("|")]
        g = next(x for x in kb.governorates() if x["id"] == loc)
        s = conv.Session(id="pregen", profile={"name": name, "location": loc, "location_ar": g["name_ar"],
                                               "current_crop": crop, "goal": goal})
        seen = {conv._confirm_text(s) for _ in range(60)}
        out += [(5, t) for t in sorted(seen)]
        out += [(4, f"أهلاً يا {name}."), (4, f"تمام يا {name}، هحلل أرضك دلوقتي.")]
    return out


def segments(plist: list[tuple[int, str]]) -> dict[str, tuple[int, str]]:
    """key → (مرحلة، نص المقطع). بنشيل التكرار."""
    segs: dict[str, tuple[int, str]] = {}
    for tier, full in plist:
        for seg in vc.split_segments(conv.vs.clean_for_speech(full)):
            k = vc.key_for(seg)
            if k not in segs or tier < segs[k][0]:
                segs[k] = (tier, seg)
    return segs


def synth(url: str, text: str, speaker: str, steps: int, timeout: float) -> tuple[bytes, str]:
    req = urllib.request.Request(
        url.rstrip("/") + "/tts",
        data=json.dumps({"text": text, "speaker": speaker, "num_step": steps}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get("X-Gen-Seconds", "?")


def to_pcm16_mono(wav_bytes: bytes) -> bytes:
    """بنوحّد كل الملفات على PCM 16-bit mono عشان الباك يركّبهم بمكتبة wave العادية."""
    import numpy as np
    import soundfile as sf
    data, rate = sf.read(io.BytesIO(wav_bytes), dtype="float32", always_2d=True)
    mono = np.clip(data.mean(axis=1), -1.0, 1.0)
    out = io.BytesIO()
    sf.write(out, mono, rate, format="WAV", subtype="PCM_16")
    return out.getvalue()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="http://127.0.0.1:8001")
    ap.add_argument("--tier", type=int, action="append", help="المرحلة (ممكن تتكرر). الافتراضي: 1")
    ap.add_argument("--names", default="", help="أسماء مفصولة بفاصلة")
    ap.add_argument("--profile", default=None, help="اسم|id المحافظة|id المحصول|id الهدف")
    ap.add_argument("--speaker", default="Yasmin")
    ap.add_argument("--steps", type=int, default=8, help="أقل = أسرع (8 مناسب)، 16 أعلى جودة")
    ap.add_argument("--timeout", type=float, default=1800)
    ap.add_argument("--limit", type=int, default=0, help="أقصى عدد مقاطع في التشغيلة دي")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--force", action="store_true", help="يعيد توليد الموجود")
    a = ap.parse_args()

    names = [n.strip() for n in a.names.split(",") if n.strip()]
    segs = segments(phrases(names, a.profile))
    man = vc.load_manifest().copy()
    have = {k for k in segs if k in man and (vc.CACHE_DIR / man[k]["file"]).exists()}

    if a.list or a.status:
        for t in sorted({v[0] for v in segs.values()}):
            items = [(k, s) for k, (tt, s) in segs.items() if tt == t]
            done = sum(1 for k, _ in items if k in have)
            print(f"\n=== المرحلة {t}: {done}/{len(items)} جاهز ===")
            if a.list:
                for k, s in items:
                    print(("  [x] " if k in have else "  [ ] ") + s)
        return

    tiers = set(a.tier or [1])
    todo = [(k, s) for k, (t, s) in segs.items() if t in tiers and (a.force or k not in have)]
    todo.sort(key=lambda x: (segs[x[0]][0], len(x[1])))
    if a.limit:
        todo = todo[: a.limit]
    print(f"هولّد {len(todo)} مقطع (المراحل {sorted(tiers)}) — steps={a.steps}, speaker={a.speaker}")
    if not todo:
        print("مفيش حاجة ناقصة في المراحل دي.")
        return

    vc.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    for i, (k, text) in enumerate(todo, 1):
        t0 = time.time()
        try:
            wav, gen = synth(a.url, text, a.speaker, a.steps, a.timeout)
            wav = to_pcm16_mono(wav)
        except (urllib.error.URLError, OSError) as e:
            print(f"\n✗ السيرفر مش بيرد ({e}). تأكدي إن uvicorn شغال على {a.url}، وشغّلي السكريبت تاني وهيكمّل.")
            sys.exit(1)
        except KeyboardInterrupt:
            raise
        fname = f"{k}.wav"
        (vc.CACHE_DIR / fname).write_bytes(wav)
        man[k] = {"text": text, "file": fname, "speaker": a.speaker, "steps": a.steps}
        tmp = vc.MANIFEST.with_suffix(".tmp")
        tmp.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(vc.MANIFEST)          # حفظ بعد كل مقطع: لو وقفتي في النص مفيش حاجة بتضيع
        spent = time.time() - t_start
        eta = spent / i * (len(todo) - i)
        print(f"[{i}/{len(todo)}] {time.time() - t0:5.0f}s  (server {gen}s)  باقي ~{eta / 60:.0f} دقيقة  | {text}", flush=True)
    print("\nخلصنا ✓")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nاتوقف. شغّليه تاني وهيكمّل من حيث وقف.")
