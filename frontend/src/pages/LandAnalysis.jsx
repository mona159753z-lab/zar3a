import { useNavigate } from 'react-router-dom'
import {
  Sprout, CloudRain, Thermometer, Sun, CheckCircle2, Droplet,
  ChevronLeft, FlaskConical, Lightbulb, Mountain, Leaf,
} from 'lucide-react'

/* ====== البيانات (بعدين نربطها بـ NASA POWER API) ====== */
const data = {
  soilScore: 78,
  rain: { level: 'خفيفة', since: 'منذ يومين' },
  temp: { value: 28, note: 'مناسبة للزراعة' },
  water: { left: 70 },
  soil: [
    { icon: Mountain, label: 'نوع التربة', value: 'طينية رملية', color: 'text-amber-900' },
    { icon: Droplet, label: 'درجة الحموضة (pH)', value: '6.8', color: 'text-sky-500' },
    { icon: Leaf, label: 'مستوى المادة العضوية', value: '2.5%', color: 'text-primary-light' },
    { icon: null, label: 'مستوى النيتروجين', value: 'متوسط' },
  ],
  recommendation: {
    intro: 'نوصي بزراعة محاصيل محسنة للتربة مثل:',
    crops: 'البقوليات أو البرسيم',
    reason: 'لتحسين خصوبة التربة وزيادة محتواها من النيتروجين',
  },
}

/* ====== دائرة النسبة ====== */
function CircleProgress({ value }) {
  const r = 45
  const c = 2 * Math.PI * r
  return (
    <div className="relative h-32 w-32">
      <svg viewBox="0 0 100 100" className="-rotate-90">
        <circle cx="50" cy="50" r={r} fill="none" stroke="#e5e7eb" strokeWidth="8" />
        <circle
          cx="50" cy="50" r={r} fill="none" stroke="#2d6a2f" strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={c - (c * value) / 100}
        />
      </svg>
      <span
        dir="ltr"
        className="absolute inset-0 flex items-center justify-center text-3xl font-extrabold text-gray-900"
      >
        {value}%
      </span>
    </div>
  )
}

/* ====== كارت عنوان صغير ====== */
function CardTitle({ icon: Icon, title, color = 'text-primary' }) {
  return (
    <div className="flex items-center gap-2">
      <Icon className={`h-7 w-7 ${color}`} />
      <h3 className={`text-lg font-bold ${color}`}>{title}</h3>
    </div>
  )
}

