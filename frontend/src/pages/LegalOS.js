import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Kpi, CardShell, SeverityBadge } from "../components/Kpi";

export default function LegalOS() {
  const [d, setD] = useState(null);
  useEffect(() => { api.get("/legal/overview").then((r) => setD(r.data)); }, []);
  if (!d) return <div className="label-cap">Chargement Legal OS…</div>;
  return (
    <div data-testid="legal-page" className="space-y-6">
      <div>
        <div className="label-cap">Legal OS</div>
        <h1 className="text-3xl font-semibold text-white mt-1">Contrats, obligations, risques</h1>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Kpi label="Contrats" value={d.contracts.length} testId="legal-contracts" />
        <Kpi label="Expirent < 60j" value={d.expiring_soon.length} tone="gold" testId="legal-expiring" />
        <Kpi label="Risques élevés" value={d.risks.length} tone="red" testId="legal-risks" />
        <Kpi label="Obligations" value={d.obligations.length} testId="legal-obligations" />
      </div>
      <CardShell title="Contrats" testId="legal-list">
        <div className="overflow-auto scroll-thin max-h-[500px]">
          <table className="w-full text-sm">
            <thead className="label-cap sticky top-0 bg-[#13141C]">
              <tr>
                <th className="text-left py-2">Nom</th>
                <th className="text-left">Entité</th>
                <th className="text-left">Type</th>
                <th className="text-left">Risque</th>
                <th className="text-right">Valeur/an</th>
                <th className="text-right">Expire dans</th>
              </tr>
            </thead>
            <tbody>
              {d.contracts.map((c) => (
                <tr key={c.id} className="border-b border-[#1A1C25]">
                  <td className="py-2 text-white">{c.name}</td>
                  <td className="text-white/60">{c.entity}</td>
                  <td className="text-white/60">{c.kind}</td>
                  <td><SeverityBadge severity={c.risk_level} /></td>
                  <td className="text-right font-mono text-white/80">€{(c.annual_value_eur || 0).toLocaleString("fr-FR")}</td>
                  <td className="text-right font-mono text-amber-400">{c.days_to_expiry}j</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardShell>
      <CardShell title="Obligations réglementaires" testId="legal-obligs">
        {d.obligations.map((o) => (
          <div key={o.id} className="flex justify-between py-2 border-b border-[#1A1C25]">
            <div>
              <div className="text-sm text-white">{o.title}</div>
              <div className="label-cap">{o.entity}</div>
            </div>
            <div className="font-mono text-xs text-amber-400">dans {o.due_in_days}j</div>
          </div>
        ))}
      </CardShell>
    </div>
  );
}
