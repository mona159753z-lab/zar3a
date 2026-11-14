import { useLocation, useNavigate } from 'react-router-dom'
import {
  Sprout, Droplet, Mountain, Sun, AlertTriangle, ThumbsUp,
  CheckCircle2, Lightbulb, Repeat,
} from 'lucide-react'

/* ====== البيانات الافتراضية (Fallback) ====== */
const defaultStrategies = [
  {
    key: 'A',
    title: 'الدورة الزراعية الحالية',
    desc: 'الاستمرار في الدورة الزراعية الحالية مع تحسينات بسيطة',
    image: '/images/Crop Rotation.jpg',
    theme: { card: 'from-amber-50 to-white border-amber-200/60', badge: 'bg-amber-600', panel: 'bg-amber-50/70' },
    stats: [
      { icon: Sprout, label: 'المحاصيل المقترحة', value: 'محاصيل الدورة الحالية', color: 'text-primary-light' },
      { icon: Droplet, label: 'احتياجات المياه', value: 'متوسطة', color: 'text-sky-500' },
      { icon: Mountain, label: 'التأثير على التربة', value: 'مستقر', color: 'text-amber-900' },
      { icon: Sun, label: 'الملاءمة المناخية', value: 'عالية', color: 'text-amber-500' },
    ],
    risk: 'احتمالية استنزاف التربة',
    pro: 'سهولة التنفيذ والاستمرارية',
    reason: 'للاستمرار في الزراعة مع مراعاة تحسين بعض الجوانب.',
  },
  {
    key: 'B',
    title: 'تقليل استهلاك المياه',
    desc: 'دورة زراعية تركز على المحاصيل الأقل استهلاكاً للمياه',
    image: '/images/save water.jpg',
    theme: { card: 'from-sky-50 to-white border-sky-200/60', badge: 'bg-sky-600', panel: 'bg-sky-50/70' },
    stats: [
      { icon: Sprout, label: 'المحاصيل المقترحة', value: 'محاصيل قليلة المياه', color: 'text-primary-light' },
      { icon: Droplet, label: 'احتياجات المياه', value: 'منخفضة', color: 'text-sky-500' },
      { icon: Mountain, label: 'التأثير على التربة', value: 'مستقر', color: 'text-amber-900' },
      { icon: Sun, label: 'الملاءمة المناخية', value: 'متوسطة إلى عالية', color: 'text-amber-500' },
    ],
    risk: 'انخفاض العائد المحتمل',
    pro: 'توفير كبير في المياه',
    reason: 'لتحقيق أقصى استفادة من المياه في منطقتك.',
  },
  {
    key: 'C',
    title: 'تحسين التربة ومقاومة التغيرات المناخية',
    desc: 'دورة زراعية تعزز خصوبة التربة وتقلل من تأثر التغيرات المناخية',
    image: '/images/impact soil.jpg',
    theme: { card: 'from-green-50 to-white border-green-200/60', badge: 'bg-primary', panel: 'bg-green-50/70' },
    stats: [
      { icon: Sprout, label: 'المحاصيل المقترحة', value: 'بقوليات + محاصيل تغطية', color: 'text-primary-light' },
      { icon: Droplet, label: 'احتياجات المياه', value: 'متوسطة', color: 'text-sky-500' },
      { icon: Mountain, label: 'التأثير على التربة', value: 'تحسين خصوبة التربة', color: 'text-amber-900' },
      { icon: Sun, label: 'الملاءمة المناخية', value: 'عالية', color: 'text-amber-500' },
    ],
    risk: 'زيادة تكاليف الزراعة',
    pro: 'تربة أكثر خصوبة ومقاومة للجفاف',
    reason: 'لتحسين جودة التربة وضمان استدامة الإنتاج على المدى الطويل.',
  },
]

