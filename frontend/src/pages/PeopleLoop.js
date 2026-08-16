import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { CardShell, Kpi } from "../components/Kpi";

const STAGE_COLOR = {
  OK: "text-emerald-400 border-emerald-500/40 bg-emerald-500/10",
  DATA_NOT_AVAILABLE: "text-white/40 border-[#252633] bg-transparent",
};

export default function PeopleLoop() {
  const [d, setD] = useState(null);
  useEffect(() => { api.get("/people/loop").then((r) => setD(r.data)); }, []);
  if (!d) return <div className="label-cap">Chargement…</div>;
  return (
    <div data-testid="people-loop-page" className="space-y-6">
      <div>
        <div className="label-cap">People OS · Loop</div>
        <h1 className="text-3xl font-semibold text-white mt-1 tracking-tight">
          Boucle humaine · <span className="text-violet-400">Academy → Succession → Academy</span>
        </h1>
        <p className="text-sm text-white/50 mt-2">
          Bottleneck : <span className="text-amber-400 font-mono">{d.bottleneck || "—"}</span> · loop_health : {d.loop_health}
        </p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Kpi label="Stages" value={d.stages.length} testId="hl-total" />
        <Kpi label="OK" value={d.stages.filter((s)=>s.status==="OK").length} tone="green" testId="hl-ok" />
        <Kpi label="DATA N/A" value={d.stages.filter((s)=>s.status!=="OK").length} tone="red" testId="hl-missing" />
        <Kpi label="Loop" value={d.loop_health} tone="gold" testId="hl-health" />
      </div>
      <CardShell title="Pipeline humain" testId="hl-pipeline">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {d.stages.map((s, i) => (
            <div key={s.stage} data-testid={`stage-${s.stage}`} className={`border rounded-sm p-4 ${STAGE_COLOR[s.status]}`}>
              <div className="flex items-center justify-between">
                <div className="label-cap">{i + 1}. {s.stage}</div>
              </div>
              <div className="kpi-value text-xl mt-2">{s.status === "OK" ? (s.count ?? "0") : "DATA NOT AVAILABLE"}</div>
              <div className="text-xs text-white/50 mt-1 font-mono">{s.source}</div>
            </div>
          ))}
        </div>
      </CardShell>
    </div>
  );
}
