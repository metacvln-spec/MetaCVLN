import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Kpi, CardShell } from "../components/Kpi";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid } from "recharts";

const fmt = (n) => `€${(n / 1000).toFixed(0)}k`;

export default function FinanceOS() {
  const [d, setD] = useState(null);
  useEffect(() => { api.get("/finance/overview").then((r) => setD(r.data)); }, []);
  if (!d) return <div className="label-cap">Chargement Finance OS…</div>;
  const s = d.snapshot || {};
  return (
    <div data-testid="finance-page" className="space-y-6">
      <div>
        <div className="label-cap">Finance OS</div>
        <h1 className="text-3xl font-semibold text-white mt-1">Trésorerie, Marge, Allocation</h1>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Kpi label="Cash Position" value={`€${(s.cash_position_eur / 1e6).toFixed(2)}M`} tone="gold" testId="fin-cash" />
        <Kpi label="Revenue YTD" value={`€${(s.revenue_ytd_eur / 1e6).toFixed(2)}M`} trend="+23.5%" tone="green" testId="fin-rev" />
        <Kpi label="EBITDA" value={`€${(s.ebitda_eur / 1e6).toFixed(2)}M`} trend="+18.7%" testId="fin-ebitda" />
        <Kpi label="Runway" value={`${s.runway_months} mois`} tone="violet" testId="fin-runway" />
        <Kpi label="Gross margin" value={`${s.gross_margin_pct}%`} testId="fin-margin" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CardShell title="Cashflow · 6 mois" testId="fin-cashflow">
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={d.cashflow_series}>
              <CartesianGrid stroke="#1E1F2A" strokeDasharray="2 4" />
              <XAxis dataKey="month" stroke="#4B5563" fontSize={10} tickLine={false} />
              <YAxis stroke="#4B5563" fontSize={10} tickLine={false} tickFormatter={fmt} />
              <Tooltip contentStyle={{ background: "#13141C", border: "1px solid #252633", fontSize: 12 }} formatter={(v) => fmt(v)} />
              <Line type="monotone" dataKey="in" stroke="#22C55E" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="out" stroke="#F59E0B" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
          <div className="flex gap-4 mt-2 label-cap">
            <span><span className="dot-status dot-green mr-2" />Entrées</span>
            <span><span className="dot-status dot-amber mr-2" />Sorties</span>
          </div>
        </CardShell>

        <CardShell title="P&L par entité" testId="fin-entities">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={d.entities_pnl} layout="vertical" margin={{ left: 40 }}>
              <XAxis type="number" stroke="#4B5563" fontSize={10} tickFormatter={fmt} />
              <YAxis type="category" dataKey="entity" stroke="#4B5563" fontSize={10} width={110} />
              <Tooltip contentStyle={{ background: "#13141C", border: "1px solid #252633", fontSize: 12 }} formatter={(v) => fmt(v)} />
              <Bar dataKey="margin" fill="#7C3AED" radius={[0, 2, 2, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardShell>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <CardShell title="Budgets · Alloués vs Dépensés" testId="fin-budgets">
          {d.budgets.map((b) => (
            <div key={b.category} className="py-2 border-b border-[#1A1C25]">
              <div className="flex justify-between">
                <div className="text-sm text-white">{b.category}</div>
                <div className="font-mono text-xs">
                  <span className="text-amber-400">{fmt(b.spent)}</span>
                  <span className="text-white/40"> / {fmt(b.allocated)}</span>
                </div>
              </div>
              <div className="h-1 rounded-full bg-[#252633] mt-2">
                <div className="h-1 rounded-full bg-amber-500" style={{ width: `${(b.spent / b.allocated) * 100}%` }} />
              </div>
            </div>
          ))}
        </CardShell>
        <CardShell title="Créances" testId="fin-recv">
          {d.receivables.map((r, i) => (
            <div key={i} className="flex items-center justify-between py-2 border-b border-[#1A1C25]">
              <div>
                <div className="text-sm text-white">{r.client}</div>
                <div className="label-cap">{r.days_overdue}j retard</div>
              </div>
              <div className="font-mono text-sm text-white">{fmt(r.amount_eur)}</div>
            </div>
          ))}
        </CardShell>
        <CardShell title="Approbations en attente" testId="fin-approvals">
          {d.approvals.length === 0 && <div className="label-cap">Aucune approbation en attente.</div>}
          {d.approvals.map((a) => (
            <div key={a.id} className="py-2 border-b border-[#1A1C25]">
              <div className="text-sm text-white">{a.title}</div>
              <div className="label-cap">{a.priority}</div>
            </div>
          ))}
        </CardShell>
      </div>
    </div>
  );
}
