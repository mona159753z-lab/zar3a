import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Leaf, Lightbulb, Bug, Sprout, CalendarDays, Package,
  Mic, Send, Smile, Keyboard, CheckCircle2, CheckCheck, User, Sparkles, Loader2
} from 'lucide-react'

const topics = [
  { icon: Sprout, label: 'أفضل المحاصيل لمنطقتي' },
  { icon: Bug, label: 'مكافحة الآفات والأمراض' },
  { icon: Package, label: 'أنواع الأسمدة المناسبة' },
  { icon: CalendarDays, label: 'مواعيد الزراعة والحصاد' },
]

const time = () =>
  new Date().toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })

function Bubble({ m }) {
  const isUser = m.from === 'user'
  return (
    <div className={`flex items-end gap-3 ${isUser ? '' : 'flex-row'}`}>
      {isUser ? (
        <div className="grid h-12 w-12 shrink-0 place-items-center rounded-full bg-primary text-white">
          <User className="h-7 w-7" />
        </div>
      ) : (
        <img src="/images/bot.png" alt="زرعة" className="h-12 w-12 shrink-0 rounded-full border-2 border-white bg-primary-light/30 object-cover shadow" />
      )}
      <div className={`max-w-[75%] ${isUser ? '' : ''}`}>
        <div className={`whitespace-pre-line rounded-2xl px-5 py-3 leading-relaxed ${isUser ? 'rounded-br-sm bg-primary-light/25 text-gray-900' : 'rounded-bl-sm bg-gray-100 text-gray-800'}`}>
          {m.text}
        </div>
        <p className="mt-1 flex items-center gap-1 px-1 text-xs text-gray-400">
          {m.time}
          {isUser && <CheckCheck className="h-4 w-4 text-primary-light" />}
        </p>
      </div>
    </div>
  )
}

function Typing() {
  return (
    <div className="flex items-end gap-3">
      <img src="/images/bot-avatar.png" alt="زرعة" className="h-12 w-12 shrink-0 rounded-full border-2 border-white bg-primary-light/30 object-cover shadow" />
      <div className="flex gap-1.5 rounded-2xl rounded-bl-sm bg-gray-100 px-5 py-4">
        {[0, 150, 300].map((d) => (
          <span key={d} className="h-2.5 w-2.5 animate-bounce rounded-full bg-primary-light" style={{ animationDelay: `${d}ms` }} />
        ))}
      </div>
    </div>
  )
}

