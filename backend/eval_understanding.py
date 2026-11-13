"""قياس فهم الحوار على الـ LLM الحقيقي (Groq). من فولدر backend:  python eval_understanding.py
بيجرّب جمل بالعامية (أخطاء تعرف صوتي، كلام في جملة واحدة، تصحيح، تأكيد، أسئلة) ويطلع نسبة الصح والغلطات.
ابعتلي الجمل الفاشلة وأحسّن عليها."""
import asyncio

from app.services import conversation as conv
from app.services import voice_service as vs

FULL = {"name": "فرحة", "location": "giza", "location_ar": "الجيزة", "current_crop": "wheat", "goal": "yield"}
# (اسم الحالة، profile قبل الجملة، stage، الجملة، شرط النجاح كـ dict من slot->قيمة متوقعة، stage متوقع بعد الجملة أو None)
CASES = [
    ("اسم بسيط", {}, "collecting", "اسمي فرحة", {"name": "فرحة"}, "collecting"),
    ("اسم بمقدمة", {}, "collecting", "السلام عليكم أنا الحاج سيد", {"name": "الحاج سيد"}, "collecting"),
    ("غلطة تعرف: منوفيا", {"name": "فرحة"}, "collecting", "أرضي في منوفيا", {"location": "menoufia"}, "collecting"),
    ("مدينة بدل محافظة", {"name": "فرحة"}, "collecting", "أنا من طنطا", {"location": "gharbia"}, "collecting"),
    ("قمحه", {"name": "فرحة", "location": "gharbia", "location_ar": "الغربية"}, "collecting", "زارعة قمحه", {"current_crop": "wheat"}, "collecting"),
    ("درة", {"name": "فرحة", "location": "gharbia", "location_ar": "الغربية"}, "collecting", "عندي درة", {"current_crop": "maize"}, "collecting"),
    ("فول سوداني", {"name": "فرحة", "location": "gharbia", "location_ar": "الغربية"}, "collecting", "بزرع فول سوداني", {"current_crop": "peanut"}, "collecting"),
    ("هدف: ميه", {**FULL, "goal": None}, "collecting", "الميه مش بتوصل لآخر الأرض", {"goal": "water_saving"}, "confirming"),
    ("هدف: ترعة ناشفة", {**FULL, "goal": None}, "collecting", "الترعة بقت ناشفة وبنتعب في الري", {"goal": "water_saving"}, "confirming"),
    ("هدف: تربة", {**FULL, "goal": None}, "collecting", "الأرض تعبت أوي ومبقتش زي زمان", {"goal": "soil_health"}, "confirming"),
    ("هدف: ملوحة", {**FULL, "goal": None}, "collecting", "الأرض بقت مالحة", {"goal": "soil_health"}, "confirming"),
    ("هدف: إنتاج", {**FULL, "goal": None}, "collecting", "عايزة المحصول يطلع أكتر", {"goal": "yield"}, "confirming"),
    ("هدف: حر", {**FULL, "goal": None}, "collecting", "الحر بقى جامد والزرع بيتحرق", {"goal": "climate_resilience"}, "confirming"),
    ("كله في جملة", {}, "collecting", "اسمي فرحة وأرضي في الغربية وزارعة ذرة وعايزة أوفر مياه",
     {"name": "فرحة", "location": "gharbia", "current_crop": "maize", "goal": "water_saving"}, "confirming"),
    ("كله مع أخطاء", {}, "collecting", "أنا محمد من منوفيا بزرع بندورة والمية قليلة",
     {"name": "محمد", "location": "menoufia", "current_crop": "tomato", "goal": "water_saving"}, "confirming"),
    ("تصحيح محافظة", FULL, "confirming", "لا مش الجيزة، المنوفية", {"location": "menoufia"}, "confirming"),
    ("تصحيح محصول", FULL, "confirming", "لأ أنا زارع برسيم مش قمح", {"current_crop": "berseem"}, "confirming"),
    ("تصحيح اسم", FULL, "confirming", "اسمي فرح مش فرحة", {"name": "فرح"}, "confirming"),
    ("تصحيح هدف", FULL, "confirming", "لا هدفي توفير المياه", {"goal": "water_saving"}, "confirming"),
    ("تأكيد", FULL, "confirming", "أيوه مظبوط", {}, "done"),
    ("تأكيد 2", FULL, "confirming", "تمام كده صح", {}, "done"),
    ("رفض بدون تصحيح", FULL, "confirming", "لا غلط", {}, "confirming"),
    ("سؤال خارج الموضوع", {"name": "فرحة"}, "collecting", "هو الجو هيبقى عامل إزاي بكرة؟", {}, "collecting"),
    ("سؤال عن زرعة", {"name": "فرحة"}, "collecting", "هو التطبيق ده بياخد فلوس؟", {}, "collecting"),
    ("محافظة مش موجودة", {"name": "فرحة"}, "collecting", "أرضي في المريخ", {"_no": "location"}, "collecting"),
]


async def main():
    if not vs.llm_enabled():
        print("مفيش مفتاح LLM في .env"); return
    ok = 0
    delay = 6   # ثواني بين الجمل عشان حد التوكنز في الدقيقة عند Groq
    for name, prof, stage, text, want, want_stage in CASES:
        s = conv.Session(id="eval", profile=dict(prof), stage=stage)
        await asyncio.sleep(delay)
        try:
            out = await conv.process_text(s, text)
        except Exception as e:
            print(f"❌ {name}: خطأ {e}"); continue
        good = out.get("engine") == "llm"
        for k, v in want.items():
            if k == "_no":
                good &= not s.profile.get(v) or s.profile.get(v) == prof.get(v)
            else:
                good &= s.profile.get(k) == v
        if want_stage:
            good &= s.stage == want_stage
        ok += good
        flag = "✅" if good else "❌"
        extra = "" if good else f"\n     قال: {text}\n     المتوقع: {want} / {want_stage}\n     اللي حصل: {s.profile} / {s.stage} / engine={out.get('engine')} {out.get('llm_error', '')}"
        print(f"{flag} {name}  ←  \"{out['reply']}\"{extra}")
    print(f"\nالنتيجة: {ok}/{len(CASES)}")


asyncio.run(main())
