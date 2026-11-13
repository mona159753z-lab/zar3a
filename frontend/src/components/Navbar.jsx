
import { User, Menu, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, NavLink } from 'react-router-dom'

const links = [
  { label: 'الرئيسية', to: '/' },
  { label: 'مزرعتي', to: '/my-farm' },
  { label: 'تحليل الأرض', to: '/land-analysis' },
  { label: 'صحة المحاصيل', to: '/crop-health' },
  { label: 'الدورات الزراعية', to: '/crop-cycles' },
  { label: 'مساعد زرعة', to: '/assistant' },
]


export default function Navbar() {
  const [lang, setLang] = useState('ar')
  const [active, setActive] = useState(0)
  const [scrolled, setScrolled] = useState(false)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    onScroll()
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header
      className={`fixed inset-x-0 top-0 z-50 px-4 transition-all duration-300 md:px-8 ${
        scrolled ? 'pt-2' : 'pt-4'
      }`}
    >
      <nav
        className={`mx-auto flex max-w-7xl items-center justify-between rounded-full border px-5 transition-all duration-300 ${
          scrolled
            ? 'h-16 border-primary/10 bg-cream/90 shadow-xl shadow-primary/10 backdrop-blur-xl'
            : 'h-[72px] border-white/40 bg-cream/80 shadow-lg shadow-black/5 backdrop-blur-md'
        }`}
      >
        {/* اللوجو */}
        <a href="/" className="flex shrink-0 items-center">
          <img src="/images/logo.png" alt="ZAR3A" className="h-12 w-auto" />
        </a>

        {/* الروابط (ديسكتوب) */}
        <ul className="hidden items-center gap-1 lg:flex">
  {links.map((l) => (
    <li key={l.label}>
      <NavLink
        to={l.to}
        end
        className={({ isActive }) =>
          `relative rounded-full px-4 py-2 text-sm font-semibold transition-all duration-200 ${
            isActive
              ? 'bg-primary text-white shadow-md shadow-primary/30'
              : 'text-primary/80 hover:bg-primary/10 hover:text-primary'
          }`
        }
      >
        {l.label}
      </NavLink>
    </li>
  ))}
</ul>

        {/* الجزء الشمال */}
        <div className="flex items-center gap-2">
          {/* تبديل اللغة */}
          <div className="hidden items-center rounded-full bg-primary/10 p-1 text-xs font-bold sm:flex">
            {[
              { code: 'ar', label: 'عربي' },
              { code: 'en', label: 'EN' },
            ].map((o) => (
              <button
                key={o.code}
                onClick={() => setLang(o.code)}
                className={`rounded-full px-3 py-1.5 transition-all ${
                  lang === o.code
                    ? 'bg-white text-primary shadow'
                    : 'text-primary/60 hover:text-primary'
                }`}
              >
                {o.label}
              </button>
            ))}
          </div>

          {/* أيقونة الدخول */}
          <button
            aria-label="دخول / إنشاء حساب"
            title="دخول / إنشاء حساب"
            className="grid h-10 w-10 place-items-center rounded-full bg-primary text-white shadow-md shadow-primary/30 transition hover:scale-105 hover:bg-primary/90"
          >
            <User className="h-5 w-5" />
          </button>

          {/* زرار القايمة (موبايل) */}
          <button
            aria-label="القائمة"
            onClick={() => setOpen(!open)}
            className="grid h-10 w-10 place-items-center rounded-full text-primary transition hover:bg-primary/10 lg:hidden"
          >
            {open ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </nav>

      {/* قايمة الموبايل */}
      <div
        className={`mx-auto mt-2 max-w-7xl overflow-hidden rounded-3xl bg-cream/95 shadow-xl backdrop-blur-xl transition-all duration-300 lg:hidden ${
          open ? 'max-h-96 border border-primary/10 opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <ul className="flex flex-col p-3">
          {links.map((l) => (
  <li key={l.label}>
    <NavLink
      to={l.to}
      end
      onClick={() => setOpen(false)}
      className={({ isActive }) =>
        `block rounded-2xl px-4 py-3 text-sm font-semibold transition ${
          isActive ? 'bg-primary text-white' : 'text-primary hover:bg-primary/10'
        }`
      }
    >
      {l.label}
    </NavLink>
  </li>
))}
          
        </ul>
      </div>
    </header>
  )
}