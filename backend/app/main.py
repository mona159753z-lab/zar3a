from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles

from .api import analysis, crops, environment, fields, voice
from .config import get_settings
from .database.connection import init_db
from .services.voice_service import api_enabled


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="ZAR3A API", version="0.1.0", lifespan=lifespan)

_origins = [o.strip() for o in get_settings().cors_origins.split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=_origins, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

for r in (crops.router, fields.router, environment.router, analysis.router, voice.router):
    app.include_router(r)


@app.get("/health", tags=["system"])
def health():
    s = get_settings()
    return {"status": "ok", "voice_mode": "api" if api_enabled() else "browser", "voice_configured": bool(s.openai_api_key)}

# صفحة تجربة الصوت: http://localhost:8000/demo/
app.mount("/demo", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="demo")
