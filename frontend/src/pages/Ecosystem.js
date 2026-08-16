import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { CardShell, StatusDot } from "../components/Kpi";

export default function Ecosystem() {
  const [entities, setEntities] = useState([]);
  useEffect(() => { api.get("/entities").then((r) => setEntities(r.data)); }, []);
  const byLayer = {};
  entities.forEach((e) => {
    byLayer[e.layer] = byLayer[e.layer] || [];
    byLayer[e.layer].push(e);
  });
  return (
    <div data-testid="ecosystem-page" className="space-y-6">
      <div>
        <div className="label-cap">Work Graph · Écosystème</div>
        <h1 className="text-3xl font-semibold text-white mt-1">
          Structure du groupe <span className="text-violet-400">META CVLN</span>
        </h1>
      </div>
      {Object.entries(byLayer).map(([layer, items]) => (
        <CardShell key={layer} title={layer} testId={`layer-${layer}`}>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {items.map((e) => (
              <div key={e.id} className="border border-[#252633] rounded-sm p-3 hover:border-violet-500/60 transition-colors">
                <div className="flex items-center gap-2 mb-1">
                  <StatusDot health={e.health} />
                  <div className="font-mono text-xs text-white">{e.name}</div>
                </div>
                <div className="text-xs text-white/50">{e.description}</div>
                <div className="label-cap mt-2">{e.kind}</div>
              </div>
            ))}
          </div>
        </CardShell>
      ))}
    </div>
  );
}
