import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Kpi, CardShell } from "../components/Kpi";

export default function WeeklyReport() {
  const [report, setReport] = useState(null);
  const [history, setHistory] = useState([]);
  useEffect(() => {
    api.get("/reports/weekly-drop/latest").then((r) => setReport(r.data));
    api.get("/reports/weekly-drop").then((r) => setHistory(r.data));
  }, []);
  if (!report || !report.id) {
    return (
      <div data-testid="weekly-report-page" className="space-y-6">
        <div>
          <div className="label-cap">Weekly Drop Report</div>
          <h1 className="text-3xl font-semibold text-white mt-1">Rapport hebdomadaire d'uptime</h1>
        </div>
        <div className="surface-card p-8 text-center">
          <div className="label-cap text-white/50">
            Le premier rapport sera généré lundi 09:00 CET par le cron `weekly-drop-report`.
            Pour un aperçu immédiat, appelez `POST /api/cron/weekly-drop-report` avec le webhook secret.
          </div>
        </div>
      </div>
    );
  }
  const rows = report.rows || [];
  return (
    <div data-testid="weekly-report-page" className="space-y-6">
      <div>
        <div className="label-cap">Weekly Drop Report</div>
        <h1 className="text-3xl font-semibold text-white mt-1 tracking-tight">
          Uptime · <span className="text-amber-400">7 derniers jours</span>
        </h1>
        <p className="text-sm text-white/50 mt-2">
          Généré le {new Date(report.created_at).toLocaleString("fr-FR")} · seuil d'alerte {report.threshold_pct}%
        </p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Kpi label="Repos surveillés" value={report.total_repos} tone="violet" testId="wr-total" />
        <Kpi label="Sous 95%" value={report.flagged_count} tone={report.flagged_count ? "red" : "green"} testId="wr-flagged" />
        <Kpi label="Rapports archivés" value={history.length} testId="wr-hist" />
        <Kpi label="Période" value={`${report.period_days}j`} tone="gold" testId="wr-period" />
      </div>
      <CardShell title="Uptime par repo" testId="wr-table">
        <table className="w-full text-sm">
          <thead className="label-cap">
            <tr>
              <th className="text-left py-2">Repo</th>
              <th className="text-right">Pings 7j</th>
              <th className="text-right">Up</th>
              <th className="text-right">Uptime</th>
              <th className="text-right">Latence moy.</th>
              <th className="text-right">Flag</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.repo_key} className="border-b border-[#1A1C25]">
                <td className="py-2 text-violet-300">{r.repo_key}</td>
                <td className="text-right font-mono text-xs text-white/80">{r.total_pings}</td>
                <td className="text-right font-mono text-xs text-white/80">{r.up}</td>
                <td className={`text-right font-mono ${r.uptime_pct >= 95 ? "text-emerald-400" : "text-red-400"}`}>{r.uptime_pct}%</td>
                <td className="text-right font-mono text-xs text-white/70">{r.avg_ms}ms</td>
                <td className="text-right">
                  {r.flag && (
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded-sm border text-red-400 border-red-500/40 bg-red-500/10">FLAG</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardShell>
    </div>
  );
}
