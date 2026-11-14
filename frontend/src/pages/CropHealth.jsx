import { useRef, useState } from 'react'
import {
  ScanSearch, Image as ImageIcon, Video, Search, CheckCircle2,
  AlertTriangle, Lightbulb, ShieldCheck, Info, Clock, CalendarDays,
  Sprout, UploadCloud, X, Loader2
} from 'lucide-react'

/* ====== مكونات صغيرة ====== */
function Card({ children, className = '' }) {
  return (
    <div className={`rounded-2xl border border-primary/5 bg-white shadow-sm ${className}`}>
      {children}
    </div>
  )
}

/* ====== كارت الرفع ====== */
function UploadCard({ onAnalyze, loading }) {
  const [mode, setMode] = useState('image') // image | video
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef(null)

  const accept = mode === 'image' ? 'image/*' : 'video/*'

  const pickFile = (f) => {
    if (!f) return
    if (preview) URL.revokeObjectURL(preview)
    setFile(f)
    setPreview(URL.createObjectURL(f))
  }

  const clear = () => {
    if (preview) URL.revokeObjectURL(preview)
    setFile(null)
    setPreview(null)
    if (inputRef.current) inputRef.current.value = ''
  }

  const switchMode = (m) => {
    setMode(m)
    clear()
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    pickFile(e.dataTransfer.files?.[0])
  }

  return (
    <Card className="p-6">
      <h2 className="mb-4 text-center text-xl font-bold text-gray-900">أضف صورة أو فيديو</h2>

      <div className="mb-4 grid grid-cols-2 gap-3">
        {[
          { key: 'image', label: 'صورة', icon: ImageIcon },
          { key: 'video', label: 'فيديو', icon: Video },
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => switchMode(key)}
            className={`flex items-center justify-center gap-2 rounded-lg py-3 font-bold transition ${
              mode === key ? 'bg-primary text-white shadow' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Icon className="h-5 w-5" /> {label}
          </button>
        ))}
      </div>

      <div
        onClick={() => !file && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`relative flex min-h-48 cursor-pointer flex-col items-center justify-center overflow-hidden rounded-xl border-2 border-dashed p-4 text-center transition ${
          dragging ? 'border-primary bg-primary-light/10' : 'border-gray-300 bg-gray-50'
        }`}
      >
        {preview ? (
          <>
            {mode === 'image' ? (
              <img src={preview} alt="معاينة" className="max-h-56 rounded-lg object-contain" />
            ) : (
              <video src={preview} controls className="max-h-56 rounded-lg" />
            )}
            <button
              onClick={(e) => { e.stopPropagation(); clear(); }}
              aria-label="إزالة"
              className="absolute left-2 top-2 grid h-8 w-8 place-items-center rounded-full bg-black/60 text-white hover:bg-black/80"
            >
              <X className="h-4 w-4" />
            </button>
          </>
        ) : (
          <>
            <UploadCloud className="mb-3 h-14 w-14 text-gray-400" />
            <p className="font-semibold text-gray-700">{mode === 'image' ? 'اسحب الصورة هنا' : 'اسحب الفيديو هنا'}</p>
            <p className="text-sm text-gray-500">أو اختر من جهازك</p>
          </>
        )}
        <input ref={inputRef} type="file" accept={accept} className="hidden" onChange={(e) => pickFile(e.target.files?.[0])} />
      </div>

      <button
        disabled={!file || loading}
        onClick={() => onAnalyze(file)}
        className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-primary py-3 font-bold text-white shadow transition hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Search className="h-5 w-5" />}
        {loading ? 'جاري التحليل...' : 'تحليل المحصول'}
      </button>
    </Card>
  )
}

/* ====== كارت النتيجة ====== */
function ResultCard({ loading, data, imagePreview }) {
  if (loading) {
    return (
      <Card className="grid min-h-80 place-items-center p-8">
        <div className="text-center">
          <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-primary-light/30 border-t-primary" />
          <p className="font-semibold text-primary">جاري فحص النبات بالذكاء الاصطناعي...</p>
        </div>
      </Card>
    )
  }

  if (!data) {
    return (
      <Card className="grid min-h-80 place-items-center p-8 text-gray-400">
        <div className="text-center">
          <ScanSearch className="mx-auto mb-4 h-16 w-16 opacity-50" />
          <p>ارفع صورة للنبات واضغط تحليل لتظهر النتائج هنا</p>
        </div>
      </Card>
    )
  }

  const { disease_info, top_prediction } = data;
  const confidence = Math.round(top_prediction.confidence * 100);

  return (
    <Card className="overflow-hidden">
      <div className="grid md:grid-cols-2">
        <div className="p-6">
          <div className={`mb-5 flex w-fit items-center gap-2 rounded-full px-5 py-2 font-bold ${confidence > 80 ? 'bg-red-100 text-red-600' : 'bg-amber-100 text-amber-600'}`}>
            <AlertTriangle className="h-5 w-5" />
            {disease_info.name_ar === 'سليم' ? 'النبات سليم' : 'تم اكتشاف مرض على النبات'}
          </div>

          <div className="flex items-center justify-between gap-4">
            <div>
              <h3 className="text-2xl font-extrabold text-gray-900 sm:text-3xl">{disease_info.name_ar}</h3>
              <p className="text-lg text-gray-600" dir="ltr">({disease_info.name})</p>
            </div>
            <img src={imagePreview} alt="Plant" className="h-24 w-24 shrink-0 rounded-full border-4 border-primary object-cover" />
          </div>

          <div className="mt-5 flex items-center gap-3 text-sm">
            <span className="font-semibold text-gray-700">نسبة الثقة: {confidence}%</span>
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-gray-200">
              <div className={`h-full rounded-full ${confidence > 80 ? 'bg-red-500' : 'bg-primary'}`} style={{ width: `${confidence}%` }} />
            </div>
          </div>

          <p className="mt-4 rounded-xl bg-gray-100 p-4 leading-relaxed text-gray-700">
            {disease_info.description}
          </p>
        </div>

        <div className="relative min-h-64 bg-cover bg-center md:order-first" style={{ backgroundImage: `url('${imagePreview}')` }}>
          <div className="absolute right-3 top-3 flex items-center gap-2 rounded-lg bg-primary/90 px-3 py-1.5 text-sm font-bold text-white">
            <CheckCircle2 className="h-4 w-4" /> تحليل ناجح
          </div>
        </div>
      </div>
    </Card>
  )
}

/* ====== الصفحة ====== */
export default function CropHealth() {
  const [loading, setLoading] = useState(false)
  const [resultData, setResultData] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)

  // رابط سيرفر الموديل الجديد (اللي هنشغله على 8002)
  const API_URL = "http://localhost:8002/predict"

  const handleAnalyze = async (file) => {
    if (!file) return;

    setLoading(true)
    setResultData(null)
    setImagePreview(URL.createObjectURL(file))

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        body: formData
      });

      if (!response.ok) throw new Error("فشل الاتصال بالسيرفر");

      const data = await response.json();
      setResultData(data);

    } catch (error) {
      console.error(error);
      alert("حدث خطأ أثناء تحليل الصورة. تأكد من تشغيل سيرفر الموديل.");
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="mx-auto max-w-7xl space-y-6 px-4 pb-16 pt-28 md:px-8">
      <section className="relative overflow-hidden rounded-3xl bg-cover bg-center" style={{ backgroundImage: "url('/images/crop-banner.jpg')" }}>
        <div className="absolute inset-0 bg-linear-to-l from-[#1b4d24] via-[#1b4d24]/90 to-transparent" />
        <div className="relative flex items-center justify-start gap-4 px-5 py-8 text-white sm:px-8 md:py-12">
          <ScanSearch className="h-12 w-12 shrink-0 sm:h-16 sm:w-16" strokeWidth={1.5} />
          <div>
            <h1 className="text-3xl font-extrabold sm:text-4xl md:text-5xl">صحة المحاصيل</h1>
            <p className="mt-2 text-lg text-white/90">تحليل ذكي لنباتتك باستخدام الذكاء الاصطناعي</p>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-5">
        <div className="lg:col-span-2">
          <UploadCard onAnalyze={handleAnalyze} loading={loading} />
        </div>
        <div className="lg:col-span-3">
          <ResultCard loading={loading} data={resultData} imagePreview={imagePreview} />
        </div>
      </section>

      {/* التوصيات والإرشادات - بتظهر بس لو فيه نتيجة */}
      {resultData && (
        <section className="grid gap-6 lg:grid-cols-5">
          <Card className="p-6 lg:col-span-3">
            <h2 className="mb-5 flex items-center gap-2 text-xl font-bold text-gray-900">
              <Lightbulb className="h-6 w-6 text-amber-500" />
              طرق العلاج والمكافحة
            </h2>
            <div className="flex items-center gap-6">
              <ul className="flex-1 space-y-3">
                {resultData.disease_info.treatments.length > 0 ? (
                  resultData.disease_info.treatments.map((t) => (
                    <li key={t} className="flex items-center gap-3 text-gray-800">
                      <CheckCircle2 className="h-6 w-6 shrink-0 fill-primary text-white" />
                      {t}
                    </li>
                  ))
                ) : (
                  <li className="text-gray-500">لا يوجد علاج مطلوب، النبات سليم.</li>
                )}
              </ul>
              <ShieldCheck className="hidden h-32 w-32 shrink-0 text-primary-light/60 sm:block" strokeWidth={1.2} />
            </div>
          </Card>

          <div className="space-y-4 lg:col-span-2">
            <Card className="p-6">
              <h2 className="mb-4 flex items-center gap-2 text-xl font-bold text-gray-900">
                <Info className="h-6 w-6 text-primary" />
                إرشادات الوقاية
              </h2>
              <ul className="space-y-2">
                 {resultData.disease_info.prevention.map((p) => (
                    <li key={p} className="text-sm text-gray-700 flex items-start gap-2">
                      <span className="mt-1 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
                      {p}
                    </li>
                 ))}
              </ul>
            </Card>

            <div className="flex items-center justify-between gap-3 rounded-2xl bg-primary-light/20 px-5 py-4 text-sm text-gray-800">
              <p>
                <b>نوع النبات المكتشف:</b> {resultData.disease_info.plant}
              </p>
              <Sprout className="h-8 w-8 shrink-0 text-primary" />
            </div>
          </div>
        </section>
      )}
    </main>
  )
}