function StrategyCard({ s, onSelect }) {
  return (
    <article className={`relative flex flex-col rounded-3xl border bg-linear-to-b p-5 pt-8 shadow-sm transition hover:-translate-y-1 hover:shadow-lg ${s.theme.card}`}>
      <span className={`absolute -top-4 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-full px-8 py-2 text-lg font-bold text-white shadow ${s.theme.badge}`}>
        الاستراتيجية <span dir="ltr">{s.key}</span>
      </span>
      <h2 className="mt-2 text-center text-xl font-extrabold text-gray-900">{s.title}</h2>
      <p className="mt-2 text-center text-sm text-gray-600">{s.desc}</p>

      <div className="mt-5 grid grid-cols-1 items-center gap-4 sm:grid-cols-2">
        <ul className="space-y-3">
          {s.stats?.map(({ icon: Icon, label, value, color }) => (
            <li key={label} className="flex items-start gap-2">
              <Icon className={`mt-1 h-5 w-5 shrink-0 ${color}`} />
              <div>
                <p className="text-sm font-bold text-gray-900">{label}</p>
                <p className="text-sm text-gray-600">{value}</p>
              </div>
            </li>
          ))}
        </ul>
        <img src={s.image} alt={s.title} className="aspect-video w-full rounded-2xl object-cover shadow-md sm:aspect-square" />
      </div>

      <div className="mt-5 grid grid-cols-2 gap-3">
        <div className="rounded-xl bg-white/80 p-3 text-sm shadow-sm">
          <p className="mb-1 flex items-center gap-1.5 font-bold text-gray-900">
            <ThumbsUp className="h-4 w-4 text-primary-light" /> المميزات
          </p>
          <p className="flex items-start gap-1 text-xs text-gray-600">
            <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary-light" /> {s.pro}
          </p>
        </div>
        <div className="rounded-xl bg-white/80 p-3 text-sm shadow-sm">
          <p className="mb-1 flex items-center gap-1.5 font-bold text-gray-900">
            <AlertTriangle className="h-4 w-4 text-amber-500" /> المخاطر
          </p>
          <p className="flex items-start gap-1 text-xs text-gray-600">
            <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary-light" /> {s.risk}
          </p>
        </div>
      </div>

      <div className={`mt-3 rounded-xl p-3 text-sm ${s.theme.panel}`}>
        <p className="mb-1 flex items-center gap-1.5 font-bold text-gray-900">
          <CheckCircle2 className="h-4 w-4 text-primary-light" /> سبب التوصية
        </p>
        <p className="flex items-start gap-1.5 text-xs text-gray-600">
          <Lightbulb className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-500" /> {s.reason}
        </p>
      </div>

      <button onClick={() => onSelect(s)} className="mt-auto flex items-center justify-center gap-2 self-center rounded-full bg-primary px-8 py-3 text-base font-bold sm:px-14 sm:text-lg text-white shadow-lg transition hover:scale-105 hover:bg-primary/90" style={{ marginTop: 20 }}>
        لنزرع معا <Sprout className="h-5 w-5" />
      </button>
    </article>
  )
}

export default function CropCycles() {
  const navigate = useNavigate()
  const location = useLocation()

  // استقبال البيانات من صفحة المساعد (لو موجودة)
  const analysisData = location.state?.analysis

  // لو الباك إند رجع استراتيجيات جاهزة في التحليل، هنستخدمها. غير كده هنستخدم الافتراضية.
  const strategiesToRender = analysisData?.strategies || defaultStrategies

  const handleSelect = (s) => {
    navigate('/my-farm')
  }

  return (
    <main className="mx-auto max-w-7xl space-y-10 px-4 pb-16 pt-28 md:px-8">
      <section className="relative overflow-hidden rounded-3xl bg-cover bg-center" style={{ backgroundImage: "url('/images/strategy.jpg')" }}>
        <div className="absolute inset-0 bg-linear-to-l from-[#1b6b2a]/95 via-[#1b6b2a]/60 to-transparent" />
        <div className="relative flex items-center gap-5 px-5 py-8 text-white sm:px-8 md:py-12">
          <Repeat className="h-12 w-12 shrink-0 sm:h-16 sm:w-16" strokeWidth={1.4} />
          <div>
            <h1 className="text-3xl font-extrabold sm:text-4xl md:text-5xl">الدورات الزراعية</h1>
            <p className="mt-2 text-lg text-white/90">
              {analysisData ? `التوصيات المخصصة لأرضك يا ${analysisData.farmer_name || 'مزارعنا'}` : 'اختر الاستراتيجية المناسبة لمزرعتك'}
            </p>
            <div className="mt-3 h-1 w-64 max-w-full rounded-full bg-linear-to-l from-amber-400 to-transparent" />
          </div>
        </div>
      </section>

      <section className="grid gap-10 pt-2 lg:grid-cols-3 lg:gap-6">
        {strategiesToRender.map((s) => (
          <StrategyCard key={s.key || s.id} s={s} onSelect={handleSelect} />
        ))}
      </section>
    </main>
  )
}