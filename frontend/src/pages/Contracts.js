import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { CardShell, Kpi } from "../components/Kpi";

export default function Contracts() {
  const [data, setData] = useState(null);
  const [active, setActive] = useState(null);
  useEffect(() => {
    api.get("/contracts").then((r) => {
      setData(r.data);
      setActive(r.data.contracts[0]);
    });
  }, []);
  if (!data) return <div className="label-cap">Chargement…</div>;
  return (
    <div data-testid="contracts-page" className="space-y-6">
      <div>
        <div className="label-cap">Cross-repo Contracts</div>
        <h1 className="text-3xl font-semibold text-white mt-1 tracking-tight">
          5 contrats · <span className="text-violet-400">versionnés</span>
        </h1>
        <p className="text-sm text-white/50 mt-2 max-w-3xl">
          Toute communication cross-entités passe par ces 5 contrats. Version stable, schéma
          JSON-Schema publié, exemples disponibles.
        </p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {data.contracts.map((c) => (
          <button
            key={c.key}
            data-testid={`contract-${c.key}`}
            onClick={() => setActive(c)}
            className={`border rounded-sm p-4 text-left hover:border-violet-500/60 transition-colors ${
              active?.key === c.key ? "border-violet-500 bg-violet-500/10" : "border-[#252633]"
            }`}
          >
            <div className="label-cap text-amber-400">v{c.version}</div>
            <div className="text-white font-semibold mt-1">{c.name}</div>
            <div className="label-cap mt-1">{c.key}</div>
          </button>
        ))}
      </div>
      {active && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <CardShell title={`${active.name} · JSON Schema`} testId="contract-schema">
            <pre className="text-[10px] font-mono text-white/70 leading-relaxed max-h-[560px] overflow-auto scroll-thin whitespace-pre-wrap">
              {JSON.stringify(active.schema, null, 2)}
            </pre>
          </CardShell>
          <CardShell title="Exemple minimal" testId="contract-example">
            <pre className="text-xs font-mono text-emerald-400 leading-relaxed max-h-[560px] overflow-auto scroll-thin whitespace-pre-wrap">
              {JSON.stringify(active.example, null, 2)}
            </pre>
          </CardShell>
        </div>
      )}
    </div>
  );
}
