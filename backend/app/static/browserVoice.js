// حوار صوتي بالدور باستخدام صوت المتصفح (Web Speech API) — من غير مفاتيح API.
// الاستماع (SpeechRecognition) شغال كويس في Chrome (كمبيوتر وأندرويد). iPhone/Safari ضعيف → استخدموا الأزرار.
// لو الباك شغال بوضع api وردّ بـ audio_base64، الوكيل بيشغّله بدل صوت المتصفح.

const SR = typeof window !== "undefined" ? window.SpeechRecognition || window.webkitSpeechRecognition : null;
const NO_HEAR = "ما سمعتكش كويس، ممكن تعيد تاني؟";

export class BrowserVoiceAgent {
  constructor({ apiUrl = "", lang = "ar-EG", onState = () => {}, onMessage = () => {}, onProfile = () => {}, onResult = () => {}, onError = () => {} } = {}) {
    Object.assign(this, { apiUrl, lang, onState, onMessage, onProfile, onResult, onError });
    this.sessionId = null;
    this.state = "idle"; // idle | speaking | listening | thinking | done
    this.rec = null;
    this.audioEl = null;
    this.retries = 0;
    this._gen = 0;
  }

  get canListen() { return !!SR; }
  get canSpeak() { return typeof speechSynthesis !== "undefined"; }
  _voice() {
    if (!this.canSpeak) return null;
    const vs = speechSynthesis.getVoices();
    // نفضّل المصري، وبعدين أصوات Google/Microsoft الأونلاين (أوضح)
    const score = (v) => (v.lang === "ar-EG" ? 2 : 0) + (/natural|online|google|neural/i.test(v.name) ? 1 : 0);
    const ar = vs.filter((v) => v.lang.toLowerCase().startsWith("ar")).sort((a, b) => score(b) - score(a));
    return ar[0] || null;
  }
  get hasArabicVoice() { return !!this._voice(); }

  _set(s) { this.state = s; this.onState(s); }
  _fail(e) {
    this._set("idle");
    const m = e && e.message ? e.message : "";
    this.onError(/fetch|network/i.test(m) ? "السيرفر مش بيرد. تأكد إنه شغال." : m || "حصلت مشكلة.");
  }

  async _post(path, body) {
    const r = await fetch(this.apiUrl + path, {
      method: "POST",
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!r.ok) {
      let d = "";
      try { d = (await r.json()).detail; } catch { /* ignore */ }
      throw new Error(typeof d === "string" && d ? d : "HTTP " + r.status);
    }
    return r.json();
  }

  // ---- نطق ----
  speak(text) {
    return new Promise((resolve) => {
      this._stopAudio();
      if (!this.canSpeak) return resolve();
      speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.lang = this.lang;
      u.rate = 0.9;
      const v = this._voice();
      if (v) u.voice = v;
      let done = false;
      const fin = () => { if (!done) { done = true; clearTimeout(t); resolve(); } };
      const t = setTimeout(fin, 4000 + text.length * 130); // حماية من توقف النطق في بعض المتصفحات
      u.onend = fin;
      u.onerror = fin;
      speechSynthesis.speak(u);
    });
  }
  _play(b64, mime) {
    return new Promise((res) => {
      const a = new Audio(`data:${mime || "audio/mpeg"};base64,${b64}`);
      this.audioEl = a;
      a.onended = a.onerror = () => res();
      a.play().catch(() => res());
    });
  }
  _stopAudio() { if (this.audioEl) { this.audioEl.pause(); this.audioEl = null; } }
  async _say(r) { return r.audio_base64 ? this._play(r.audio_base64, r.audio_mime) : this.speak(r.reply_text); }

  // ---- التحكم ----
  stop() {
    this._gen++;
    if (this.rec) { try { this.rec.abort(); } catch { /* ignore */ } this.rec = null; }
    if (this.canSpeak) speechSynthesis.cancel();
    this._stopAudio();
    this._set("idle");
  }

  /** لازم تتنده من ضغطة زرار (المتصفح بيمنع الصوت التلقائي). */
  async start() {
    this.stop();
    const gen = this._gen;
    this.retries = 0;
    this._set("thinking");
    try {
      const r = await this._post("/api/voice/start");
      this.sessionId = r.session_id;
      await this._handle(r, gen);
    } catch (e) { this._fail(e); }
  }

  listen() {
    if (!SR) { this._set("idle"); this.onError("المتصفح ده مبيدعمش التعرف على الصوت. استخدم Chrome، أو اختار بالضغط."); return; }
    if (this.canSpeak) speechSynthesis.cancel();
    const gen = this._gen;
    const rec = new SR();
    this.rec = rec;
    rec.lang = this.lang;
    rec.interimResults = false;
    rec.continuous = false;
    rec.maxAlternatives = 1;
    let got = false;
    rec.onresult = (e) => { got = true; this.sendText(e.results[0][0].transcript, gen); };
    rec.onerror = (e) => {
      if (e.error === "no-speech") return;
      got = true;
      if (e.error === "aborted") return;
      this._set("idle");
      this.onError(e.error === "not-allowed" || e.error === "service-not-allowed"
        ? "لازم تسمح للمتصفح باستخدام الميكروفون."
        : e.error === "network" ? "التعرف على الصوت محتاج إنترنت." : "مقدرتش أسمعك. جرب تاني أو اختار بالضغط.");
    };
    rec.onend = () => { if (!got && gen === this._gen && this.state === "listening") this._noHear(gen); };
    this._set("listening");
    try { rec.start(); } catch { /* already started */ }
  }

  async _noHear(gen) {
    this.retries++;
    if (this.retries > 2) { this.retries = 0; this._set("idle"); return; }
    this.onMessage({ role: "assistant", text: NO_HEAR });
    this._set("speaking");
    await this.speak(NO_HEAR);
    if (gen === this._gen) this.listen();
  }

  /** نص من الميكروفون أو من الأزرار/الكتابة. */
  async sendText(text, gen) {
    if (gen === undefined) { this.stop(); gen = this._gen; }
    text = (text || "").trim();
    if (!text) return;
    this.retries = 0;
    this.onMessage({ role: "user", text });
    this._set("thinking");
    try {
      const r = await this._post("/api/voice/text-turn", { session_id: this.sessionId || "new", text });
      this.sessionId = r.session_id;
      if (gen !== this._gen) return;
      await this._handle(r, gen);
    } catch (e) { this._fail(e); }
  }

  async _handle(r, gen) {
    if (r.engine) console.log(`[zarah] engine=${r.engine}${r.llm_error ? " LLM error: " + r.llm_error : ""} intent=${r.intent || "-"} action=${r.action || "-"}`);
    this.onMessage({ role: "assistant", text: r.reply_text });
    this.onProfile(r.profile, r.missing);
    this._set("speaking");
    await this._say(r);
    if (gen !== this._gen) return;
    if (r.done) await this.finish(gen);
    else this.listen();
  }

  async finish(gen = this._gen) {
    this._set("thinking");
    try {
      const out = await this._post(`/api/voice/session/${this.sessionId}/analyze?speak=true`);
      this.onResult(out);
      if (gen !== this._gen) return;
      this._set("speaking");
      const sp = out.speech || {};
      if (sp.audio_base64) await this._play(sp.audio_base64, sp.audio_mime);
      else await this.speak(out.analysis.spoken_summary_ar);
      if (gen === this._gen) this._set("done");
    } catch (e) { this._fail(e); }
  }
}
