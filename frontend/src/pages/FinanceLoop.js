import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { CardShell, Kpi } from "../components/Kpi";

const STAGE_COLOR = {
  OK: "text-emerald-400 border-emerald-500/40 bg-emerald-500/10",
  DATA_NOT_AVAILABLE: "text-white/40 border-[#252633] bg-transparent",
};

function fmt(v) {
  if (v == null) return "—";
  if (typeof v === "number" && v > 10000) return `€${(v / 1000).toFixed(0)}k`;
  if (typeof v === "number" && v > 0 && v < 100) return `${v}%`;
  return String(v);
}

export default function FinanceLoop() {
  const [d, setD] = useState(null);
  useEffect(() => { api.get("/finance/loop").then((r) => setD(r.data)); }, []);
  if (!d) return <div className="label-cap">Chargement…</div>;
  const missing = d.stages.filter((s) => s.status === "DATA_NOT_AVAILABLE").length;
  return (
    <div data-testid="finance-loop-page" className="space-y-6">
      <div>
        <div className="label-cap">Finance OS · Loop</div>
        <h1 className="text-3xl font-semibold text-white mt-1 tracking-tight">
          Boucle financière · <span className="text-amber-400">flux, pas snapshot</span>
        </h1>
        <p className="text-sm text-white/50 mt-2">
          Bottleneck actuel : <span className="text-amber-400 font-mono">{d.bottleneck || "—"}</span> · loop_health : {d.loop_health}
        </p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Kpi label="Stages" value={d.stages.length} testId="fl-total" />
        <Kpi label="OK" value={d.stages.filter((s)=>s.status==="OK").length} tone="green" testId="fl-ok" />
        <Kpi label="DATA NOT AVAILABLE" value={missing} tone="red" testId="fl-missing" />
        <Kpi label="Loop" value={d.loop_health} tone="gold" testId="fl-health" />
      </div>
      <CardShell title="Pipeline vivant" testId="fl-pipeline">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {d.stages.map((s, i) => (
            <div key={s.stage} data-testid={`stage-${s.stage}`} className={`border rounded-sm p-4 ${STAGE_COLOR[s.status]}`}>
              <div className="flex items-center justify-between">
                <div className="label-cap">{i + 1}. {s.stage}</div>
                <div className="label-cap">{s.status === "OK" ? "OK" : "N/A"}</div>
              </div>
              <div className="kpi-value text-xl mt-2">{s.status === "OK" ? fmt(s.value) : "DATA NOT AVAILABLE"}</div>
              <div className="text-xs text-white/50 mt-1">source · <span className="font-mono">{s.source}</span></div>
              {s.confidence != null && (
                <div className="label-cap mt-2">confidence {Math.round((s.confidence || 0) * 100)}%</div>
              )}
            </div>
          ))}
        </div>
      </CardShell>
    </div>
  );
}
