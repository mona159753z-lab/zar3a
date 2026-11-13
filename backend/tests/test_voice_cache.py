import io
import json
import wave

from app.services import voice_cache as vc


def _wav(path, seconds=0.5, rate=24000):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(b"\x01\x00" * int(rate * seconds))


def _seed(tmp_path, monkeypatch, texts):
    man = {}
    for i, t in enumerate(texts):
        f = f"{i}.wav"
        _wav(tmp_path / f)
        man[vc.key_for(t)] = {"text": t, "file": f}
    (tmp_path / "manifest.json").write_text(json.dumps(man, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(vc, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(vc, "MANIFEST", tmp_path / "manifest.json")
    monkeypatch.setattr(vc, "_manifest_mtime", -1.0)


def test_split_segments():
    assert vc.split_segments("المنوفية، تمام. بتزرع إيه؟") == ["المنوفية، تمام.", "بتزرع إيه؟"]


def test_lookup_joins_cached_segments(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch, ["المنوفية، تمام.", "بتزرع إيه؟"])
    audio = vc.lookup("المنوفية، تمام. بتزرع إيه؟")
    assert audio and audio[:4] == b"RIFF"
    w = wave.open(io.BytesIO(audio))
    assert w.getnframes() / w.getframerate() > 1.0   # نص ثانية × 2 + سكتة


def test_lookup_misses_when_any_segment_missing(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch, ["بتزرع إيه؟"])
    assert vc.lookup("أهلاً يا سعدية. بتزرع إيه؟") is None
    assert vc.lookup("") is None


def test_lookup_without_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(vc, "MANIFEST", tmp_path / "nope.json")
    monkeypatch.setattr(vc, "_manifest_mtime", -1.0)
    assert vc.lookup("أي حاجة") is None
