"""تجربة المفتاح قبل ما نعتمد عليه. من فولدر backend:  python check_llm.py"""
import asyncio

from app.config import get_settings
from app.services import voice_service as vs


async def main():
    s = get_settings()
    print("base_url:", s.llm_base_url or s.openai_base_url)
    print("model   :", s.llm_model)
    print("key set :", bool(s.llm_api_key or s.openai_api_key))
    msgs = [{"role": "system", "content": 'رد بـ JSON فقط: {"extracted": {"location": null}, "reply": "..."}'},
            {"role": "user", "content": "أرضي في منوفيا"}]
    try:
        print("\nLLM chat: OK ->", await vs.chat_json(msgs))
    except vs.VoiceServiceError as e:
        print("\nLLM chat: فشل ->", e.message)


asyncio.run(main())