"""اختبارات الفهم المحلي (من غير إنترنت ولا مفاتيح)."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import nlu_local as nlu


@pytest.mark.parametrize("text,goal", [
    ("الميه مش بتوصل لآخر الأرض", "water_saving"),
    ("عايز أقلل الري", "water_saving"),
    ("الأرض تعبت أوي", "soil_health"),
    ("عايز أكسب أكتر من الفدان", "yield"),
    ("الجو حر أوي والزرع بيتحرق", "climate_resilience"),
])
def test_goal_free_phrasing(text, goal):
    assert nlu.classify_goal(text) == goal


@pytest.mark.parametrize("text", ["مش عارف", "كام الساعة", "ممكن تعيد"])
def test_goal_unrelated_returns_none(text):
    assert nlu.classify_goal(text) is None


def test_fuzzy_governorate_and_crop():
    assert nlu.find_governorate("منوفيا", fuzzy=True)["id"] == "menoufia"
    assert nlu.find_governorate("منوفيا", fuzzy=False) is None
    assert nlu.find_crop("قمحه", fuzzy=True) == "wheat"


def test_fuzzy_does_not_misread_names():
    for name in ["محمد", "مروة", "كريم", "ريم", "فرحة"]:
        assert nlu.find_governorate(name, fuzzy=True) is None
        assert nlu.find_crop(name, fuzzy=True) is None


def test_full_dialog_without_keys(offline):
    with TestClient(app) as c:
        sid = c.post("/api/voice/start").json()["session_id"]
        turn = lambda t: c.post("/api/voice/text-turn", json={"session_id": sid, "text": t}).json()
        assert turn("اسمي فرحة")["profile"]["name"] == "فرحة"
        assert turn("في منوفيا")["profile"]["location"] == "menoufia"
        assert turn("بزرع قمحه")["profile"]["current_crop"] == "wheat"
        r = turn("الميه مش بتوصل لآخر الأرض")
        assert r["profile"]["goal"] == "water_saving" and not r["done"]   # بيطلب تأكيد الأول
        assert turn("ايوه صح")["done"]