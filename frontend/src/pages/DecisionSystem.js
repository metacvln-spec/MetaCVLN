import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { CardShell, SeverityBadge } from "../components/Kpi";

export default function DecisionSystem() {
  const [items, setItems] = useState([]);
  const [selected, setSelected] = useState(null);
  const [busy, setBusy] = useState(false);
  const [comment, setComment] = useState("");

  async function load() {
    const { data } = await api.get("/decisions");
    setItems(data);
    if (!selected && data.length) setSelected(data[0]);
  }
  useEffect(() => { load(); }, []);

  async function act(action) {
    if (!selected) return;
    setBusy(true);
    try {
      await api.post(`/decisions/${selected.id}/action`, { action, comment });
      toast.success(`Décision ${action}`);
      setComment("");
      await load();
      setSelected((s) => s ? { ...s, status: action } : s);
    } catch (e) {
      toast.error(`Échec: ${e.response?.data?.detail || e.message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div data-testid="decisions-page" className="space-y-6">
      <div>
        <div className="label-cap">Decision System</div>
        <h1 className="text-3xl font-semibold text-white mt-1">Décisions préparées · Décisions humaines</h1>
        <p className="text-sm text-white/50 mt-2 max-w-2xl">
          Question → Contexte → Données → Options → Risques → Recommandation → Approbation humaine → Exécution → Résultat.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <CardShell title="En attente" testId="decisions-list">
          <div className="max-h-[560px] overflow-auto scroll-thin">
            {items.map((d) => (
              <button
                key={d.id}
                data-testid={`decision-${d.id}`}
                onClick={() => setSelected(d)}
                className={`w-full text-left py-2 px-2 border-b border-[#1A1C25] hover:bg-white/5 ${selected?.id === d.id ? "bg-violet-500/10" : ""}`}
              >
                <div className="flex items-center gap-2">
                  <SeverityBadge severity={d.priority} />
                  <div className="text-sm text-white flex-1">{d.title}</div>
                </div>
                <div className="label-cap mt-1">{d.category} · {d.status}</div>
              </button>
            ))}
          </div>
        </CardShell>

        <div className="lg:col-span-2">
          {selected && (
            <CardShell title="Détail de la décision" testId="decision-detail">
              <div className="mb-4">
                <h3 className="text-xl font-semibold text-white">{selected.title}</h3>
                <div className="label-cap mt-1">Préparée par {selected.prepared_by} · confidence {Math.round((selected.confidence || 0) * 100)}%</div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <div className="label-cap mb-2">Contexte</div>
                  <p className="text-sm text-white/80">{selected.context}</p>
                </div>
                <div>
                  <div className="label-cap mb-2">Sources</div>
                  <ul className="text-sm space-y-1">
                    {selected.sources?.map((s) => (
                      <li key={s} className="text-white/70">· {s}</li>
                    ))}
                  </ul>
                </div>
              </div>
              <div className="mt-4">
                <div className="label-cap mb-2">Options</div>
                <div className="space-y-2">
                  {selected.options?.map((o, i) => (
                    <div key={i} className={`px-3 py-2 rounded-sm border ${o === selected.recommendation ? "border-amber-500/50 bg-amber-500/5" : "border-[#252633]"}`}>
                      <div className="flex justify-between text-sm">
                        <span className="text-white">{o}</span>
                        {o === selected.recommendation && <span className="label-cap text-amber-400">Recommandé</span>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="mt-4">
                <div className="label-cap mb-2">Risques identifiés</div>
                <div className="flex flex-wrap gap-2">
                  {selected.risks?.map((r) => (
                    <span key={r} className="text-xs border border-red-500/30 bg-red-500/5 text-red-300 px-2 py-1 rounded-sm">{r}</span>
                  ))}
                </div>
              </div>

              <div className="mt-6 border-t border-[#252633] pt-4">
                <div className="label-cap mb-2">Commentaire de décision</div>
                <textarea
                  data-testid="decision-comment"
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  rows={2}
                  className="w-full bg-[#0F1017] border border-[#252633] rounded-sm px-3 py-2 text-sm text-white outline-none focus:border-violet-500"
                  placeholder="Motivation, contexte additionnel…"
                />
                <div className="flex flex-wrap gap-2 mt-3">
                  <button disabled={busy} data-testid="btn-approve" onClick={() => act("approve")} className="btn-gold">Approuver</button>
                  <button disabled={busy} data-testid="btn-reject" onClick={() => act("reject")} className="btn-ghost hover:!border-red-500 hover:!text-red-400">Rejeter</button>
                  <button disabled={busy} data-testid="btn-edit" onClick={() => act("edit")} className="btn-ghost">Éditer</button>
                  <button disabled={busy} data-testid="btn-escalate" onClick={() => act("escalate")} className="btn-ghost">Escalader</button>
                  <button disabled={busy} data-testid="btn-pause" onClick={() => act("pause")} className="btn-ghost">Pause</button>
                  <button disabled={busy} data-testid="btn-rollback" onClick={() => act("rollback")} className="btn-ghost">Rollback</button>
                </div>
                <div className="label-cap mt-3 text-white/40">
                  Statut courant : <span className="text-white">{selected.status}</span> · Toute action est journalisée dans Evidence & Audit.
                </div>
              </div>
            </CardShell>
          )}
        </div>
      </div>
    </div>
  );
}
