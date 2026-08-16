import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Kpi, CardShell, StatusDot, SeverityBadge } from "../components/Kpi";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

export default function CommandCenter() {
  const [data, setData] = useState(null);
  useEffect(() => {
    api.get("/command-center/overview").then((r) => setData(r.data));
  }, []);

  if (!data) return <div className="label-cap">Chargement du Command Center…</div>;

  const eventsByType = {};
  (data.agents || []).forEach((a) => {
    const k = a.authority_scope || "other";
    eventsByType[k] = (eventsByType[k] || 0) + 1;
  });
  const donutData = Object.entries(eventsByType).map(([k, v]) => ({ name: k, value: v }));
  const donutColors = ["#7C3AED", "#F59E0B", "#A78BFA", "#22C55E", "#60A5FA", "#EAB308", "#EF4444"];

  const series = Array.from({ length: 24 }).map((_, i) => ({
    h: `${String(i).padStart(2, "0")}h`,
    v: 40 + Math.round(Math.sin(i / 3) * 30 + Math.random() * 25) + i,
  }));

  return (
    <div data-testid="command-center-page" className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <div className="label-cap">Command Center</div>
          <h1 className="text-3xl font-semibold text-white mt-1 tracking-tight">
            Qu'est-ce qui se passe dans <span className="text-violet-400">CVLN</span> ?
          </h1>
          <p className="text-sm text-white/50 mt-2 max-w-2xl">
            Vue d'ensemble opérationnelle du groupe. Chaque KPI mène à un contexte, une source, une action.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="label-cap">Mode</div>
          <div className="border border-[#252633] rounded-sm px-3 py-1.5 font-mono text-xs text-white bg-[#13141C]">
            Normal
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 stagger-fade">
        <Kpi testId="kpi-health" label="Santé globale" value={`${data.global_health}%`} trend="Excellent" tone="green" />
        <Kpi testId="kpi-events" label="Événements / 24h" value={data.events_24h.toLocaleString("fr-FR")} trend="+18.3%" />
        <Kpi testId="kpi-agents" label="Agents actifs" value={`${data.active_agents}/${data.agents_total}`} tone="violet" />
        <Kpi testId="kpi-cash" label="Trésorerie" value={`€${(data.finance.cash_position_eur / 1_000_000).toFixed(2)}M`} tone="gold" />
        <Kpi testId="kpi-alerts" label="Alertes critiques" value={data.alerts.filter((a)=>a.severity==="critical").length} tone="red" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <CardShell testId="realtime-chart" title="Activité en temps réel · 24h" className="lg:col-span-2">
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={series} margin={{ top: 5, right: 5, bottom: 0, left: -20 }}>
              <defs>
                <linearGradient id="v" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="#7C3AED" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="#7C3AED" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <XAxis dataKey="h" stroke="#4B5563" fontSize={10} tickLine={false} />
              <YAxis stroke="#4B5563" fontSize={10} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: "#13141C", border: "1px solid #252633", borderRadius: 4, fontSize: 12 }} />
              <Area type="monotone" dataKey="v" stroke="#A78BFA" strokeWidth={2} fill="url(#v)" />
            </AreaChart>
          </ResponsiveContainer>
        </CardShell>

        <CardShell testId="agents-donut" title="Répartition des agents">
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={donutData} innerRadius={55} outerRadius={90} dataKey="value" paddingAngle={2}>
                {donutData.map((_, i) => (
                  <Cell key={i} fill={donutColors[i % donutColors.length]} stroke="#0F1017" />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "#13141C", border: "1px solid #252633", borderRadius: 4, fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-2 gap-2 mt-2">
            {donutData.map((d, i) => (
              <div key={d.name} className="flex items-center gap-2 text-xs text-white/70">
                <span className="w-2 h-2 rounded-full" style={{ background: donutColors[i % donutColors.length] }} />
                <span className="truncate">{d.name}</span>
                <span className="font-mono text-white/40 ml-auto">{d.value}</span>
              </div>
            ))}
          </div>
        </CardShell>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CardShell testId="alerts-card" title="Alertes récentes" right={<span className="label-cap text-white/40">{data.alerts.length} ouvertes</span>}>
          <div className="space-y-2">
            {data.alerts.slice(0, 6).map((a) => (
              <div key={a.id} className="flex items-start gap-3 py-2 border-b border-[#1A1C25] last:border-0">
                <SeverityBadge severity={a.severity} />
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-white truncate">{a.message}</div>
                  <div className="label-cap mt-0.5">{a.module} · {a.source}</div>
                </div>
              </div>
            ))}
          </div>
        </CardShell>

        <CardShell testId="decisions-card" title="Décisions en attente" right={<span className="label-cap text-amber-400">{data.pending_decisions.length} à traiter</span>}>
          <div className="space-y-2">
            {data.pending_decisions.slice(0, 5).map((d) => (
              <div key={d.id} className="py-2 border-b border-[#1A1C25] last:border-0">
                <div className="flex items-center gap-2">
                  <SeverityBadge severity={d.priority} />
                  <div className="text-sm text-white flex-1 truncate">{d.title}</div>
                </div>
                <div className="label-cap mt-1 text-white/50">{d.category} · owner {d.owner_email}</div>
              </div>
            ))}
          </div>
        </CardShell>
      </div>

      <CardShell testId="entities-strip" title="Écosystème CVLN">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {data.entities.slice(0, 12).map((e) => (
            <div key={e.id} className="border border-[#252633] rounded-sm p-3 hover:border-violet-500/60 transition-colors">
              <div className="flex items-center gap-2">
                <StatusDot health={e.health} />
                <div className="font-mono text-xs text-white truncate">{e.name}</div>
              </div>
              <div className="label-cap mt-1">{e.layer}</div>
            </div>
          ))}
        </div>
      </CardShell>
    </div>
  );
}
