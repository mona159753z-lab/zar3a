
import { Play, ArrowLeft, Satellite } from 'lucide-react'
import { Link } from 'react-router-dom'
export default function Hero() {
  return (
    <section
      className="relative min-h-[620px] bg-cover bg-center"
      style={{ backgroundImage: "url('/images/hero.jpg')" }}
    >
      {/* تدرج أخضر غامق من الشمال */}
      <div className="absolute inset-0 bg-linear-to-r from-[#1b4d24] via-[#1b4d24]/70 to-transparent" />

      {/* المحتوى (على الشمال زي التصميم) */}
      <div className="relative mr-auto flex w-full max-w-2xl px-6 pb-16 pt-36 sm:pb-28 sm:pt-44 md:px-16" dir="rtl">
        <div className="max-w-xl text-white">
          <img
  src="/images/logo2.png"
  alt="ZAR3A"
  className="mb-6 block h-25 w-auto md:-translate-x-60 md:h-32"
/>

          <h1 className="mb-5 text-3xl font-bold md:text-3xl">
            زراعة أذكى .. لمستقبل أكثر استدامة
          </h1>

          <p className="mb-8 text-lg leading-relaxed text-white/90">
            منصة زراعية متكاملة لمساعدة المزارعين في اتخاذ قرارات زراعية أفضل.
          </p>

          <div className="flex flex-wrap gap-4">
            <Link
  to="/my-farm"
  className="flex items-center gap-3 rounded-full bg-primary-light px-8 py-3 font-bold text-white shadow-lg transition hover:bg-primary-light/90"
>
  ابدأ الآن
  <span className="grid h-7 w-7 place-items-center rounded-full bg-white text-primary">
    <ArrowLeft className="h-4 w-4" />
  </span>
</Link>

            <button className="flex items-center gap-3 rounded-full border-2 border-white/80 px-8 py-3 font-bold text-white transition hover:bg-white/10">
              شاهد كيف تعمل المنصة
              <span className="grid h-7 w-7 place-items-center rounded-full bg-primary-light">
                <Play className="h-3 w-3 fill-white" />
              </span>
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}