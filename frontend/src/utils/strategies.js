// تحويل نتيجة التحليل من الباك (scenarios A/B/C) لشكل كروت صفحة الدورات الزراعية.
const GENERIC_RISK = 'التوصية تحتاج مراجعة مهندس زراعي'

export function buildStrategies(analysis, icons, themes) {
  const scenarios = analysis?.scenarios
  if (!Array.isArray(scenarios) || scenarios.length === 0) return null

  return scenarios.map((sc) => {
    const m = sc.metrics || {}
    const crops = (sc.crops || []).map((c) => c.name_ar).join(' ← ')
    const water = m.water_change_vs_current_pct
    const waterTxt = `حوالي ${m.water_mm_total_estimate} مم للدورة` +
      (sc.scenario_id !== 'A' && water ? ` (${water > 0 ? '+' : ''}${water}٪ عن الحالية)` : '')
    // المخاطر المفيدة أولًا (من غير جملة "راجع مهندس" العامة)، وبحد أقصى اتنين
    const risks = (sc.risks || []).filter((r) => !r.startsWith(GENERIC_RISK))
    const soilLine = (sc.evidence || []).find((e) => e.startsWith('تقدير التربة')) || (sc.evidence || [])[0]
    const key = sc.scenario_id

    return {
      key,
      title: key === 'A' ? 'الدورة الزراعية الحالية' : `بديل: ${sc.focus || 'دورة مقترحة'}`,
      desc: crops,
      image: `/images/strategy-${key.toLowerCase()}.jpg`,
      theme: themes[key] || themes.A,
      stats: [
        { icon: icons.crop, label: 'المحاصيل المقترحة', value: crops, color: 'text-primary-light' },
        { icon: icons.water, label: 'احتياجات المياه', value: waterTxt, color: 'text-sky-500' },
        { icon: icons.soil, label: 'مؤشر التربة', value: `${m.soil_index} من 100 (نسبي)`, color: 'text-amber-900' },
        { icon: icons.sun, label: 'الملاءمة المناخية', value: `${m.climate_index} من 100 (نسبي)`, color: 'text-amber-500' },
      ],
      pro: (sc.benefits || [])[0] || '',
      risk: risks.slice(0, 2).join(' ') || (sc.risks || [])[0] || '',
      reason: soilLine || '',
    }
  })
}
