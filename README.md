<div align="center">

# 🌱 ZAR3A | زرعة

### A voice-first AI farming assistant for Egyptian farmers
**Talk to it in Egyptian Arabic. It reads NASA climate data for your land and tells you which crop rotation to plant next, and why.**

`NASA POWER` · `Voice in Egyptian Arabic` · `Explainable recommendations` · `Plant disease diagnosis from a photo`

*Built for the NASA Space Apps Challenge*

</div>

---

## نبذة بالعربي

**زرعة** مساعد زراعي صوتي للمزارع المصري. المزارع بيتكلم بالعامية ("اسمي فرحة، أرضي في المنوفية، بزرع قمح، عايز أوفر مياه")، وزرعة بترد عليه بصوت مصري وتسأله سؤال واحد في المرة، وبعدين تسحب بيانات مناخ أرضه من **NASA POWER** وتديله **٣ دورات زراعية** مقارنة بنظامه الحالي، مع شرح بسيط لكل واحدة: الفايدة، والمخاطر، والدليل، وحدود التقدير. وكمان تقدر تصوّر ورقة النبات وترفعها، وزرعة تقوله المرض وطريقة العلاج والوقاية.

مفيش كتابة ولا قراءة مطلوبة من المزارع. ده مقصود، لأن كتير من المزارعين مبيقروش ولا بيكتبوا.

---

## The problem

Egyptian smallholder farmers decide what to plant next from habit, neighbours' advice, and last season's price. That leads to three costly mistakes:

- **Wasted irrigation water** in a country where water is the scarcest input.
- **Exhausted soil** from planting the same crop or the same plant family back to back.
- **Late disease detection**, when a crop is already damaged.

Existing agri-tech tools assume the user can read, type, and navigate dashboards. Many farmers can't, or won't.

## The solution

ZAR3A turns a **two-minute spoken conversation** into a **data-backed crop plan**:

1. The farmer talks. ZAR3A listens, understands Egyptian dialect, and asks one short question at a time.
2. ZAR3A pulls **NASA POWER** climate data for the farmer's governorate.
3. A rotation engine builds and scores candidate 3-season plans, then returns the current system plus two better alternatives.
4. ZAR3A **speaks the result back** and explains it in plain Arabic.
5. For plant problems, the farmer uploads a photo and gets a diagnosis with treatment and prevention steps.

---

## ✨ Key features

### 🎙️ 1. A real voice conversation, not a form
- **Speaks and listens in Egyptian Arabic.** The farmer taps one big mic button and talks.
- **Guided, one-question-at-a-time dialogue** collecting four things: name, governorate, current crop, goal.
- **Free-form answers work too.** "اسمي فرحة وأرضي في الغربية وزارعة ذرة وعايزة أوفر مياه" fills all four slots in one sentence.
- **Understands corrections.** "لا مش الجيزة، المنوفية" updates the answer instead of derailing the chat.
- **Confirms before analysing.** ZAR3A repeats what it understood ("أرضك في المنوفية وبتزرع قمح، صح؟") so a misheard word never produces a wrong plan.
- **Forgiving to speech-recognition errors.** Fuzzy matching maps "منوفيا" to المنوفية and "قمحه" to wheat.
- **Never blocks the farmer.** Every voice step has a tap fallback (buttons or typing) for noisy fields and poor connections.

### 🧠 2. Resilient, layered intelligence
Voice understanding degrades gracefully instead of failing:

| Layer | What it does |
|---|---|
| **LLM (any OpenAI-compatible provider)** | Natural dialogue in Egyptian dialect, slot extraction, tone. Supports a **fallback model** if the primary hits a rate limit. |
| **Output guard** | Every LLM reply is checked against the dialogue state, then regenerated or replaced by a safe scripted reply if it drifts. |
| **Local NLU (no API, no key)** | Fuzzy governorate/crop matching plus a small **Naive Bayes goal classifier** trained in under a second from hand-written Egyptian-dialect examples. It understands "الميه مش بتوصل لآخر الأرض" as *water saving* even without the keyword. |

If the internet or the LLM goes down, the conversation **keeps working** on the local layer.

### 🛰️ 3. Powered by NASA data
- Pulls **monthly climatology** from **NASA POWER** (community `AG`) for the farmer's location:
  - `T2M` air temperature
  - `PRECTOTCORR` precipitation
  - `ALLSKY_SFC_SW_DWN` solar radiation
