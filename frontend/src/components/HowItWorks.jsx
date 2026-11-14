import { ChevronLeft } from 'lucide-react'

const steps = [
  { img: '/images/map.jpg', title: 'حدد أرضك على الخريطة', desc: 'وأدخل بيانات موقعها' },
  { img: '/images/soil.jpg', title: 'أدخل بيانات التربة والمياه', desc: 'للحصول على تحليل دقيق' },
  { img: '/images/analysis.jpg', title: 'احصل على التوصيات', desc: 'لتحسين إنتاجيتك' },
  { img: '/images/step4.jpg', title: 'ابدأ في تطبيق الخطة', desc: 'وحقق أفضل النتائج' },
]

export default function HowItWorks() {
  return (
    <section className="mx-auto max-w-7xl px-4 py-16">
      <div className="mb-12 flex items-center gap-4">
        <div className="h-px flex-1 bg-primary-light" />
        <h2 className="text-2xl font-bold text-primary">
          كيف تعمل منصة <span dir="ltr">زرعة</span> ؟
        </h2>
        <div className="h-px flex-1 bg-primary-light" />
      </div>

      <div className="flex flex-col items-center gap-6 md:flex-row md:items-stretch">
        {steps.map((s, i) => (
          <div key={s.title} className="flex flex-1 items-center gap-4">
            <div className="relative w-full rounded-2xl bg-white p-3 pt-6 text-center shadow-md">
              <span className="absolute -top-4 left-1/2 grid h-8 w-8 -translate-x-1/2 place-items-center rounded-full bg-primary font-bold text-white">
                {i + 1}
              </span>
              <img src={s.img} alt={s.title} className="h-36 w-full rounded-xl object-cover" />
              <h3 className="mt-3 font-bold text-primary">{s.title}</h3>
              <p className="text-sm text-gray-500">{s.desc}</p>
            </div>

            {i < steps.length - 1 && (
              <ChevronLeft className="hidden shrink-0 text-primary md:block" />
            )}
          </div>
        ))}
      </div>
    </section>
  )
}