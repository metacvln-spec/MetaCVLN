import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { CardShell, Kpi } from "../components/Kpi";

export default function LearningProposals() {
  const [items, setItems] = useState([]);
  const [subject, setSubject] = useState("");
  const [newDoc, setNewDoc] = useState("");
  const [oldDoc, setOldDoc] = useState("");
  const [impact, setImpact] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    const { data } = await api.get("/learning/proposals");
    setItems(data);
  }
  useEffect(() => { load(); }, []);

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    try {
      await api.post("/learning/proposals", {
        subject, new_doctrine: newDoc, old_doctrine: oldDoc || null,
        expected_impact: impact || null, supporting_feedback_ids: [], affected_systems: [],
      });
      toast.success("Proposition créée. En attente de validation humaine.");
      setSubject(""); setNewDoc(""); setOldDoc(""); setImpact("");
      await load();
    } catch (e) {
      toast.error("Failed: " + (e.response?.data?.detail || e.message));
    } finally { setBusy(false); }
  }

  async function approve(id) {
    try {
      await api.post(`/learning/proposals/${id}/approve`);
      toast.success("Doctrine mise à jour");
      await load();
    } catch (e) {
      toast.error("Failed: " + (e.response?.data?.detail || e.message));
    }
  }

  const pending = items.filter((x) => x.status === "pending").length;
  const approved = items.filter((x) => x.status === "approved").length;

  return (
    <div data-testid="learning-page" className="space-y-6">
      <div>
        <div className="label-cap">Learning Validation</div>
        <h1 className="text-3xl font-semibold text-white mt-1 tracking-tight">
          Feedback → Proposition → <span className="text-emerald-400">Doctrine</span>
        </h1>
        <p className="text-sm text-white/50 mt-2 max-w-3xl">
          Aucune modification automatique de production. Chaque proposition demande une validation
          humaine explicite avant d'entrer dans la doctrine.
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Kpi label="Total" value={items.length} testId="lp-total" />
        <Kpi label="Draft" value={items.filter((x)=>x.status==="draft").length} testId="lp-draft" />
        <Kpi label="Pending" value={pending} tone="gold" testId="lp-pending" />
        <Kpi label="Approved" value={approved} tone="green" testId="lp-approved" />
      </div>

      <CardShell title="Proposer une évolution de doctrine" testId="lp-new">
        <form onSubmit={submit} className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="md:col-span-2">
            <div className="label-cap mb-1">Sujet</div>
            <input data-testid="lp-subject" value={subject} onChange={(e)=>setSubject(e.target.value)} required
              className="w-full bg-[#0F1017] border border-[#252633] rounded-sm px-3 py-2 text-sm text-white outline-none focus:border-violet-500" />
          </div>
          <div>
            <div className="label-cap mb-1">Ancienne doctrine (optionnel)</div>
            <textarea data-testid="lp-old" rows={4} value={oldDoc} onChange={(e)=>setOldDoc(e.target.value)}
              className="w-full bg-[#0F1017] border border-[#252633] rounded-sm px-3 py-2 text-sm text-white/70 outline-none focus:border-violet-500" />
          </div>
          <div>
            <div className="label-cap mb-1">Nouvelle doctrine</div>
            <textarea data-testid="lp-new-doc" rows={4} value={newDoc} onChange={(e)=>setNewDoc(e.target.value)} required
              className="w-full bg-[#0F1017] border border-[#252633] rounded-sm px-3 py-2 text-sm text-white outline-none focus:border-violet-500" />
          </div>
          <div className="md:col-span-2">
            <div className="label-cap mb-1">Impact attendu</div>
            <input data-testid="lp-impact" value={impact} onChange={(e)=>setImpact(e.target.value)}
              className="w-full bg-[#0F1017] border border-[#252633] rounded-sm px-3 py-2 text-sm text-white outline-none focus:border-violet-500" />
          </div>
          <div className="md:col-span-2">
            <button type="submit" data-testid="lp-submit" disabled={busy} className="btn-primary disabled:opacity-50">
              {busy ? "…" : "Créer la proposition"}
            </button>
          </div>
        </form>
      </CardShell>

      <CardShell title="Historique" testId="lp-list">
        {items.length === 0 && <div className="label-cap text-center py-8">Aucune proposition.</div>}
        {items.map((p) => (
          <div key={p.id} className="py-3 border-b border-[#1A1C25] last:border-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`text-[10px] font-mono uppercase tracking-widest px-1.5 py-0.5 rounded-sm border ${
                p.status === "approved" ? "text-emerald-400 border-emerald-500/40 bg-emerald-500/10"
                  : p.status === "pending" ? "text-amber-400 border-amber-500/40 bg-amber-500/10"
                  : "text-white/50 border-[#252633]"
              }`}>{p.status}</span>
              <div className="text-sm text-white font-semibold flex-1">{p.subject}</div>
              {p.status !== "approved" && (
                <button data-testid={`approve-${p.id}`} onClick={() => approve(p.id)} className="btn-gold text-[10px]">
                  Approuver
                </button>
              )}
            </div>
            <div className="text-xs text-white/60 mt-1">{p.new_doctrine}</div>
            <div className="label-cap mt-1 text-white/40">
              supporting {p.supporting_count}/{p.threshold} · {p.author?.email} · {new Date(p.created_at).toLocaleString("fr-FR")}
            </div>
          </div>
        ))}
      </CardShell>
    </div>
  );
}
