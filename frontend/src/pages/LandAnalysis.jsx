import { useNavigate } from 'react-router-dom'
import {
  Sprout, CloudRain, Thermometer, Sun, CheckCircle2, Droplet,
  ChevronLeft, FlaskConical, Lightbulb, Mountain, Leaf,
} from 'lucide-react'

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

function CircleProgress({ value }) {
  const r = 45
  const c = 2 * Math.PI * r
  return (
    <div className="relative h-28 w-28 sm:h-32 sm:w-32">
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
        className="absolute inset-0 flex items-center justify-center text-2xl font-extrabold text-gray-900 sm:text-3xl"
      >
        {value}%
      </span>
    </div>
  )
}

function CardTitle({ icon: Icon, title, color = 'text-primary' }) {
  return (
    <div className="flex items-center gap-2">
      <Icon className={`h-6 w-6 sm:h-7 sm:w-7 ${color}`} />
      <h3 className={`text-base font-bold sm:text-lg ${color}`}>{title}</h3>
    </div>
  )
}

export default function LandAnalysis() {
  const navigate = useNavigate()

  return (
    <main className="mx-auto w-full max-w-7xl space-y-5 overflow-x-hidden px-4 pb-16 pt-24 sm:space-y-6 sm:px-6 sm:pt-28 lg:px-8">
      {/* البانر */}
      <section
        className="relative overflow-hidden rounded-3xl bg-cover bg-center"
        style={{ backgroundImage: "url('/images/land-banner.jpg')" }}
      >
        <div className="absolute inset-0 bg-linear-to-l from-[#1b6b2a]/95 via-[#1b6b2a]/50 to-transparent" />
        <div className="relative flex items-center gap-4 px-5 py-8 text-white sm:gap-5 sm:px-8 md:py-12">
          <Sprout className="h-12 w-12 shrink-0 sm:h-16 sm:w-16" strokeWidth={1.4} />
          <div>
            <h1 className="text-3xl font-extrabold sm:text-4xl md:text-5xl">تحليل الأرض</h1>
            <p className="mt-2 text-base text-white/90 sm:text-lg">معرفة حالة أرضك .. لزراعة أفضل</p>
            <div className="mt-3 h-1 w-48 max-w-full rounded-full bg-linear-to-l from-amber-400 to-transparent sm:w-64" />
          </div>
        </div>
      </section>

      {/* الكروت الأربعة */}
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-3xl bg-linear-to-b from-sky-50 to-white p-4 shadow-sm sm:p-5">
          <CardTitle icon={Droplet} title="ميزانية المياه" color="text-sky-600" />
          <div className="mt-4 flex items-center justify-between gap-3">
            <Droplet className="h-16 w-16 fill-sky-300 text-sky-500 sm:h-20 sm:w-20" strokeWidth={1.2} />
            <div className="text-center">
              <p dir="ltr" className="text-3xl font-extrabold text-gray-900 sm:text-4xl">{data.water.left}%</p>
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

        <div className="rounded-3xl bg-linear-to-b from-amber-50 to-white p-4 shadow-sm sm:p-5">
          <CardTitle icon={Thermometer} title="درجة الحرارة" color="text-red-600" />
          <div className="mt-4 flex items-center justify-between gap-3">
            <Sun className="h-16 w-16 fill-amber-400 text-amber-400 sm:h-20 sm:w-20" strokeWidth={1.2} />
            <p dir="ltr" className="text-4xl font-extrabold text-gray-900 sm:text-5xl">{data.temp.value}°C</p>
          </div>
          <p className="mt-4 flex items-center gap-1.5 text-sm text-gray-600">
            <CheckCircle2 className="h-5 w-5 text-primary-light" />
            {data.temp.note}
          </p>
        </div>

        <div className="rounded-3xl bg-linear-to-b from-sky-50 to-white p-4 shadow-sm sm:p-5">
          <CardTitle icon={CloudRain} title="الأمطار" color="text-sky-600" />
          <div className="mt-4 flex items-center justify-between gap-3">
            <CloudRain className="h-16 w-16 text-slate-400 sm:h-20 sm:w-20" strokeWidth={1.2} />
            <div className="text-center">
              <p className="text-2xl font-extrabold text-gray-900 sm:text-3xl">{data.rain.level}</p>
              <p className="mt-1 text-sm text-gray-600">{data.rain.since}</p>
            </div>
          </div>
        </div>

        <div className="rounded-3xl bg-linear-to-b from-green-50 to-white p-4 shadow-sm sm:p-5">
          <CardTitle icon={Sprout} title="حالة التربة" />
          <div className="mt-3 flex justify-center">
            <CircleProgress value={data.soilScore} />
          </div>
          <p className="mt-3 rounded-full bg-green-100 py-2 text-center text-sm font-bold text-primary">
            تربة صحية وجيدة
          </p>
        </div>
      </section>

      {/* الجزء السفلي */}
      <section className="grid gap-4 lg:grid-cols-5">
        <div className="rounded-3xl bg-white p-4 shadow-sm sm:p-5 lg:col-span-3">
          <CardTitle icon={Lightbulb} title="توصياتنا لك" />
          <div className="mt-4 flex flex-col items-center gap-4 rounded-2xl bg-green-50 p-4 sm:flex-row sm:p-5">
            <div className="flex-1 text-center">
              <p className="text-base font-bold text-gray-800 sm:text-lg">{data.recommendation.intro}</p>
              <p className="mt-1 text-xl font-extrabold text-primary sm:text-2xl">
                {data.recommendation.crops}
              </p>
              <p className="mt-2 text-sm text-gray-600">{data.recommendation.reason}</p>
            </div>
            <img
              src="/images/planet.jpg"
              alt="نبتة"
              className="h-32 w-full rounded-2xl object-cover sm:w-40"
            />
          </div>
          <button
            onClick={() => navigate('/crop-cycles')}
            className="mx-auto mt-5 flex w-full items-center justify-center gap-2 rounded-full bg-primary px-6 py-3 text-base font-bold text-white shadow-lg transition hover:scale-105 hover:bg-primary/90 sm:w-auto sm:px-16 sm:text-lg"
          >
            عرض الخطة التفصيلية
            <Sprout className="h-5 w-5" />
          </button>
        </div>

        <div className="rounded-3xl bg-white p-4 shadow-sm sm:p-5 lg:col-span-2">
          <CardTitle icon={FlaskConical} title="بيانات التربة" />
          <div className="mt-4 flex items-center gap-4">
            <ul className="flex-1 divide-y divide-gray-100">
              {data.soil.map(({ icon: Icon, label, value, color }) => (
                <li key={label} className="flex items-center justify-between gap-2 py-3 text-sm">
                  <span className="flex items-center gap-2 text-gray-700">
                    {Icon ? (
                      <Icon className={`h-5 w-5 shrink-0 ${color}`} />
                    ) : (
                      <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-slate-800 text-[10px] font-bold text-white">
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
              src="/images/soil2.jpg"
              alt="تربة"
              className="hidden h-44 w-36 rounded-2xl object-cover shadow-md sm:block"
            />
          </div>
        </div>
      </section>
    </main>
  )
}