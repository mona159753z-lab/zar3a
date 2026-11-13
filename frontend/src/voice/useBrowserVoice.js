import { useEffect, useRef, useState } from "react";
import { BrowserVoiceAgent } from "./browserVoice";

// استخدام: const v = useBrowserVoice(); <button onClick={v.onMicClick}>{v.state}</button>
export function useBrowserVoice(apiUrl = import.meta.env.VITE_API_URL || "") {
  const [state, setState] = useState("idle");
  const [bot, setBot] = useState("");
  const [me, setMe] = useState("");
  const [profile, setProfile] = useState({});
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const agent = useRef(null);

  if (!agent.current) {
    agent.current = new BrowserVoiceAgent({
      apiUrl,
      onState: setState,
      onMessage: (m) => (m.role === "assistant" ? setBot(m.text) : setMe(m.text)),
      onProfile: setProfile,
      onResult: (out) => setResult(out.analysis),
      onError: setError,
    });
  }
  useEffect(() => () => agent.current.stop(), []);

  const a = agent.current;
  const onMicClick = () => {
    if (!a.sessionId || a.state === "done") return a.start();   // أول ضغطة لازم تبدأ من هنا
    if (a.state === "listening") return a.stop();
    if (a.state === "thinking") return;
    a.stop(); a.listen();
  };
  return { state, bot, me, profile, result, error, onMicClick, sendText: (t) => a.sendText(t),
           canListen: a.canListen, hasArabicVoice: a.hasArabicVoice };
}
