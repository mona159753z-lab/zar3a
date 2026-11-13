"""fixture لتشغيل اختبار أوفلاين حتى لو فيه مفاتيح في .env."""
import pytest

from app.config import get_settings

from app.services import voice_service as vs


@pytest.fixture
def offline(monkeypatch):
    monkeypatch.setattr(vs, "llm_enabled", lambda: False)
    monkeypatch.setattr(vs, "api_enabled", lambda: False)
    monkeypatch.setattr(get_settings(), "tts_provider", "browser")
