import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Kpi, CardShell, SeverityBadge } from "../components/Kpi";
import { useAuth } from "../contexts/AuthContext";

export default function Workbench() {
  const { user } = useAuth();
  const [d, setD] = useState(null);
  useEffect(() => {
    api.get("/workbench").then((r) => setD(r.data));
  }, []);
  if (!d) return <div className="label-cap">Chargement Workbench…</div>;

  return (
    <div data-testid="workbench-page" className="space-y-6">
      <div>
        <div className="label-cap">My Workspace</div>
        <h1 className="text-3xl font-semibold text-white mt-1 tracking-tight">
          Bonjour, <span className="text-violet-400">{user?.name || user?.email}</span>
        </h1>
        <p className="text-sm text-white/50 mt-2 max-w-2xl">
          Voici ce qui nécessite votre attention aujourd'hui. Priorisé par le OS.
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 stagger-fade">
        {d.kpis.map((k, i) => (
          <Kpi key={i} label={k.label} value={k.value} trend={k.trend} testId={`workbench-kpi-${i}`} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <CardShell title="Travail prioritaire" testId="priority-tasks" className="lg:col-span-2">
          <div className="space-y-2">
            {d.priority_tasks.map((t) => (
              <div key={t.id} className="flex items-center gap-3 py-2 border-b border-[#1A1C25] last:border-0">
                <SeverityBadge severity={t.priority} />
                <div className="text-sm text-white flex-1">{t.title}</div>
                <div className="label-cap">{t.assignee_email}</div>
              </div>
            ))}
          </div>
        </CardShell>

        <CardShell title="Décisions à prendre" testId="workbench-decisions">
          {d.decisions_pending.map((x) => (
            <div key={x.id} className="py-2 border-b border-[#1A1C25] last:border-0">
              <SeverityBadge severity={x.priority} />
              <div className="text-sm text-white mt-1">{x.title}</div>
            </div>
          ))}
        </CardShell>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CardShell title="Projets" testId="workbench-projects">
          {d.projects.map((p) => (
            <div key={p.id} className="py-2 border-b border-[#1A1C25] last:border-0">
              <div className="flex items-center justify-between">
                <div className="text-sm text-white">{p.name}</div>
                <div className="label-cap">{p.entity}</div>
              </div>
              <div className="h-1 rounded-full bg-[#252633] mt-2">
                <div className="h-1 rounded-full bg-violet-500" style={{ width: `${p.progress}%` }} />
              </div>
            </div>
          ))}
        </CardShell>
        <CardShell title="Mes alertes" testId="workbench-alerts">
          {d.alerts.map((a) => (
            <div key={a.id} className="flex items-start gap-3 py-2 border-b border-[#1A1C25] last:border-0">
              <SeverityBadge severity={a.severity} />
              <div className="text-sm text-white">{a.message}</div>
            </div>
          ))}
        </CardShell>
      </div>
    </div>
  );
}
