import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Kpi, CardShell } from "../components/Kpi";

export default function PeopleOS() {
  const [d, setD] = useState(null);
  useEffect(() => { api.get("/people/overview").then((r) => setD(r.data)); }, []);
  if (!d) return <div className="label-cap">Chargement People OS…</div>;

  return (
    <div data-testid="people-page" className="space-y-6">
      <div>
        <div className="label-cap">People OS</div>
        <h1 className="text-3xl font-semibold text-white mt-1">Human Capital</h1>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Kpi label="Headcount" value={d.headcount} testId="people-headcount" />
        <Kpi label="Onboarding" value={d.onboarding.length} tone="gold" testId="people-onboarding" />
        <Kpi label="Absences" value={d.absences.length} testId="people-absences" />
        <Kpi label="Objectifs actifs" value={d.objectives.length} tone="violet" testId="people-objectives" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CardShell title="Collaborateurs" testId="people-list">
          <div className="max-h-[420px] overflow-auto scroll-thin">
            {d.people.map((p) => (
              <div key={p.id} className="flex items-center gap-3 py-2 border-b border-[#1A1C25]">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-amber-500 flex items-center justify-center text-[10px] font-mono">
                  {p.name.split(" ").map((n) => n[0]).join("").slice(0, 2)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-white truncate">{p.name}</div>
                  <div className="label-cap">{p.role} · {p.entity}</div>
                </div>
                <span className={`label-cap ${p.status === "onboarding" ? "text-amber-400" : "text-emerald-400"}`}>{p.status}</span>
              </div>
            ))}
          </div>
        </CardShell>
        <CardShell title="Objectifs & OKR" testId="people-objectives-card">
          {d.objectives.map((o) => (
            <div key={o.id} className="py-2 border-b border-[#1A1C25]">
              <div className="flex justify-between">
                <div className="text-sm text-white">{o.title}</div>
                <div className="font-mono text-xs text-violet-300">{o.progress}%</div>
              </div>
              <div className="label-cap mt-1">{o.person}</div>
              <div className="h-1 rounded-full bg-[#252633] mt-2">
                <div className="h-1 rounded-full bg-violet-500" style={{ width: `${o.progress}%` }} />
              </div>
            </div>
          ))}
        </CardShell>
      </div>
    </div>
  );
}
