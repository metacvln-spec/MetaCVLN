import { useEffect, useRef, useState } from "react";
import { api } from "../lib/api";
import { toast } from "sonner";

export default function CVLBrain() {
  const [messages, setMessages] = useState([]);
  const [q, setQ] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef(null);

  async function load() {
    const { data } = await api.get("/brain/history");
    setMessages(data);
  }
  useEffect(() => { load(); }, []);
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function send(e) {
    e?.preventDefault();
    if (!q.trim()) return;
    setBusy(true);
    const question = q;
    setQ("");
    setMessages((m) => [...m, { id: `t-${Date.now()}`, question, answer: null, pending: true, created_at: new Date().toISOString() }]);
    try {
      const { data } = await api.post("/brain/ask", { question });
      await load();
    } catch (err) {
      toast.error(`CVL Brain: ${err.response?.data?.detail || err.message}`);
      setMessages((m) => m.filter((x) => !x.pending));
    } finally {
      setBusy(false);
    }
  }

  const suggestions = [
    "Prépare un briefing exécutif du groupe pour ce lundi.",
    "Quelles décisions financières nécessitent mon attention cette semaine ?",
    "Analyse les risques contractuels imminents sur les 60 prochains jours.",
    "Résume les initiatives Laurentia en cours et leur impact attendu.",
  ];

  return (
    <div data-testid="brain-page" className="h-full flex flex-col space-y-4">
      <div>
        <div className="label-cap">CVL Brain</div>
        <h1 className="text-3xl font-semibold text-white mt-1">
          Couche cognitive · <span className="text-violet-400">Claude Sonnet 4.6</span>
        </h1>
        <p className="text-sm text-white/50 mt-2 max-w-3xl">
          CVL Brain produit CONTEXTE → ANALYSE → INSIGHT → RECOMMANDATION avec source, confiance et traçabilité. Il ne décide pas.
        </p>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-auto scroll-thin surface-card p-5">
        {messages.length === 0 && (
          <div className="text-center py-16">
            <div className="label-cap text-white/50">Commencez la conversation</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-6 max-w-2xl mx-auto">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => setQ(s)}
                  data-testid={`brain-suggest-${s.slice(0,12)}`}
                  className="text-left text-sm text-white/70 hover:text-white border border-[#252633] hover:border-violet-500/60 p-3 rounded-sm transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m) => (
          <div key={m.id} className="mb-6 pb-6 border-b border-[#1A1C25] last:border-0">
            <div className="label-cap mb-2 text-violet-300">Vous</div>
            <div className="text-sm text-white/90 mb-4">{m.question}</div>
            <div className="label-cap mb-2 text-amber-400">CVL Brain</div>
            {m.pending ? (
              <div className="text-sm text-white/50 animate-pulse">Analyse en cours…</div>
            ) : (
              <>
                <div className="text-sm text-white/85 whitespace-pre-wrap">{m.answer}</div>
                {m.provenance && (
                  <div className="mt-3 flex flex-wrap gap-2 label-cap">
                    <span className="border border-[#252633] px-2 py-1 rounded-sm">SOURCE {m.provenance.source}</span>
                    <span className="border border-[#252633] px-2 py-1 rounded-sm">MODEL {m.provenance.model}</span>
                    <span className="border border-[#252633] px-2 py-1 rounded-sm">CONFIDENCE {Math.round((m.provenance.confidence || 0) * 100)}%</span>
                    <span className="border border-[#252633] px-2 py-1 rounded-sm">DATE {new Date(m.provenance.date).toLocaleString("fr-FR")}</span>
                  </div>
                )}
              </>
            )}
          </div>
        ))}
      </div>

      <form onSubmit={send} className="flex gap-2">
        <input
          data-testid="brain-input"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Posez votre question à CVL Brain…"
          className="flex-1 bg-[#13141C] border border-[#252633] rounded-sm px-3 py-2.5 text-sm text-white outline-none focus:border-violet-500"
        />
        <button data-testid="brain-send" type="submit" disabled={busy || !q.trim()} className="btn-primary disabled:opacity-50">
          {busy ? "…" : "Interroger"}
        </button>
      </form>
    </div>
  );
}
