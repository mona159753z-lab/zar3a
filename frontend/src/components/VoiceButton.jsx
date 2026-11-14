import { Mic } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function VoiceButton() {
  return (
    <Link
      to="/assistant"
      aria-label="تحدث مع مساعد زرعة"
      title="تحدث مع مساعد زرعة"
      className="fixed bottom-5 left-5 z-50 flex items-center gap-2 rounded-full bg-primary px-4 py-3 text-white shadow-xl shadow-primary/40 transition hover:scale-105 hover:bg-primary/90 sm:bottom-8 sm:left-8 sm:px-5"
    >
      <span className="relative grid h-10 w-10 place-items-center rounded-full bg-white/20">
        <span className="absolute inset-0 animate-ping rounded-full bg-primary-light/60" />
        <Mic className="relative h-6 w-6" />
      </span>
      <span className="hidden text-sm font-bold sm:block">اسأل زرعة</span>
    </Link>
  )
}