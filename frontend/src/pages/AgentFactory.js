import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Kpi, CardShell, StatusDot } from "../components/Kpi";

export default function AgentFactory() {
  const [agents, setAgents] = useState([]);
  const [caps, setCaps] = useState([]);
  const [selected, setSelected] = useState(null);
  useEffect(() => {
    api.get("/agents").then((r) => { setAgents(r.data); setSelected(r.data[0]); });
    api.get("/capabilities").then((r) => setCaps(r.data));
  }, []);
  return (
    <div data-testid="agents-page" className="space-y-6">
      <div>
        <div className="label-cap">Agent Factory</div>
        <h1 className="text-3xl font-semibold text-white mt-1">Fabrique d'agents spécialisés</h1>
        <p className="text-sm text-white/50 mt-2 max-w-2xl">
          Chaque agent : mission, permissions, tools, actions autorisées et interdites, escalation, audit. Réutiliser avant de créer.
        </p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Kpi label="Agents totaux" value={agents.length} testId="agents-total" />
        <Kpi label="En santé" value={agents.filter((a)=>a.health==="green").length} tone="green" testId="agents-green" />
        <Kpi label="Capabilities" value={caps.length} tone="violet" testId="agents-caps" />
        <Kpi label="Latence P95 moy." value={`${Math.round(agents.reduce((s,a)=>s+(a.latency_p95_ms||0),0)/(agents.length||1))}ms`} testId="agents-latency" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <CardShell title="Agents" testId="agents-list">
          <div className="max-h-[520px] overflow-auto scroll-thin">
            {agents.map((a) => (
              <button
                key={a.id}
                onClick={() => setSelected(a)}
                data-testid={`agent-${a.code}`}
                className={`w-full text-left py-2 px-2 border-b border-[#1A1C25] hover:bg-white/5 ${selected?.id === a.id ? "bg-violet-500/10" : ""}`}
              >
                <div className="flex items-center gap-2">
                  <StatusDot health={a.health} />
                  <div className="text-sm text-white flex-1">{a.name}</div>
                  <div className="font-mono text-[10px] text-violet-300">v{a.version}</div>
                </div>
                <div className="label-cap">{a.authority_scope} · P95 {a.latency_p95_ms}ms</div>
              </button>
            ))}
          </div>
        </CardShell>

        <div className="lg:col-span-2 space-y-4">
          {selected && (
            <>
              <CardShell title={`Détail · ${selected.name}`} testId="agent-detail">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div><div className="label-cap">Mission</div><div className="text-sm text-white mt-1">{selected.mission}</div></div>
                  <div><div className="label-cap">Scope</div><div className="text-sm text-violet-300 mt-1">{selected.authority_scope}</div></div>
                  <div><div className="label-cap">Health</div><div className="text-sm text-emerald-400 mt-1">{selected.health}</div></div>
                  <div><div className="label-cap">Précision</div><div className="text-sm text-white mt-1 font-mono">{Math.round(selected.precision*100)}%</div></div>
                </div>
                <div className="mt-4 grid grid-cols-2 gap-3">
                  <div>
                    <div className="label-cap mb-2">Actions autorisées</div>
                    <div className="space-y-1">
                      {selected.allowed_actions?.map((a)=>(
                        <div key={a} className="text-xs text-emerald-400 font-mono">+ {a}</div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <div className="label-cap mb-2">Actions interdites</div>
                    <div className="space-y-1">
                      {selected.prohibited_actions?.map((a)=>(
                        <div key={a} className="text-xs text-red-400 font-mono">✕ {a}</div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardShell>
              <CardShell title="Capabilities disponibles" testId="agent-caps">
                {caps.slice(0, 8).map((c) => (
                  <div key={c.id} className="flex items-center justify-between py-2 border-b border-[#1A1C25]">
                    <div className="flex items-center gap-2">
                      <StatusDot health={c.health} />
                      <div>
                        <div className="text-sm text-white">{c.name}</div>
                        <div className="label-cap">{c.agent_code} · v{c.version}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-mono text-xs text-white">{c.latency_p95_ms}ms</div>
                      <div className="label-cap">€{c.cost_eur}/call</div>
                    </div>
                  </div>
                ))}
              </CardShell>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