export default function Assistant() {
  const [messages, setMessages] = useState([])
  const [text, setText] = useState('')
  const [typing, setTyping] = useState(false)
  const [listening, setListening] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [isDone, setIsDone] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  
  const bottomRef = useRef(null)
  const recRef = useRef(null)
  const audioRef = useRef(null)
  const navigate = useNavigate()

  const API_BASE = "https://zar3a-api-production.up.railway.app/api/voice"

  const playAudio = (base64, mime, fallbackText, speakInBrowser) => {
    if (base64 && mime) {
      const audioSrc = `data:${mime};base64,${base64}`
      if (audioRef.current) {
        audioRef.current.src = audioSrc
        audioRef.current.play().catch(e => console.log("Audio blocked:", e))
      }
    } else if (speakInBrowser && fallbackText) {
      const utterance = new SpeechSynthesisUtterance(fallbackText)
      utterance.lang = 'ar-EG'
      window.speechSynthesis.speak(utterance)
    }
  }

  // 1. استرجاع الجلسة أو بدء واحدة جديدة
  useEffect(() => {
    const initSession = async () => {
      setTyping(true)
      const savedSessionId = localStorage.getItem('zar3a_session_id')
      
      try {
        if (savedSessionId) {
          // محاولة استرجاع الجلسة القديمة من الباك إند
          const res = await fetch(`${API_BASE}/session/${savedSessionId}`)
          if (res.ok) {
            const data = await res.json()
            setSessionId(data.session_id)
            setIsDone(data.done)
            // لو الجلسة موجودة، بنعرض رسالة ترحيب تانية عشان مفيش تاريخ رسايل محفوظ
            setMessages([{ id: Date.now(), from: 'bot', text: 'أهلاً بيك تاني! كملنا كلامنا من حيث ما وقفنا. إيه اللي عايز تضيفه؟', time: time() }])
            setTyping(false)
            return
          }
        }
        
        // لو مفيش جلسة قديمة أو انتهت، نبدأ واحدة جديدة
        const res = await fetch(`${API_BASE}/start`, { method: 'POST' })
        const data = await res.json()
        
        setSessionId(data.session_id)
        localStorage.setItem('zar3a_session_id', data.session_id) // حفظ الجلسة في المتصفح
        setMessages([{ id: Date.now(), from: 'bot', text: data.reply_text, time: time() }])
        playAudio(data.audio_base64, data.audio_mime, data.reply_text, data.speak_in_browser)
        
      } catch (err) {
        console.error(err)
        setMessages([{ id: Date.now(), from: 'bot', text: 'معلش، في مشكلة في الاتصال بالسيرفر. تأكد إن الباك إند شغال.', time: time() }])
      } finally {
        setTyping(false)
      }
    }
    initSession()
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, typing])

  const send = async (value) => {
    const q = (value ?? text).trim()
    if (!q || isDone) return

    setMessages((m) => [...m, { id: Date.now(), from: 'user', text: q, time: time() }])
    setText('')
    setTyping(true)

    try {
      const response = await fetch(`${API_BASE}/text-turn`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: q, session_id: sessionId })
      })

      if (!response.ok) throw new Error("Server Error")
      
      const data = await response.json()
      if (data.session_id) setSessionId(data.session_id)
      if (data.done) setIsDone(true)

      setMessages((m) => [...m, { id: Date.now() + 1, from: 'bot', text: data.reply_text, time: time() }])
      playAudio(data.audio_base64, data.audio_mime, data.reply_text, data.speak_in_browser)

    } catch (error) {
      setMessages((m) => [...m, { id: Date.now() + 1, from: 'bot', text: 'معلش، في مشكلة في الاتصال.', time: time() }])
    } finally {
      setTyping(false)
    }
  }

  // 2. دالة تحليل الأرض والانتقال للصفحة التالية
  const handleAnalyze = async () => {
    setIsAnalyzing(true)
    try {
      const res = await fetch(`${API_BASE}/session/${sessionId}/analyze`, { method: 'POST' })
      if (!res.ok) throw new Error("فشل التحليل")
      
      const data = await res.json()
      // مسح الجلسة من المتصفح عشان لو حب يبدأ من جديد
      localStorage.removeItem('zar3a_session_id')
      
      // الانتقال لصفحة الدورات مع تمرير بيانات التحليل
      navigate('/crop-cycles', { state: { analysis: data.analysis } })
      
    } catch (error) {
      alert("حصلت مشكلة أثناء تحليل الأرض. تأكد إن الباك إند شغال.")
    } finally {
      setIsAnalyzing(false)
    }
  }

  const toggleMic = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) return alert('المتصفح ده مش بيدعم التعرف على الصوت. جرّبي Chrome أو Edge.')
    if (listening) return recRef.current?.stop()

    const rec = new SR()
    rec.lang = 'ar-EG'
    rec.interimResults = false
    rec.onstart = () => setListening(true)
    rec.onend = () => setListening(false)
    rec.onerror = () => setListening(false)
    rec.onresult = (e) => send(e.results[0][0].transcript)
    recRef.current = rec
    rec.start()
  }

  return (
    <main className="mx-auto max-w-7xl px-4 pb-12 pt-28 md:px-8">
      <audio ref={audioRef} className="hidden" />
      <div className="grid gap-6 lg:grid-cols-5">
        <aside className="relative flex flex-col justify-between overflow-hidden rounded-3xl bg-primary-light/20 bg-cover bg-center order-last lg:order-none lg:col-span-2" style={{ backgroundImage: "url('/images/assistant-bg.jpg')" }}>
          <div className="relative z-10 p-5">
            <div className="mr-auto max-w-[75%] rounded-3xl rounded-tr-sm bg-white p-5 shadow-lg">
              <h2 className="flex items-center gap-2 text-2xl font-extrabold text-primary">
                <Leaf className="h-6 w-6 text-primary-light" /> أهلاً بك في مساعد زرعة!
              </h2>
              <p className="mt-2 text-sm text-gray-600">أنا هنا لمساعدتك في أي استفسار عن الزراعة 😊</p>
            </div>
          </div>
          <img src="/images/bot.png" alt="مساعد زرعة" className="relative z-0 mx-auto -mt-6 h-48 w-auto sm:h-72 object-contain drop-shadow-xl" />
          <div className="relative z-10 mx-5 mb-4 rounded-3xl bg-cream/95 p-5 shadow-lg backdrop-blur">
            <h3 className="mb-3 flex items-center gap-2 font-bold text-gray-900">
              <Lightbulb className="h-5 w-5 text-amber-500" /> ماذا يمكنك أن تسأل؟
            </h3>
            <div className="grid grid-cols-2 gap-3">
              {topics.map(({ icon: Icon, label }) => (
                <button key={label} onClick={() => send(label)} disabled={isDone} className="flex flex-col items-center gap-2 rounded-xl bg-white p-3 text-center text-sm font-semibold text-gray-800 shadow-sm transition hover:-translate-y-0.5 hover:bg-primary-light/15 hover:shadow disabled:opacity-50">
                  <Icon className="h-6 w-6 text-primary" /> {label}
                </button>
              ))}
            </div>
          </div>
          <div className="relative z-10 mx-5 mb-5 rounded-full bg-primary px-6 py-3 text-center text-sm font-semibold text-white">
            مع <span dir="ltr">ZAR3A</span>.. زراعة أسهل ومستقبل أفضل
          </div>
        </aside>

        <section className="flex flex-col overflow-hidden rounded-3xl border border-primary/5 bg-white shadow-sm lg:col-span-3">
          <header className="flex items-center gap-3 bg-primary px-6 py-5 text-white">
            <Leaf className="h-9 w-9 text-primary-light" />
            <h1 className="text-2xl font-extrabold">مساعد زرعة</h1>
          </header>

          <div className="flex-1 space-y-5 overflow-y-auto bg-cream/60 p-4 sm:p-6" style={{ maxHeight: 460, minHeight: 300 }}>
            {messages.map((m) => (
              <div key={m.id}><Bubble m={m} /></div>
            ))}
            {typing && <Typing />}
            <div ref={bottomRef} />
            
            {/* زرار التحليل يظهر لما الحوار يخلص */}
            {isDone && (
              <div className="flex justify-center mt-6">
                <button 
                  onClick={handleAnalyze}
                  disabled={isAnalyzing}
                  className="flex items-center gap-2 rounded-full bg-primary px-8 py-4 text-lg font-bold text-white shadow-lg hover:bg-primary/90 transition animate-bounce disabled:animate-none disabled:opacity-50"
                >
                  {isAnalyzing ? <Loader2 className="h-6 w-6 animate-spin" /> : <Sparkles className="h-6 w-6" />}
                  {isAnalyzing ? 'جاري التحليل...' : 'تحليل الأرض الآن'}
                </button>
              </div>
            )}
          </div>

          <div className="flex items-center justify-center gap-4 bg-cream/60 px-6 pb-4">
            <div className="flex w-full max-w-md flex-col items-center gap-3 rounded-3xl bg-primary-light/20 px-6 py-5">
              <div className="flex items-center gap-4">
                <span className="text-3xl text-primary-light/70">)))</span>
                <button
                  onClick={toggleMic}
                  disabled={isDone}
                  aria-label="تحدث"
                  className={`grid h-20 w-20 place-items-center rounded-full bg-primary text-white shadow-lg transition hover:scale-105 ${
                    listening ? 'animate-pulse ring-8 ring-primary-light/40' : ''
                  } ${isDone ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <Mic className="h-9 w-9" />
                </button>
                <span className="text-3xl text-primary-light/70">(((</span>
              </div>
              <p className="font-bold text-gray-800">
                {isDone ? 'تم جمع البيانات بنجاح!' : listening ? 'جاري الاستماع...' : 'اضغط على الميكروفون وتحدث الآن'}
              </p>
            </div>
          </div>

          <div className="m-4 mt-0 flex items-center gap-3 rounded-2xl bg-gray-100 p-3">
            <button onClick={() => send()} disabled={isDone} className={`grid h-12 w-12 shrink-0 place-items-center rounded-full bg-primary text-white shadow transition hover:bg-primary/90 ${isDone ? 'opacity-50' : ''}`}>
              <Send className="h-5 w-5 -scale-x-100" />
            </button>
            <input
              value={text}
              disabled={isDone}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && send()}
              placeholder={isDone ? "الحوار انتهى، يمكنك تحليل الأرض الآن" : "أو اكتب سؤالك هنا..."}
              className="h-12 flex-1 rounded-full bg-white px-5 outline-none placeholder:text-gray-400 focus:ring-2 focus:ring-primary-light disabled:bg-gray-200"
            />
            <Smile className="hidden h-7 w-7 text-gray-500 sm:block" />
            <Keyboard className="hidden h-7 w-7 text-gray-500 sm:block" />
          </div>
        </section>
      </div>
    </main>
  )
}