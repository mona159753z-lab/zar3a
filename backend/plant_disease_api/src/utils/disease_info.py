from dataclasses import dataclass
from typing import List

@dataclass
class DiseaseInfo:
    name: str
    name_ar: str
    plant: str
    severity: str  # "low", "medium", "high"
    description: str
    treatments: List[str]
    prevention: List[str]

DISEASE_DATABASE = {
    "Apple___Apple_scab": DiseaseInfo(
        name="Apple Scab",
        name_ar="جرب التفاح",
        plant="تفاح",
        severity="medium",
        description="مرض فطري يسبب آفات داكنة قشرية على الأوراق والثمار.",
        treatments=[
            "رش مبيد فطري يحتوي على كابتان أو مانكوزيب",
            "إزالة الأوراق المصابة المتساقطة وتدميرها",
            "الرش كل 7 أيام خلال موسم الأمطار",
        ],
        prevention=[
            "زراعة أصناف تفاح مقاومة للمرض",
            "ضمان دوران هواء جيد",
            "تنظيف الأوراق المتساقطة في الخريف",
        ],
    ),
    "Apple___Black_rot": DiseaseInfo(
        name="Black Rot",
        name_ar="العفن الأسود",
        plant="تفاح",
        severity="high",
        description="مرض فطري يسبب آفات تعفن سوداء على الثمار والأوراق.",
        treatments=[
            "تطبيق مبيد فطري يحتوي على كابتان",
            "تقليم وإزالة الفروع المصابة",
            "إزالة الثمار المحنطة من الشجرة",
        ],
        prevention=[
            "الحفاظ على نظافة البستان",
            "تقليم الأخشاب الميتة بانتظام",
            "تجنب جرح الأشجار أثناء التقليم",
        ],
    ),
    "Apple___Cedar_apple_rust": DiseaseInfo(
        name="Cedar Apple Rust",
        name_ar="صدأ التفاح",
        plant="تفاح",
        severity="medium",
        description="مرض فطري يسبب بقعاً برتقالية على أوراق التفاح.",
        treatments=[
            "تطبيق مبيد فطري ميكلوبوتانيل عند تفتح البراعم",
            "إزالة أشجار الأرز/العرعر القريبة إن أمكن",
            "الرش كل 7-10 أيام خلال الطقس الرطب",
        ],
        prevention=[
            "زراعة أصناف تفاح مقاومة للصدأ",
            "تجنب الزراعة بالقرب من أشجار الأرز",
            "مراقبة الأوراق أسبوعياً في الربيع",
        ],
    ),
    "Apple___healthy": DiseaseInfo(
        name="Healthy",
        name_ar="سليم",
        plant="تفاح",
        severity="low",
        description="النبات يبدو سليماً ولا تظهر عليه أي علامات مرض.",
        treatments=[],
        prevention=[
            "الاستمرار في المراقبة المنتظمة",
            "الحفاظ على التسميد المناسب",
            "ضمان الري الكافي",
        ],
    ),
    "Blueberry___healthy": DiseaseInfo(
        name="Healthy",
        name_ar="سليم",
        plant="توت أزرق",
        severity="low",
        description="النبات يبدو سليماً ولا تظهر عليه أي علامات مرض.",
        treatments=[],
        prevention=[
            "الحفاظ على حموضة التربة (pH 4.5-5.5)",
            "مراقبة المرض أسبوعياً",
            "ضمان الصرف الصحي",
        ],
    ),
    "Cherry_(including_sour)___Powdery_mildew": DiseaseInfo(
        name="Powdery Mildew",
        name_ar="البياض الدقيقي",
        plant="كرز",
        severity="medium",
        description="مرض فطري يسبب طبقة بيضاء مسحوقية على الأوراق.",
        treatments=[
            "تطبيق الكبريت أو بيكربونات البوتاسيوم",
            "إزالة البراعم المصابة بشدة",
            "الرش كل 7-14 يوم",
        ],
        prevention=[
            "الزراعة في مناطق مشمسة وجيدة التهوية",
            "تجنب الإفراط في التسميد النيتروجيني",
            "استخدام أصناف كرز مقاومة",
        ],
    ),
    "Cherry_(including_sour)___healthy": DiseaseInfo(
        name="Healthy",
        name_ar="سليم",
        plant="كرز",
        severity="low",
        description="النبات يبدو سليماً ولا تظهر عليه أي علامات مرض.",
        treatments=[],
        prevention=[
            "الحفاظ على نظافة البستان",
            "المراقبة المنتظمة للمرض",
            "التقليم المناسب لتدفق الهواء",
        ],
    ),
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": DiseaseInfo(
        name="Gray Leaf Spot",
        name_ar="تبقع الأوراق الرمادي",
        plant="ذرة",
        severity="high",
        description="مرض فطري يسبب آفات رمادية مستطيلة على أوراق الذرة.",
        treatments=[
            "تطبيق مبيد فطري ستروبيلورين",
            "الرش في مرحلة ظهور الحريرة",
            "التكرار كل 14 يوماً",
        ],
        prevention=[
            "زراعة هجين مقاوم",
            "تقليل بقايا المحاصيل من خلال الحراثة",
            "التناوب مع فول الصويا أو محاصيل أخرى",
        ],
    ),
    "Corn_(maize)___Common_rust_": DiseaseInfo(
        name="Common Rust",
        name_ar="الصدأ الشائع",
        plant="ذرة",
        severity="medium",
        description="مرض فطري يسبب بثور بنية مائلة للحمرة على أسطح الأوراق.",
        treatments=[
            "تطبيق مبيد فطري بروبيكونازول",
            "الرش عند أول علامة على ظهور البثور",
            "التكرار بعد 14 يوماً إذا لزم الأمر",
        ],
        prevention=[
            "زراعة هجين مقاوم للصدأ",
            "الزراعة المبكرة لتجنب فترات العدوى القصوى",
            "مراقبة الحقول بانتظام",
        ],
    ),
    "Corn_(maize)___Northern_Leaf_Blight": DiseaseInfo(
        name="Northern Leaf Blight",
        name_ar="لفحة الأوراق الشمالية",
        plant="ذرة",
        severity="high",
        description="مرض فطري يسبب آفات طويلة رمادية خضراء على أوراق الذرة.",
        treatments=[
            "تطبيق بروبيكونازول أو أزوكسيستروبين",
            "الرش عند أول علامة على الآفات",
            "التكرار بعد 14 يوماً إذا لزم الأمر",
        ],
        prevention=[
            "زراعة هجين ذرة مقاوم",
            "تناوب المحاصيل مع نباتات غير مضيفة",
            "حرث بقايا المحاصيل المصابة بعد الحصاد",
        ],
    ),
    "Corn_(maize)___healthy": DiseaseInfo(
        name="Healthy",
        name_ar="سليم",
        plant="ذرة",
        severity="low",
        description="النبات يبدو سليماً ولا تظهر عليه أي علامات مرض.",
        treatments=[],
        prevention=[
            "الحفاظ على التسميد المتوازن",
            "ضمان الصرف الجيد",
            "تفقد الحقول أسبوعياً",
        ],
    ),
    "Grape___Black_rot": DiseaseInfo(
        name="Black Rot",
        name_ar="العفن الأسود",
        plant="عنب",
        severity="high",
        description="مرض فطري يسبب توتاً أسود متجعداً وبقعاً على الأوراق.",
        treatments=[
            "تطبيق مانكوزيب أو ميكلوبوتانيل",
            "إزالة وتدمير التوت المصاب",
            "الرش كل 10 أيام من تفتح البراعم",
        ],
        prevention=[
            "تقليم الكروم لتدفق هواء جيد",
            "إزالة التوت المحنط",
            "تجنب الري بالرش",
        ],
    ),
    "Grape___Esca_(Black_Measles)": DiseaseInfo(
        name="Esca (Black Measles)",
        name_ar="مرض الإسكا",
        plant="عنب",
        severity="high",
        description="مرض فطري يسبب أنماطاً مخططّة كالنمر على الأوراق.",
        treatments=[
            "لا يوجد علاج كيميائي متاح",
            "إزالة وحرق الأخشاب المصابة",
            "تطبيق واقيات الجروح بعد التقليم",
        ],
        prevention=[
            "استخدام أدوات تقليم نظيفة",
            "التقليم خلال الطقس الجاف",
            "حماية جروح التقليم فوراً",
        ],
    ),
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": DiseaseInfo(
        name="Leaf Blight",
        name_ar="لفحة أوراق العنب",
        plant="عنب",
        severity="medium",
        description="مرض فطري يسبب بقعاً بنية داكنة على أوراق العنب.",
        treatments=[
            "تطبيق مبيد فطري نحاسي",
            "إزالة الأوراق المصابة فوراً",
            "رش مانكوزيب كل 14 يوماً",
        ],
        prevention=[
            "ضمان دوران هواء جيد",
            "تجنب تبليل الأوراق",
            "المراقبة الأسبوعية خلال الطقس الرطب",
        ],
    ),
    "Grape___healthy": DiseaseInfo(
        name="Healthy",
        name_ar="سليم",
        plant="عنب",
        severity="low",
        description="النبات يبدو سليماً ولا تظهر عليه أي علامات مرض.",
        treatments=[],
        prevention=[
            "الحفاظ على جدول تقليم منتظم",
            "مراقبة العلامات المبكرة للمرض",
            "ضمان التغذية السليمة",
        ],
    ),
    "Orange___Haunglongbing_(Citrus_greening)": DiseaseInfo(
        name="Citrus Greening (HLB)",
        name_ar="اخضرار الحمضيات",
        plant="برتقال",
        severity="high",
        description="مرض بكتيري قاتل ينتشر بواسطة الحشرات — لا يوجد علاج متاح.",
        treatments=[
            "إزالة وتدمير الأشجار المصابة",
            "مكافحة حشرة بسيلا الحمضيات الآسيوية",
            "تطبيق مبيدات حشرية جهازية",
        ],
        prevention=[
            "استخدام نباتات مشتل خالية من الأمراض",
            "مراقبة الحشرات البسيلا",
            "حجر النباتات الجديدة قبل الزراعة",
        ],
    ),
    "Peach___Bacterial_spot": DiseaseInfo(
        name="Bacterial Spot",
        name_ar="التبقع البكتيري",
        plant="خوخ",
        severity="high",
        description="مرض بكتيري يسبب آفات مشبعة بالماء على الأوراق والثمار.",
        treatments=[
            "تطبيق مبيد بكتيري نحاسي",
            "إزالة الثمار والأوراق المصابة",
            "الرش خلال موسم السكون",
        ],
        prevention=[
            "زراعة أصناف خوخ مقاومة",
            "تجنب العمل في الظروف الرطبة",
            "التقليم لتدفق هواء جيد",
        ],
    ),
    "Peach___healthy": DiseaseInfo(
        name="Healthy",
        name_ar="سليم",
        plant="خوخ",
        severity="low",
        description="النبات يبدو سليماً ولا تظهر عليه أي علامات مرض.",
        treatments=[],
        prevention=[
            "التقليم المنتظم لتدفق الهواء",
            "مراقبة العلامات المبكرة للمرض",
            "الحفاظ على التسميد المناسب",
        ],
    ),
    "Pepper,_bell___Bacterial_spot": DiseaseInfo(
        name="Bacterial Spot",
        name_ar="التبقع البكتيري",
        plant="فلفل",
        severity="high",
        description="مرض بكتيري يسبب بقعاً مشبعة بالماء على الأوراق والثمار.",
        treatments=[
            "تطبيق مبيد بكتيري نحاسي فوراً",
            "إزالة النباتات المصابة بشدة",
            "تجنب العمل في الحقول المبتلة",
        ],
        prevention=[
            "استخدام بذور معتمدة خالية من الأمراض",
            "تناوب المحاصيل كل 2-3 سنوات",
            "تجنب الري بالرش",
        ],
    ),
    "Pepper,_bell___healthy": DiseaseInfo(
        name="Healthy",
        name_ar="سليم",
        plant="فلفل",
        severity="low",
        description="النبات يبدو سليماً ولا تظهر عليه أي علامات مرض.",
        treatments=[],
        prevention=[
            "الحفاظ على التباعد المناسب",
            "المراقبة الأسبوعية لعلامات المرض",
            "ضمان الصرف الكافي",
        ],
    ),
    "Potato___Early_blight": DiseaseInfo(
        name="Early Blight",
        name_ar="اللفحة المبكرة",
        plant="بطاطس",
        severity="medium",
        description="مرض فطري يسبب آفات داكنة على الأوراق الأكبر سناً أولاً.",
        treatments=[
            "تطبيق كلوروثالونيل أو مانكوزيب",
            "إزالة الأوراق السفلية المصابة",
            "تكرار الرش كل 7-10 أيام",
        ],
        prevention=[
            "استخدام بطاطس بذور خالية من الأمراض",
            "تجنب الري بالرش",
            "الحفاظ على العناصر الغذائية الكافية للتربة",
        ],
    ),
    "Potato___Late_blight": DiseaseInfo(
        name="Late Blight",
        name_ar="اللفحة المتأخرة",
        plant="بطاطس",
        severity="high",
        description="مرض فطري شديد التدمير — تسبب في مجاعة البطاطس الأيرلندية.",
        treatments=[
            "تطبيق مبيد فطري ميتالاكسيل فوراً",
            "تدمير جميع المواد النباتية المصابة",
            "عدم تخزين الدرنات المصابة",
        ],
        prevention=[
            "زراعة أصناف مقاومة",
            "تكديس التربة حول النباتات",
            "تجنب الزراعة في الحقول المصابة سابقاً",
        ],
    ),
    "Potato___healthy": DiseaseInfo(
        name="Healthy",
        name_ar="سليم",
        plant="بطاطس",
        severity="low",
        description="النبات يبدو سليماً ولا تظهر عليه أي علامات مرض.",
        treatments=[],
        prevention=[
            "الحفاظ على الفحص المنتظم",
            "ضمان الصرف الصحي",
            "تناوب المحاصيل سنوياً",
        ],
    ),
    "Raspberry___healthy": DiseaseInfo(
        name="Healthy",
        name_ar="سليم",
        plant="توت العليق",
        severity="low",
        description="النبات يبدو سليماً ولا تظهر عليه أي علامات مرض.",
        treatments=[],
        prevention=[
            "تقليم السيقان القديمة بعد الحصاد",
            "الحفاظ على دوران هواء جيد",
            "مراقبة الآفات والأمراض",
        ],
    ),
    "Soybean___healthy": DiseaseInfo(
        name="Healthy",
        name_ar="سليم",
        plant="فول الصويا",
        severity="low",
        description="النبات يبدو سليماً ولا تظهر عليه أي علامات مرض.",
        treatments=[],
        prevention=[
            "تناوب المحاصيل سنوياً",
            "استخدام بذور معتمدة خالية من الأمراض",
            "مراقبة الحقول بانتظام",
        ],
    ),
    "Squash___Powdery_mildew": DiseaseInfo(
        name="Powdery Mildew",
        name_ar="البياض الدقيقي",
        plant="قرع",
        severity="medium",
        description="مرض فطري يسبب مسحوقاً أبيض على أسطح الأوراق.",
        treatments=[
            "تطبيق زيت النيم أو رش الكبريت",
            "إزالة الأوراق المصابة",
            "رش محلول بيكربونات الصوديوم (ملعقة كبيرة لكل لتر)",
        ],
        prevention=[
            "الزراعة في مواقع مشمسة بالكامل",
            "تجنب ازدحام النباتات",
            "الري من القاعدة وليس على الأوراق",
        ],
    ),
    "Strawberry___Leaf_scorch": DiseaseInfo(
        name="Leaf Scorch",
        name_ar="احتراق أوراق الفراولة",
        plant="فراولة",
        severity="medium",
        description="مرض فطري يسبب بقعاً أرجوانية تتحد لتشكل مناطق محترقة كبيرة.",
        treatments=[
            "تطبيق مبيد فطري كابتان أو ثيرام",
            "إزالة وتدمير الأوراق المصابة",
            "الرش كل 7-10 أيام",
        ],
        prevention=[
            "زراعة أصناف مقاومة",
            "تجنب الري بالرش",
            "ضمان دوران هواء جيد بين النباتات",
        ],
    ),
    "Strawberry___healthy": DiseaseInfo(
        name="Healthy",
        name_ar="سليم",
        plant="فراولة",
        severity="low",
        description="النبات يبدو سليماً ولا تظهر عليه أي علامات مرض.",
        treatments=[],
        prevention=[
            "الحفاظ على التباعد المناسب للنباتات",
            "إزالة الأوراق القديمة بانتظام",
            "مراقبة علامات المرض أسبوعياً",
        ],
    ),
    "Tomato___Bacterial_spot": DiseaseInfo(
        name="Bacterial Spot",
        name_ar="التبقع البكتيري",
        plant="طماطم",
        severity="high",
        description="مرض بكتيري يسبب بقعاً مشبعة بالماء على الأوراق والثمار.",
        treatments=[
            "تطبيق مبيد بكتيري نحاسي فوراً",
            "إزالة المواد النباتية المصابة",
            "تجنب العمل مع النباتات المبتلة",
        ],
        prevention=[
            "استخدام بذور معتمدة خالية من الأمراض",
            "تجنب الري بالرش",
            "تناوب المحاصيل كل 2-3 سنوات",
        ],
    ),
    "Tomato___Early_blight": DiseaseInfo(
        name="Early Blight",
        name_ar="اللفحة المبكرة",
        plant="طماطم",
        severity="medium",
        description="مرض فطري يسبب بقعاً داكنة بحلقات متحدة المركز على الأوراق.",
        treatments=[
            "رش مبيد فطري يحتوي على كلوروثالونيل",
            "إزالة الأوراق المصابة وتدميرها فوراً",
            "تطبيق مبيد فطري نحاسي كل 7 أيام",
        ],
        prevention=[
            "تجنب الري بالرش من الأعلى",
            "ضمان التباعد المناسب بين النباتات لتدفق الهواء",
            "تناوب المحاصيل كل موسم",
        ],
    ),
    "Tomato___Late_blight": DiseaseInfo(
        name="Late Blight",
        name_ar="اللفحة المتأخرة",
        plant="طماطم",
        severity="high",
        description="مرض فطري شديد يمكن أن يدمر المحاصيل بأكملها بسرعة.",
        treatments=[
            "تطبيق مبيد فطري مانكوزيب أو ميتالاكسيل",
            "إزالة النباتات المصابة لمنع الانتشار",
            "الرش كل 5 أيام خلال الطقس الرطب",
        ],
        prevention=[
            "استخدام أصناف طماطم مقاومة",
            "تجنب العمل في الحقول المبتلة",
            "تدمير جميع مخلفات النباتات بعد الحصاد",
        ],
    ),
    "Tomato___Leaf_Mold": DiseaseInfo(
        name="Leaf Mold",
        name_ar="عفن أوراق الطماطم",
        plant="طماطم",
        severity="medium",
        description="مرض فطري يزدهر في البيئات عالية الرطوبة.",
        treatments=[
            "تحسين تهوية الدفيئة",
            "تطبيق مبيد فطري يحتوي على مانكوزيب",
            "تقليل الرطوبة إلى أقل من 85%",
        ],
        prevention=[
            "الزراعة في مناطق جيدة التهوية",
            "تجنب تبليل الأوراق عند الري",
            "استخدام أصناف مقاومة للأمراض",
        ],
    ),
    "Tomato___Septoria_leaf_spot": DiseaseInfo(
        name="Septoria Leaf Spot",
        name_ar="تبقع سيبتوريا",
        plant="طماطم",
        severity="medium",
        description="مرض فطري يسبب بقعاً دائرية صغيرة ذات حواف داكنة.",
        treatments=[
            "تطبيق كلوروثالونيل أو مانكوزيب",
            "إزالة الأوراق السفلية المصابة",
            "الرش كل 7-10 أيام",
        ],
        prevention=[
            "تجنب الري بالرش",
            "تغطية التربة (Mulch) حول قاعدة النباتات",
            "تناوب المحاصيل سنوياً",
        ],
    ),
    "Tomato___Spider_mites Two-spotted_spider_mite": DiseaseInfo(
        name="Spider Mites",
        name_ar="العناكب الحمراء",
        plant="طماطم",
        severity="medium",
        description="إصابة بالآفات تسبب أوراقاً صفراء منقطة وشبكات عنكبوت.",
        treatments=[
            "تطبيق زيت النيم أو صابون مبيد للحشرات",
            "رش الماء بقوة على الجانب السفلي للأوراق",
            "تطبيق مبيد أبامكتين إذا كانت الإصابة شديدة",
        ],
        prevention=[
            "الحفاظ على رطوبة التربة الكافية",
            "تجنب الإفراط في النيتروجين",
            "إدخال العناكب المفترسة",
        ],
    ),
    "Tomato___Target_Spot": DiseaseInfo(
        name="Target Spot",
        name_ar="التبقع الهدفي",
        plant="طماطم",
        severity="medium",
        description="مرض فطري يسبب بقعاً ذات حلقات متحدة المركز على الأوراق.",
        treatments=[
            "تطبيق مبيد فطري كلوروثالونيل",
            "إزالة الأوراق المصابة",
            "الرش كل 7 أيام",
        ],
        prevention=[
            "ضمان دوران هواء جيد",
            "تجنب الري بالرش",
            "تناوب المحاصيل بانتظام",
        ],
    ),
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": DiseaseInfo(
        name="Yellow Leaf Curl Virus",
        name_ar="فيروس تجعد الأوراق الصفراء",
        plant="طماطم",
        severity="high",
        description="مرض فيروسي ينتشر بواسطة الذباب الأبيض ويسبب اصفراراً وتجعداً.",
        treatments=[
            "إزالة وتدمير النباتات المصابة",
            "مكافحة تعداد الذباب الأبيض بالمبيدات الحشرية",
            "لا يوجد علاج كيميائي للفيروس",
        ],
        prevention=[
            "استخدام أصناف طماطم مقاومة للفيروس",
            "مكافحة الذباب الأبيض بالمصائد الصفراء اللاصقة",
            "استخدام أغلفة عاكسة لطرد الذباب الأبيض",
        ],
    ),
    "Tomato___Tomato_mosaic_virus": DiseaseInfo(
        name="Tomato Mosaic Virus",
        name_ar="فيروس موزاييك الطماطم",
        plant="طماطم",
        severity="high",
        description="مرض فيروسي يسبب أنماط موزاييك وأوراقاً مشوهة.",
        treatments=[
            "إزالة وتدمير النباتات المصابة فوراً",
            "تطهير الأدوات بمحلول مبيض",
            "لا يوجد علاج كيميائي متاح",
        ],
        prevention=[
            "استخدام بذور معتمدة خالية من الفيروسات",
            "غسل اليدين قبل التعامل مع النباتات",
            "مكافحة ناقلات المن",
        ],
    ),
    "Tomato___healthy": DiseaseInfo(
        name="Healthy",
        name_ar="سليم",
        plant="طماطم",
        severity="low",
        description="النبات يبدو سليماً ولا تظهر عليه أي علامات مرض.",
        treatments=[],
        prevention=[
            "الاستمرار في جدول الري المنتظم",
            "المراقبة الأسبوعية للعلامات المبكرة",
            "الحفاظ على التغذية السليمة",
        ],
    ),
}

def get_disease_info(class_name: str) -> DiseaseInfo:
    """Get disease information by class name."""
    return DISEASE_DATABASE.get(
        class_name,
        DiseaseInfo(
            name=class_name.replace("_", " "),
            name_ar="غير معروف",
            plant="غير معروف",
            severity="medium",
            description="معلومات المرض غير متوفرة.",
            treatments=["استشر خبيراً زراعياً محلياً"],
            prevention=["راقب النبات بانتظام"],
        ),
    )

def get_severity_color(severity: str) -> str:
    """Return color code based on severity."""
    colors = {
        "low": "#22c55e",
        "medium": "#f97316", 
        "high": "#ef4444",
    }
    return colors.get(severity, "#888888")

SUPPORTED_PLANTS = list({info.plant for info in DISEASE_DATABASE.values()})
ALL_CLASSES = list(DISEASE_DATABASE.keys())