/* ====== الصفحة ====== */
export default function LandAnalysis() {
  const navigate = useNavigate()

  return (
    <main className="mx-auto max-w-7xl space-y-6 px-4 pb-16 pt-28 md:px-8">
      {/* البانر */}
      <section
        className="relative overflow-hidden rounded-3xl bg-cover bg-center"
        style={{ backgroundImage: "url('/images/land-banner.jpg')" }}
      >
        <div className="absolute inset-0 bg-linear-to-l from-[#1b6b2a]/95 via-[#1b6b2a]/50 to-transparent" />
        <div className="relative flex items-center gap-5 px-8 py-10 text-white md:py-12">
          <Sprout className="h-16 w-16 shrink-0" strokeWidth={1.4} />
          <div>
            <h1 className="text-4xl font-extrabold md:text-5xl">تحليل الأرض</h1>
            <p className="mt-2 text-lg text-white/90">معرفة حالة أرضك .. لزراعة أفضل</p>
            <div className="mt-3 h-1 w-64 max-w-full rounded-full bg-linear-to-l from-amber-400 to-transparent" />
          </div>
        </div>
      </section>

      {/* الكروت الأربعة (أول كارت يمين) */}
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* ميزانية المياه */}
        <div className="rounded-3xl bg-linear-to-b from-sky-50 to-white p-5 shadow-sm">
          <CardTitle icon={Droplet} title="ميزانية المياه" color="text-sky-600" />
          <div className="mt-4 flex items-center justify-between gap-3">
            <Droplet className="h-20 w-20 fill-sky-300 text-sky-500" strokeWidth={1.2} />
            <div className="text-center">
              <p dir="ltr" className="text-4xl font-extrabold text-gray-900">{data.water.left}%</p>
              <p className="mt-1 text-sm text-gray-600">متبقي من الميزانية</p>
            </div>
          </div>
          <button
            onClick={() => navigate('/water')}
            className="mt-4 flex w-full items-center justify-center gap-1 rounded-full border border-gray-200 bg-white py-2 text-sm font-semibold text-gray-800 transition hover:bg-sky-50"
          >
            تفاصيل الاستهلاك
            <ChevronLeft className="h-4 w-4" />
          </button>
        </div>

        {/* درجة الحرارة */}
        <div className="rounded-3xl bg-linear-to-b from-amber-50 to-white p-5 shadow-sm">
          <CardTitle icon={Thermometer} title="درجة الحرارة" color="text-red-600" />
          <div className="mt-4 flex items-center justify-between gap-3">
            <Sun className="h-20 w-20 fill-amber-400 text-amber-400" strokeWidth={1.2} />
            <p dir="ltr" className="text-5xl font-extrabold text-gray-900">{data.temp.value}°C</p>
          </div>
          <p className="mt-4 flex items-center gap-1.5 text-sm text-gray-600">
            <CheckCircle2 className="h-5 w-5 text-primary-light" />
            {data.temp.note}
          </p>
        </div>

        {/* الأمطار */}
        <div className="rounded-3xl bg-linear-to-b from-sky-50 to-white p-5 shadow-sm">
          <CardTitle icon={CloudRain} title="الأمطار" color="text-sky-600" />
          <div className="mt-4 flex items-center justify-between gap-3">
            <CloudRain className="h-20 w-20 text-slate-400" strokeWidth={1.2} />
            <div className="text-center">
              <p className="text-3xl font-extrabold text-gray-900">{data.rain.level}</p>
              <p className="mt-1 text-sm text-gray-600">{data.rain.since}</p>
            </div>
          </div>
        </div>

        {/* حالة التربة */}
        <div className="rounded-3xl bg-linear-to-b from-green-50 to-white p-5 shadow-sm">
          <CardTitle icon={Sprout} title="حالة التربة" />
          <div className="mt-3 flex justify-center">
            <CircleProgress value={data.soilScore} />
          </div>
          <p className="mt-3 rounded-full bg-green-100 py-2 text-center text-sm font-bold text-primary">
            تربة صحية وجيدة
          </p>
        </div>
      </section>

      {/* الجزء السفلي: التوصيات يمين، بيانات التربة شمال */}
      <section className="grid gap-4 lg:grid-cols-5">
        {/* توصياتنا لك */}
        <div className="rounded-3xl bg-white p-5 shadow-sm lg:col-span-3">
          <CardTitle icon={Lightbulb} title="توصياتنا لك" />
          <div className="mt-4 flex flex-col items-center gap-4 rounded-2xl bg-green-50 p-5 sm:flex-row">
            <div className="flex-1 text-center">
              <p className="text-lg font-bold text-gray-800">{data.recommendation.intro}</p>
              <p className="mt-1 text-2xl font-extrabold text-primary">
                {data.recommendation.crops}
              </p>
              <p className="mt-2 text-sm text-gray-600">{data.recommendation.reason}</p>
            </div>
            <img
              src="/images/sprout-soil.jpg"
              alt="نبتة"
              className="h-32 w-40 rounded-2xl object-cover"
            />
          </div>
          <button
            onClick={() => navigate('/crop-cycles')}
            className="mx-auto mt-5 flex items-center justify-center gap-2 rounded-full bg-primary px-16 py-3 text-lg font-bold text-white shadow-lg transition hover:scale-105 hover:bg-primary/90"
          >
            عرض الخطة التفصيلية
            <Sprout className="h-5 w-5" />
          </button>
        </div>

        {/* بيانات التربة */}
        <div className="rounded-3xl bg-white p-5 shadow-sm lg:col-span-2">
          <CardTitle icon={FlaskConical} title="بيانات التربة" />
          <div className="mt-4 flex items-center gap-4">
            <ul className="flex-1 divide-y divide-gray-100">
              {data.soil.map(({ icon: Icon, label, value, color }) => (
                <li key={label} className="flex items-center justify-between gap-2 py-3 text-sm">
                  <span className="flex items-center gap-2 text-gray-700">
                    {Icon ? (
                      <Icon className={`h-5 w-5 ${color}`} />
                    ) : (
                      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-800 text-[10px] font-bold text-white">
                        N
                      </span>
                    )}
                    {label}
                  </span>
                  <span className="font-bold text-gray-900">{value}</span>
                </li>
              ))}
            </ul>
            <img
              src="/images/soil-plant.jpg"
              alt="تربة"
              className="hidden h-44 w-36 rounded-2xl object-cover shadow-md sm:block"
            />
          </div>
        </div>
      </section>
    </main>
  )
}