from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Voice providers (OpenAI-compatible endpoints) ---
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    stt_model: str = "gpt-4o-transcribe"      # أو whisper-1
    llm_model: str = "gpt-4o-mini"
    tts_model: str = "gpt-4o-mini-tts"        # أو tts-1
    tts_voice: str = "alloy"
    # مصدر الصوت: auto (OpenAI لو متاح، وبعدين Edge، وبعدين المتصفح) | edge | openai | browser
    tts_provider: str = "auto"
    edge_voice: str = "ar-EG-SalmaNeural"     # مصري. الراجل: ar-EG-ShakirNeural
    edge_rate: str = "-5%"                    # أبطأ شوية عشان الوضوح
    # --- موديل صوت مصري من Hugging Face (سيرفر منفصل: hf_voice_server/server.py) ---
    hf_tts_url: str = ""                      # مثال: http://127.0.0.1:8001  (فاضي = مش مستخدم)
    hf_tts_speaker: str = "Yasmin"            # Yasmin ست | Mohammed, Ahmed رجالة
    hf_tts_steps: int = 16                    # أقل = أسرع (على CPU جرّب 8 إلى 16)
    hf_tts_timeout: float = 25.0              # لو عدّى الوقت ده نرجع لـ Edge
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_fallback_model: str = ""              # موديل تاني على نفس المزوّد يُستخدم لو الأول رجّع 429 (لكل موديل حد مستقل)
    stt_language: str = "ar"
    voice_mode: str = "auto"                  # auto | api | browser  (auto = api لو فيه مفتاح، غير كده صوت المتصفح)
    max_audio_mb: int = 10
    session_ttl_seconds: int = 31536000  # سنة كاملة

    # --- App ---
    database_url: str = "sqlite:///./zar3a.db"
    cors_origins: str = "*"                   # مثال: https://zar3a.vercel.app,http://localhost:5173

    # --- NASA ---
    nasa_timeout: float = 20.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
