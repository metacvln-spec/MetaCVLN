import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Kpi, CardShell, SeverityBadge, StatusDot } from "../components/Kpi";

export default function OpsOS() {
  const [d, setD] = useState(null);
  useEffect(() => { api.get("/ops/overview").then((r) => setD(r.data)); }, []);
  if (!d) return <div className="label-cap">Chargement Operations OS…</div>;
  return (
    <div data-testid="ops-page" className="space-y-6">
      <div>
        <div className="label-cap">Operations OS</div>
        <h1 className="text-3xl font-semibold text-white mt-1">Projets, workflows, incidents</h1>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Kpi label="Projets" value={d.projects.length} testId="ops-projects" />
        <Kpi label="Workflows" value={d.workflows.length} tone="violet" testId="ops-workflows" />
        <Kpi label="Incidents" value={d.incidents.length} tone="gold" testId="ops-incidents" />
        <Kpi label="Tasks ouvertes" value={d.tasks.length} testId="ops-tasks" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CardShell title="Projets actifs" testId="ops-project-list">
          {d.projects.map((p) => (
            <div key={p.id} className="py-2 border-b border-[#1A1C25]">
              <div className="flex items-center justify-between">
                <div className="text-sm text-white">{p.name}</div>
                <SeverityBadge severity={p.priority} />
              </div>
              <div className="label-cap mt-1">{p.entity} · {p.status} · échéance {p.due}</div>
              <div className="h-1 rounded-full bg-[#252633] mt-2">
                <div className="h-1 rounded-full bg-violet-500" style={{ width: `${p.progress}%` }} />
              </div>
            </div>
          ))}
        </CardShell>
        <CardShell title="Workflows" testId="ops-workflow-list">
          {d.workflows.map((w) => (
            <div key={w.id} className="py-2 border-b border-[#1A1C25]">
              <div className="flex items-center gap-2">
                <StatusDot health={w.health} />
                <div className="text-sm text-white flex-1">{w.description}</div>
                <span className="label-cap">{w.status}</span>
              </div>
              <div className="label-cap mt-1">{w.steps_count} étapes · dernière run il y a {Math.abs(Math.round((Date.now() - new Date(w.last_run)) / 3600000))}h</div>
            </div>
          ))}
        </CardShell>
      </div>
      <CardShell title="Incidents ouverts" testId="ops-incident-list">
        {d.incidents.map((i) => (
          <div key={i.id} className="flex items-center gap-3 py-2 border-b border-[#1A1C25]">
            <SeverityBadge severity={i.severity} />
            <div className="flex-1">
              <div className="text-sm text-white">{i.title}</div>
              <div className="label-cap">{i.entity} · {i.status}</div>
            </div>
          </div>
        ))}
      </CardShell>
    </div>
  );
}
