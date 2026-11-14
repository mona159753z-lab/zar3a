import {
  Sprout, CalendarDays, Wheat, Warehouse, History, MapPin,
  Lightbulb, Zap, Pencil, FileText, Plus, ArrowLeft, RefreshCw, Leaf,
} from 'lucide-react'

/* ====== البيانات (بعدين هتيجي من API) ====== */
const stats = [
  { icon: Warehouse, label: 'مزرعة النور', value: '12 فدان', sub: 'مساحة المزرعة' },
  { icon: Wheat, label: 'المحصول الحالي', value: 'قمح' },
  { icon: Sprout, label: 'عدد الحقول', value: '3 حقول' },
  { icon: CalendarDays, label: 'الموسم الحالي', value: 'شتاء 2026' },
]

const history = [
  { crop: 'قمح', year: 2026, badge: 'الموسم الحالي', current: true },
  { crop: 'ذرة', year: 2025, badge: 'الموسم السابق' },
  { crop: 'فول', year: 2024, badge: 'قبل موسمين' },
]

const fields = [
  { name: 'الحقل الرئيسي', info: 'قمح · 6 فدان' },
  { name: 'الحقل الشرقي', info: 'ذرة · 4 فدان' },
  { name: 'الحقل الغربي', info: 'بدون زراعة · 2 فدان' },
]

const actions = [
  { icon: Pencil, label: 'تعديل بيانات المزرعة' },
  { icon: FileText, label: 'عرض سجل المحاصيل' },
  { icon: Plus, label: 'إضافة محصول جديد' },
]

/* ====== مكونات صغيرة ====== */
function Card({ children, className = '' }) {
  return (
    <div className={`rounded-2xl border border-primary/5 bg-white p-5 shadow-sm ${className}`}>
      {children}
    </div>
  )
}

function CardTitle({ icon: Icon, children }) {
  return (
    <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-primary">
      <Icon className="h-5 w-5" />
      {children}
    </h2>
  )
}

