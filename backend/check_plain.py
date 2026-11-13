import asyncio

from app.services import voice_service as vs


async def main():
    msgs = [{"role": "user", "content": 'Reply with only this JSON: {"ok": true}'}]
    try:
        print("OK ->", await vs.chat_json(msgs))
    except vs.VoiceServiceError as e:
        print("فشل ->", e.message)


asyncio.run(main())