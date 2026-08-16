import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { Kpi, CardShell, SeverityBadge } from "../components/Kpi";

const KINDS = [
  { key: "error", label: "Erreur", tone: "border-red-500/40 text-red-400" },
  { key: "inefficiency", label: "Inefficacité", tone: "border-amber-500/40 text-amber-400" },
  { key: "anomaly", label: "Anomalie", tone: "border-violet-500/40 text-violet-300" },
  { key: "opportunity", label: "Opportunité", tone: "border-emerald-500/40 text-emerald-400" },
  { key: "improvement", label: "Amélioration", tone: "border-blue-500/40 text-blue-400" },
  { key: "need", label: "Besoin", tone: "border-white/30 text-white/70" },
];

const MODULES = ["command_center","workbench","people_os","finance_os","legal_os","ops_os","knowledge_os","registry","agent_factory","decisions","evidence","notarizations","brain","other"];

export default function Feedback() {
  const [items, setItems] = useState([]);
  const [kind, setKind] = useState("opportunity");
  const [module, setModule] = useState("command_center");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    const { data } = await api.get("/feedback");
    setItems(data);
  }
  useEffect(() => { load(); }, []);

  async function submit(e) {
    e.preventDefault();
    if (!subject.trim() || !message.trim()) return;
    setBusy(true);
    try {
      await api.post("/feedback", { kind, subject, message, module });
      toast.success("Feedback enregistré. Merci — la doctrine apprend.");
      setSubject(""); setMessage("");
      await load();
    } catch (e) {
      toast.error("Échec: " + (e.response?.data?.detail || e.message));
    } finally { setBusy(false); }
  }

  const byKind = KINDS.map((k) => ({ ...k, count: items.filter((i)=>i.kind===k.key).length }));

  return (
    <div data-testid="feedback-page" className="space-y-6">
      <div>
        <div className="label-cap">Feedback System</div>
        <h1 className="text-3xl font-semibold text-white mt-1 tracking-tight">
          Signalez la friction · <span className="text-emerald-400">l'OS apprend</span>
        </h1>
        <p className="text-sm text-white/50 mt-2 max-w-3xl">
          RESULT → COMPARE → DETECT DEVIATION → ANALYZE → LEARN → UPDATE PROCESS → UPDATE DOCTRINE.
          Chaque signalement devient une donnée exploitable pour l'évolution du système.
        </p>
      </div>

      <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
        {byKind.map((k) => (
          <div key={k.key} className={`border rounded-sm p-3 ${k.tone}`}>
            <div className="kpi-value text-2xl">{k.count}</div>
            <div className="label-cap mt-1">{k.label}</div>
          </div>
        ))}
      </div>

      <CardShell title="Nouveau signalement" testId="fb-new">
        <form onSubmit={submit} className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div>
            <div className="label-cap mb-1">Type</div>
            <select data-testid="fb-kind" value={kind} onChange={(e)=>setKind(e.target.value)}
              className="w-full bg-[#0F1017] border border-[#252633] rounded-sm px-3 py-2 text-sm text-white font-mono text-xs">
              {KINDS.map((k)=><option key={k.key} value={k.key}>{k.label}</option>)}
            </select>
          </div>
          <div>
            <div className="label-cap mb-1">Module</div>
            <select data-testid="fb-module" value={module} onChange={(e)=>setModule(e.target.value)}
              className="w-full bg-[#0F1017] border border-[#252633] rounded-sm px-3 py-2 text-sm text-white font-mono text-xs">
              {MODULES.map((m)=><option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          <div className="md:col-span-2">
            <div className="label-cap mb-1">Sujet</div>
            <input data-testid="fb-subject" value={subject} onChange={(e)=>setSubject(e.target.value)}
              placeholder="Ex: Latence trop élevée sur Legal Agent"
              className="w-full bg-[#0F1017] border border-[#252633] rounded-sm px-3 py-2 text-sm text-white outline-none focus:border-violet-500" />
          </div>
          <div className="md:col-span-4">
            <div className="label-cap mb-1">Message</div>
            <textarea data-testid="fb-message" value={message} onChange={(e)=>setMessage(e.target.value)} rows={3}
              placeholder="Décrivez ce qui ne fonctionne pas ou pourrait mieux fonctionner…"
              className="w-full bg-[#0F1017] border border-[#252633] rounded-sm px-3 py-2 text-sm text-white outline-none focus:border-violet-500" />
          </div>
          <div className="md:col-span-4">
            <button data-testid="fb-submit" type="submit" disabled={busy} className="btn-primary disabled:opacity-50">
              {busy ? "…" : "Signaler"}
            </button>
          </div>
        </form>
      </CardShell>

      <CardShell title="Historique · dernier haut" testId="fb-list">
        <div className="max-h-[520px] overflow-auto scroll-thin">
          {items.length === 0 && (
            <div className="text-center py-10 label-cap">Aucun feedback pour l'instant.</div>
          )}
          {items.map((i) => {
            const k = KINDS.find((x)=>x.key===i.kind) || {};
            return (
              <div key={i.id} className="py-3 border-b border-[#1A1C25] last:border-0">
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-mono uppercase tracking-widest px-1.5 py-0.5 rounded-sm border ${k.tone || "border-[#252633] text-white/60"}`}>{k.label || i.kind}</span>
                  <div className="text-sm text-white flex-1">{i.subject}</div>
                  <div className="label-cap">{i.module || "—"}</div>
                </div>
                <div className="text-xs text-white/60 mt-1">{i.message}</div>
                <div className="label-cap mt-1 text-white/40">
                  {i.author?.email} · {new Date(i.created_at).toLocaleString("fr-FR")}
                </div>
              </div>
            );
          })}
        </div>
      </CardShell>
    </div>
  );
}
