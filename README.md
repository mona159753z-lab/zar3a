# ZAR3A — زرعة

```
zar3a/
├── backend/    FastAPI (جاهز)
├── frontend/   حط React هنا
├── docs/       الوثيقة والعرض
└── render.yaml نشر الباك على reliway
```

## تشغيل الباك (محلي)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate      # ويندوز: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                                   # حط OPENAI_API_KEY
uvicorn app.main:app --reload
```

- التوثيق التفاعلي: http://localhost:8000/docs
- الاختبارات: `python -m pytest -q` (١٤ اختبار، من غير إنترنت ولا مفاتيح)

## الصوت من غير API (صوت المتصفح) ← الافتراضي لو مفيش مفتاح

من غير `OPENAI_API_KEY` الباك بيشتغل تلقائيًا بوضع المتصفح (أو ثبّتيه بـ `VOICE_MODE=browser` في `.env`):

- النطق والاستماع بيتعملوا في المتصفح (Web Speech API)، والباك بيستقبل النص بس ويفهمه بقواعد (من غير LLM).
- **جربيه فورًا:** شغلي الباك وافتحي **http://localhost:8000/demo/** في **Chrome**، واضغطي الميكروفون.
- لو الباك على Render، نفس الصفحة على `https://اسم-الخدمة.onrender.com/demo/` (الميكروفون محتاج HTTPS أو localhost).
- الواجهة بتستخدم `frontend/src/voice/browserVoice.js` (فيه كلاس `BrowserVoiceAgent`) و`useBrowserVoice.js` كـ hook لـ React. نفس الملف موجود في `backend/app/static/` للصفحة التجريبية.
- الأسئلة: الاسم ← المحافظة ← المحصول ← الهدف. المزارع ممكن يقول كل حاجة في جملة واحدة. وفيه أزرار بديلة لو الصوت فشل.

**حدود الوضع ده:** الاستماع شغال كويس في Chrome (كمبيوتر وأندرويد) وبيحتاج إنترنت، وضعيف على iPhone/Safari وFirefox. دقة العامية المصرية متوسطة. جودة صوت النطق بتعتمد على الجهاز؛ لو مفيهوش صوت عربي هيظهر الكلام مكتوب بس. ولأن الفهم بالقواعد، المحاصيل والمحافظات لازم تكون من القوائم اللي في `data/`.

## الحوار الصوتي بالـ API (STT → LLM → TTS) — اختياري

الدور الواحد = تسجيل المزارع → نص → LLM يستخرج المعلومة ويرد → رد صوتي. الأسئلة بالترتيب: الاسم ← المحافظة ← المحصول ← الهدف.

| الخطوة | Endpoint |
|---|---|
| بداية + ترحيب صوتي | `POST /api/voice/start` |
| دور بالصوت (multipart: `audio`, `session_id`) | `POST /api/voice/turn` |
| دور بالنص (بديل لو المايك فشل) | `POST /api/voice/text-turn` `{session_id, text}` |
| نطق أي نص | `POST /api/voice/tts` `{text}` |
| لما `done=true`: تحليل كامل (+ `?speak=true` لصوت الملخص) | `POST /api/voice/session/{id}/analyze` |

كل رد فيه `reply_text` و`audio_base64` (mp3) و`profile` و`missing` و`done`. لو `audio_base64` فاضي (فشل TTS) استخدموا `speechSynthesis` في المتصفح على `reply_text`.

مثال للواجهة (JS):

```js
const API = import.meta.env.VITE_API_URL;
let sid;
async function start() {
  const r = await (await fetch(`${API}/api/voice/start`, { method: "POST" })).json();
  sid = r.session_id; play(r);                       // لازم تتنده من ضغطة زرار
}
async function sendRecording(blob) {                 // blob من MediaRecorder
  const fd = new FormData(); fd.append("audio", blob, "a.webm"); fd.append("session_id", sid);
  const r = await (await fetch(`${API}/api/voice/turn`, { method: "POST", body: fd })).json();
  play(r);
  if (r.done) { const out = await (await fetch(`${API}/api/voice/session/${sid}/analyze?speak=true`, { method: "POST" })).json(); /* out.analysis, out.speech */ }
}
const play = (r) => r.audio_base64 ? new Audio("data:audio/mpeg;base64," + r.audio_base64).play() : speechSynthesis.speak(new SpeechSynthesisUtterance(r.reply_text));
```

## باقي الـ API

`GET /health` · `GET /api/crops` · `GET /api/governorates` · `POST /api/fields` · `POST /api/fields/{id}/crop-history` · `POST /api/fields/{id}/soil-data` · `GET /api/environment/{field_id}` · `POST /api/analysis/{field_id}` · `GET /api/analysis/{id}/scenarios` · `GET /api/analysis/{id}/scenarios/{A|B|C}/explanation` · `POST /api/quick-analysis` (من غير تخزين، لتجربة الواجهة).

## ملفات لازم تتراجع

- `backend/app/data/crops.json` و`rotation_rules.json`: **قيم مبدئية** (احتياج مائي، مدى الحرارة، أثر على التربة، قواعد التناوب) لازم تتراجع من مرجع (FAO/مراكز البحوث) قبل العرض. كل محصول معلّم `needs_expert_review`.
- `backend/app/data/governorates.json`: إحداثيات تقريبية لمراكز المحافظات.

## النشر

- **Render**: ارفع الريبو، يقرأ `render.yaml`، وحط `OPENAI_API_KEY` في Environment. الخطة المجانية بتنام؛ افتحوا `/health` قبل العرض بدقايق. ملف SQLite ممكن يتمسح عند إعادة التشغيل (المحاصيل في JSON جوه الريبو فمفيش مشكلة).
- **Frontend على Vercel**: HTTPS مطلوب للمايك. غيّروا `CORS_ORIGINS` لعنوان الموقع.