/* ====== الصفحة ====== */
export default function MyFarm() {
  return (
    <main className="mx-auto max-w-7xl space-y-6 px-4 pb-16 pt-28 md:px-8">
      {/* البانر */}
      <section
        className="relative overflow-hidden rounded-3xl bg-cover bg-center"
        style={{ backgroundImage: "url('/images/farm-banner.jpg')" }}
      >
        <div className="absolute inset-0 bg-linear-to-l from-[#1b4d24]/95 via-[#1b4d24]/60 to-transparent" />
        <div className="relative px-5 py-8 text-white sm:px-8 md:py-12">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold sm:text-4xl md:text-5xl">مزرعتي</h1>
            <Sprout className="h-10 w-10 text-primary-light" />
          </div>
          <p className="mt-3 text-lg text-white/90">كل معلومات أرضك ومحاصيلك في مكان واحد</p>
          <div className="mt-3 h-1 w-40 rounded-full bg-linear-to-l from-amber-400 to-transparent" />
        </div>
      </section>

      {/* كروت الإحصائيات */}
      <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {stats.map(({ icon: Icon, label, value, sub }) => (
          <Card key={label} className="flex flex-col items-start gap-2 sm:flex-row sm:items-center sm:gap-4">
            <div className="grid h-14 w-14 shrink-0 place-items-center rounded-2xl bg-primary-light/15">
              <Icon className="h-8 w-8 text-primary" />
            </div>
            <div>
              <p className="text-sm text-gray-500">{label}</p>
              <p className="text-xl font-extrabold text-gray-900 sm:text-2xl">{value}</p>
              {sub && <p className="text-xs text-gray-400">{sub}</p>}
            </div>
          </Card>
        ))}
      </section>

      {/* الصف الرئيسي */}
      <section className="grid gap-6 lg:grid-cols-5">
        {/* يمين: المحصول الحالي + معلومة */}
        <div className="space-y-6 lg:col-span-3">
          {/* كارت المحصول الحالي */}
          <Card className="overflow-hidden p-0">
            <div className="grid md:grid-cols-2">
              <div className="p-5 md:order-1">
                <CardTitle icon={Sprout}>المحصول المزروع حالياً</CardTitle>
                <div className="my-6 flex items-center gap-3">
                  <Wheat className="h-12 w-12 text-amber-500" />
                  <span className="text-4xl font-extrabold text-primary">القمح</span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="flex items-center gap-2">
                    <Warehouse className="h-6 w-6 text-primary" />
                    <div>
                      <p className="text-gray-500">الحقل الرئيسي</p>
                      <p className="font-bold">6 فدان</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <CalendarDays className="h-6 w-6 text-primary" />
                    <div>
                      <p className="text-gray-500">تاريخ الزراعة</p>
                      <p className="font-bold">15 نوفمبر</p>
                    </div>
                  </div>
                </div>

                <div className="mt-4 flex items-center justify-center gap-2 rounded-xl bg-primary-light/20 py-3 text-sm font-semibold text-primary">
                  <Sprout className="h-5 w-5" />
                  مرحلة الإنبات
                </div>
              </div>

              <div
                className="min-h-56 bg-cover bg-center md:order-2"
                style={{ backgroundImage: "url('/images/wheat.jpg')" }}
              />
            </div>
          </Card>

          {/* معلومة عن مزرعتك */}
          <div className="flex items-center justify-between gap-4 rounded-2xl bg-amber-50 p-6 shadow-sm">
            <div>
              <h3 className="mb-3 flex items-center gap-2 text-lg font-bold text-amber-800">
                <Lightbulb className="h-5 w-5 text-amber-500" />
                معلومة عن مزرعتك
              </h3>
              <p className="leading-relaxed text-gray-700">
                آخر محصول بقولي مسجل عندك هو <b>الفول</b> في موسم 2024.
              </p>
            </div>
            <Wheat className="hidden h-24 w-24 shrink-0 text-amber-500/70 sm:block" />
          </div>

          {/* إجراءات سريعة */}
          <Card>
            <CardTitle icon={Zap}>إجراءات سريعة</CardTitle>
            <div className="grid gap-3 sm:grid-cols-3">
              {actions.map(({ icon: Icon, label }) => (
                <button
                  key={label}
                  className="flex items-center justify-center gap-2 rounded-xl border border-primary/10 bg-cream px-4 py-3 text-sm font-semibold text-gray-800 transition hover:border-primary-light hover:bg-primary-light/15"
                >
                  <Icon className="h-5 w-5 text-primary" />
                  {label}
                </button>
              ))}
            </div>
          </Card>
        </div>

        {/* شمال: السجل + الحقول */}
        <div className="space-y-6 lg:col-span-2">
          {/* سجل المواسم */}
          <Card>
            <CardTitle icon={History}>سجل المواسم السابقة</CardTitle>
            <ul className="relative space-y-3">
              {history.map((h) => (
                <li
                  key={h.year}
                  className="flex items-center justify-between border-b border-gray-100 pb-3 last:border-0"
                >
                  <div className="flex items-center gap-3">
                    <Wheat className="h-6 w-6 text-amber-500" />
                    <span className="font-bold">
                      {h.crop} – {h.year}
                    </span>
                  </div>
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      h.current ? 'bg-primary-light/20 text-primary' : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {h.badge}
                  </span>
                </li>
              ))}
            </ul>
            <button className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-primary-light/20 py-3 text-sm font-semibold text-primary transition hover:bg-primary-light/30">
              <ArrowLeft className="h-4 w-4" />
              عرض المزيد
            </button>
          </Card>

          {/* معلومات الحقول */}
          <Card>
            <CardTitle icon={MapPin}>معلومات الحقول</CardTitle>
            <ul>
              {fields.map((f) => (
                <li
                  key={f.name}
                  className="flex items-center justify-between border-b border-gray-100 py-3 last:border-0"
                >
                  <div>
                    <p className="font-bold text-gray-900">{f.name}</p>
                    <p className="text-sm text-gray-500">{f.info}</p>
                  </div>
                  <Leaf className="h-9 w-9 text-primary-light" />
                </li>
              ))}
            </ul>
          </Card>
        </div>
      </section>

      {/* آخر تحديث */}
      <div className="flex w-fit items-center gap-3 rounded-full bg-primary-light/15 px-6 py-3 text-sm text-gray-700">
        <RefreshCw className="h-5 w-5 text-primary" />
        آخر تحديث: 13 نوفمبر 2026 – 10:30 ص
      </div>
    </main>
  )
}