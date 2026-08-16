import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { CardShell, Kpi } from "../components/Kpi";

const MODE_COLOR = {
  normal: "text-emerald-400 border-emerald-500/40 bg-emerald-500/10",
  degraded: "text-amber-400 border-amber-500/40 bg-amber-500/10",
  critical: "text-red-400 border-red-500/40 bg-red-500/10",
};

export default function AdaptiveRuntime() {
  const [state, setState] = useState(null);
  const [busy, setBusy] = useState(false);

  async function load() {
    const { data } = await api.get("/runtime/state");
    setState(data);
  }
  useEffect(() => { load(); const t = setInterval(load, 15000); return () => clearInterval(t); }, []);

  async function override(mode) {
    setBusy(true);
    try {
      await api.post("/runtime/state/override", { mode, reason: "manual UI override" });
      toast.success(`Runtime forced to ${mode}`);
      await load();
    } catch (e) {
      toast.error("Failed: " + (e.response?.data?.detail || e.message));
    } finally { setBusy(false); }
  }

  if (!state) return <div className="label-cap">Chargement…</div>;
  const s = state.signals || {};

  return (
    <div data-testid="runtime-page" className="space-y-6">
      <div>
        <div className="label-cap">Adaptive Runtime</div>
        <h1 className="text-3xl font-semibold text-white mt-1 tracking-tight">
          Mode courant · <span className={`${MODE_COLOR[state.mode]?.split(" ")[0]}`}>{state.mode.toUpperCase()}</span>
        </h1>
        <p className="text-sm text-white/50 mt-2">
          Calculé le {new Date(state.computed_at).toLocaleString("fr-FR")} · fenêtre {s.window}
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Kpi label="Pings (1h)" value={s.total_pings || 0} testId="rt-pings" />
        <Kpi label="Up" value={s.up_pings || 0} tone="green" testId="rt-up" />
        <Kpi label="Error rate" value={`${Math.round((s.error_rate || 0) * 100)}%`} tone={s.error_rate > 0.1 ? "red" : "green"} testId="rt-err" />
        <Kpi label="P95 latency" value={`${s.p95_ms || 0}ms`} tone={s.p95_ms > 2500 ? "gold" : "green"} testId="rt-p95" />
        <Kpi label="Incidents" value={s.active_incidents || 0} tone={s.active_incidents > 0 ? "red" : "green"} testId="rt-inc" />
      </div>

      <CardShell title="Policy" testId="rt-policy">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="border border-amber-500/30 rounded-sm p-3">
            <div className="label-cap text-amber-400">DEGRADED</div>
            <div className="text-xs font-mono text-white/80 mt-1">{state.policy?.degraded_if}</div>
          </div>
          <div className="border border-red-500/30 rounded-sm p-3">
            <div className="label-cap text-red-400">CRITICAL</div>
            <div className="text-xs font-mono text-white/80 mt-1">{state.policy?.critical_if}</div>
          </div>
        </div>
      </CardShell>

      <CardShell title="Manual override (admin)" testId="rt-override">
        <div className="flex flex-wrap gap-2">
          {["normal", "degraded", "critical"].map((m) => (
            <button key={m} data-testid={`btn-mode-${m}`} onClick={() => override(m)} disabled={busy}
              className={`btn-ghost disabled:opacity-50 ${state.mode === m ? "!border-violet-500 !text-white" : ""}`}>
              Force {m}
            </button>
          ))}
        </div>
        <p className="label-cap mt-3 text-white/50">
          Toute bascule est journalisée dans Evidence · nécessite le rôle admin.
        </p>
      </CardShell>
    </div>
  );
}
