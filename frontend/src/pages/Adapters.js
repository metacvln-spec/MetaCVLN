import { useState } from "react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { CardShell } from "../components/Kpi";

const ADAPTERS = [
  {
    id: "labelos_push",
    capability: "labelos.push_catalogue",
    entity: "labelos:fms",
    endpoint: "/adapters/labelos/push_catalogue",
    roles: ["admin", "cfo", "ops_lead"],
    approval: "cfo",
    example: { items: [{ isrc: "FR-XXX-25-00001", title: "Demo track", artist: "Anba T." }] },
  },
  {
    id: "wallet_tx",
    capability: "wallet.transaction",
    entity: "cvln_wallet",
    endpoint: "/adapters/wallet/transaction",
    roles: ["admin", "cfo"],
    approval: "cfo",
    example: { from: "labelos:fms", to: "artist:XXX", amount_eur: 1250, ref: "royalty Q1" },
  },
  {
    id: "laurentia_brief",
    capability: "laurentia.briefing",
    entity: "laurentia",
    endpoint: "/adapters/laurentia/briefing",
    roles: ["*"],
    approval: null,
    example: { topic: "Q1 diaspora signals", horizon_days: 30 },
  },
];

export default function Adapters() {
  const [selected, setSelected] = useState(ADAPTERS[0]);
  const [inputs, setInputs] = useState(JSON.stringify(ADAPTERS[0].example, null, 2));
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);

  function select(a) {
    setSelected(a);
    setInputs(JSON.stringify(a.example, null, 2));
    setResult(null);
  }

  async function invoke() {
    setBusy(true);
    setResult(null);
    try {
      const parsed = JSON.parse(inputs);
      const { data } = await api.post(selected.endpoint, { inputs: parsed });
      setResult(data);
      toast[(data.http && data.http < 400) ? "success" : "error"](
        `${selected.capability} → HTTP ${data.http ?? "—"} · ${data.ms ?? "—"}ms`
      );
    } catch (e) {
      toast.error("Échec: " + (e.response?.data?.detail || e.message));
      setResult({ error: e.response?.data?.detail || e.message });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div data-testid="adapters-page" className="space-y-6">
      <div>
        <div className="label-cap">Typed Cross-Repo Adapters</div>
        <h1 className="text-3xl font-semibold text-white mt-1 tracking-tight">
          Appels typés · <span className="text-violet-400">contrat versionné</span>
        </h1>
        <p className="text-sm text-white/50 mt-2 max-w-3xl">
          Chaque adapter est un appel typé qui résout la cible dans Registry, injecte l'auth,
          journalise dans Evidence, notarise en amont. Trace ID propagé de bout en bout.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="space-y-3">
          {ADAPTERS.map((a) => (
            <button
              key={a.id}
              data-testid={`adapter-${a.id}`}
              onClick={() => select(a)}
              className={`w-full text-left border rounded-sm p-4 transition-colors ${
                selected.id === a.id ? "border-violet-500 bg-violet-500/10" : "border-[#252633] hover:border-violet-500/60"
              }`}
            >
              <div className="label-cap text-amber-400">{a.entity}</div>
              <div className="text-sm text-white font-mono mt-1">{a.capability}</div>
              <div className="label-cap mt-2">roles {a.roles.join(", ")}</div>
              {a.approval && <div className="label-cap text-amber-400">approval by {a.approval}</div>}
            </button>
          ))}
        </div>

        <div className="lg:col-span-2 space-y-4">
          <CardShell title={`inputs · ${selected.capability}`} testId="adapter-inputs">
            <textarea
              data-testid="adapter-inputs-json"
              value={inputs}
              onChange={(e) => setInputs(e.target.value)}
              rows={10}
              className="w-full bg-[#0F1017] border border-[#252633] rounded-sm px-3 py-2 text-xs font-mono text-emerald-300 outline-none focus:border-violet-500"
            />
            <button data-testid="adapter-invoke" onClick={invoke} disabled={busy} className="btn-primary mt-3 disabled:opacity-50">
              {busy ? "Appel en cours…" : `Invoke ${selected.capability}`}
            </button>
          </CardShell>

          {result && (
            <CardShell title="Résultat" testId="adapter-result">
              <div className="flex flex-wrap gap-2 mb-3">
                {result.trace_id && (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-sm border border-violet-500/40 bg-violet-500/10 text-violet-300">
                    trace_id {result.trace_id.slice(0, 8)}…
                  </span>
                )}
                {result.http && (
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded-sm border ${
                    result.http < 400 ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-400" : "border-red-500/40 bg-red-500/10 text-red-400"
                  }`}>HTTP {result.http}</span>
                )}
                {result.ms && <span className="text-[10px] font-mono px-2 py-0.5 rounded-sm border border-[#252633] text-white/70">{result.ms}ms</span>}
                {result.status && <span className="text-[10px] font-mono px-2 py-0.5 rounded-sm border border-amber-500/40 bg-amber-500/10 text-amber-400">{result.status}</span>}
              </div>
              <pre className="text-xs font-mono text-white/80 max-h-[300px] overflow-auto scroll-thin whitespace-pre-wrap">
                {JSON.stringify(result, null, 2)}
              </pre>
            </CardShell>
          )}
        </div>
      </div>
    </div>
  );
}