- Covers all **27 Egyptian governorates**.
- Results are **cached per 0.5° grid cell**, so repeat queries are instant and demos survive bad Wi-Fi.
- **Honest offline mode.** If NASA is unreachable, ZAR3A uses a clearly labelled approximate Nile-Delta estimate and tells the user the data wasn't live (`data_status.nasa_data_available = false`). It never silently pretends.

### 🔄 4. Three crop-rotation scenarios, scored and compared
For every analysis ZAR3A returns three plans over the next **three seasons**:

| Scenario | Meaning |
|---|---|
| **A: Current system** | The baseline the farmer already follows. Used as the comparison point. |
| **B: Optimised for the farmer's goal** | Best plan for water saving, soil health, or climate fit, depending on what they asked for. |
| **C: A different trade-off** | A deliberately *different* plan (it must differ from B in at least two seasons) optimised for the next objective, so the farmer sees a real choice. |

How the engine works:
- Enumerates every valid season-by-season combination from a **13-crop knowledge base** (wheat, berseem, faba bean, onion, sugar beet, potato, maize, rice, cotton, sesame, peanut, sorghum, tomato).
- **Hard agronomic rules:** never the same crop twice in a plan, and no back-to-back crops from the same plant family for sensitive families (Solanaceae, Amaranthaceae, Amaryllidaceae, Malvaceae).
- **Soft penalties** for cereal-after-cereal and legume-after-legume.
- **Water filter:** if the farmer reports low water availability, high-water crops are excluded.
- Scores each plan on three indexes: **estimated water use**, **climate suitability** (crop's optimal temperature range vs NASA temperature for its growing months), and **soil health** (nitrogen-fixing legumes and family diversity).
- Reports the change versus the current system, for example *"estimated water use about 18% lower than your current rotation."*

### 🔍 5. Explainable, not a black box
Every scenario ships with four plain-Arabic sections:
- **Benefits**: what improves compared with the current system.
- **Risks**: for example "this crop needs a lot of water", or a rotation-rule violation in the current plan.
- **Evidence**: the actual NASA numbers behind the claim (mean season temperature, annual rainfall) and each crop's temperature range.
- **Limitations**: what we assumed and what's missing.

### 🛡️ 6. Built to be trusted
- **No invented numbers.** The indexes are *relative comparisons between alternatives*, not yield forecasts. ZAR3A does not predict production without real yield data.
- **Assumptions are flagged.** If a farmer didn't say what they grew last season, the plan marks that slot as assumed.
- Crop parameters are flagged `needs_expert_review`, and every result carries a disclaimer to consult an agronomist.
- It reports what's missing (`soil_nutrients`, `crop_history`, `goal`) rather than guessing.

### 🌿 7. Plant disease diagnosis from a photo
- Upload a **photo or video** of a plant (the interface has separate image and video tabs).
- ZAR3A returns:
  - the **disease name** in Arabic and English (for example *اللفحة المبكرة / Early Blight*),
  - a **confidence score**,
  - a short **description** of the disease,
  - the **detected plant type**,
  - **treatment methods** and **prevention guidelines**.

### 🔊 8. Voice that sounds Egyptian, with four fallbacks
The speaking side picks the best available engine and falls through automatically:

1. **Self-hosted Egyptian TTS model** from Hugging Face (optional, own server on port 8001)
2. **OpenAI TTS** (if a key is configured)
3. **Microsoft Edge neural voice** `ar-EG-SalmaNeural` (free, no key, Egyptian accent)
4. **Browser `speechSynthesis`** as the last resort, so the farmer always hears something

Speech recognition runs in the browser (Web Speech API, Chrome) or on the server (OpenAI transcription) through `POST /api/voice/turn`.

---

## 🏗️ Architecture

```mermaid
flowchart LR
    F([👩‍🌾 Farmer]) -- speaks / taps --> UI[React + Vite UI]
    UI -- text or audio --> API[FastAPI backend]
    API --> CONV[Conversation engine<br/>LLM + local NLU]
    CONV --> KB[(Knowledge base<br/>13 crops · 27 governorates<br/>rotation rules)]
    API --> NASA[NASA POWER API<br/>T2M · rain · solar]
    NASA -. cached by 0.5° cell .-> CACHE[(Local cache)]
    API --> ENGINE[Rotation engine<br/>generate → filter → score → pick A/B/C]
    ENGINE --> EXPL[Explainability<br/>benefits · risks · evidence · limits]
    API --> DB[(SQLite)]
    API --> TTS[TTS chain<br/>HF → OpenAI → Edge → Browser]
    TTS --> UI
```

### Tech stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Web Speech API |
| Backend | Python 3.12, FastAPI, Pydantic, httpx |
| Data | SQLAlchemy + SQLite, JSON knowledge base |
| Climate data | NASA POWER API |
| Language AI | Any OpenAI-compatible LLM (tested with Groq) + local Naive Bayes NLU |
| Voice | Edge neural TTS, OpenAI TTS/STT, Hugging Face Egyptian TTS, browser speech |
| Deploy | Docker, Render (`render.yaml`), Vercel |
| Tests | pytest |

---

## 🚀 Quick start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env               # then fill in the keys you have
uvicorn app.main:app --reload
```

- API docs (Swagger): `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
- **Voice demo page:** `http://localhost:8000/demo/`

> **No API key? It still works.** Without keys ZAR3A runs on browser voice, free Edge TTS, and the local NLU.

### Frontend

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev                        # http://localhost:5173
```

> Voice input needs **Chrome (desktop or Android)** and **HTTPS** in production. iPhone/Safari speech recognition is limited, so use the tap fallback there.

### Optional: Egyptian TTS model from Hugging Face

```bash
cd backend
pip install -r hf_voice_server/requirements.txt
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install omnivoice
uvicorn hf_voice_server.server:app --port 8001
```

Then set `HF_TTS_URL=http://127.0.0.1:8001` and `TTS_PROVIDER=hf` in `.env`. The first start downloads about 3 GB. On CPU a sentence can take minutes, so use a GPU or pre-generate fixed sentences; the Edge voice is the default for live use.

### Configuration (`backend/.env`)

| Variable | Purpose |
|---|---|
| `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` | Dialogue LLM (any OpenAI-compatible endpoint) |
| `LLM_FALLBACK_MODEL` | Backup model used on rate limits (429) |
| `OPENAI_API_KEY` | Optional OpenAI STT/TTS |
| `VOICE_MODE` | `auto` · `api` · `browser` |
| `TTS_PROVIDER` | `auto` · `edge` · `openai` · `hf` · `browser` |
| `DATABASE_URL` | Defaults to local SQLite |
| `CORS_ORIGINS` | Allowed frontend origins |

### Run the tests

```bash
cd backend
python -m pytest -q
```

---

## 🔌 API at a glance

| Method | Endpoint | What it does |
|---|---|---|
| `POST` | `/api/voice/start` | Start a conversation, returns greeting + audio |
| `POST` | `/api/voice/text-turn` | One dialogue turn from text (mic or buttons) |
| `POST` | `/api/voice/turn` | One dialogue turn from recorded audio |
| `POST` | `/api/voice/session/{id}/analyze` | Run the analysis once the 4 answers are confirmed |
| `POST` | `/api/quick-analysis` | Rotation analysis without saving a field |
| `POST` | `/api/fields` | Create a field profile |
| `POST` | `/api/analysis/{field_id}` | Run and store an analysis |
| `GET` | `/api/analysis/{id}/scenarios/{A\|B\|C}/explanation` | Benefits, risks, evidence, limitations |
| `GET` | `/api/environment/{field_id}` | Monthly NASA climate for a field |
| `GET` | `/api/crops`, `/api/governorates` | Knowledge base |
| `GET` | `/health`, `/api/voice/llm-check`, `/api/voice/tts-check` | Diagnostics |

---

## 🗺️ Roadmap

- Real **soil-test input** to sharpen the soil index.
- More NASA sources: **SMAP** soil moisture, **GPM** rainfall, **MODIS** vegetation indices.
- **Reviewed agronomic parameters** from FAO / Egyptian Ministry of Agriculture, replacing the current starting values.
- A yield model once **verified yield data** is available. We deliberately don't fake one.
- More crops and a finer regional resolution than the governorate level.
- Offline-first mobile experience for low-connectivity farms.

---

## ⚠️ Disclaimer

ZAR3A is a **decision-support tool**, not a replacement for an agronomist. Crop parameters and rotation rules are initial values pending expert review, and climate figures are historical averages, not forecasts for the coming season.

---

<div align="center">

**Built so a farmer can just talk. 🌾**

</div>
