import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { CardShell } from "../components/Kpi";

export default function EvidenceAudit() {
  const [items, setItems] = useState([]);
  useEffect(() => { api.get("/evidence").then((r) => setItems(r.data)); }, []);
  return (
    <div data-testid="evidence-page" className="space-y-6">
      <div>
        <div className="label-cap">Evidence & Audit</div>
        <h1 className="text-3xl font-semibold text-white mt-1">Trace immuable des actions</h1>
        <p className="text-sm text-white/50 mt-2 max-w-2xl">
          Chaque opération produit une preuve : ACTION · ACTOR · TIMESTAMP · INPUT · OUTPUT · APPROVAL.
        </p>
      </div>
      <CardShell title="Journal" testId="evidence-list">
        <div className="max-h-[600px] overflow-auto scroll-thin">
          <table className="w-full text-sm">
            <thead className="label-cap sticky top-0 bg-[#13141C]">
              <tr>
                <th className="text-left py-2">Timestamp</th>
                <th className="text-left">Action</th>
                <th className="text-left">Acteur</th>
                <th className="text-left">Entity</th>
                <th className="text-left">Approval</th>
                <th className="text-left">Trace</th>
              </tr>
            </thead>
            <tbody>
              {items.map((e) => (
                <tr key={e.id} className="border-b border-[#1A1C25]">
                  <td className="py-2 font-mono text-[10px] text-white/60">{new Date(e.timestamp).toLocaleString("fr-FR")}</td>
                  <td className="text-violet-300 font-mono text-xs">{e.action}</td>
                  <td className="text-white/80">{e.actor?.email}</td>
                  <td className="text-white/60">{e.entity_type}</td>
                  <td className="text-amber-400 font-mono text-xs">{e.approval || "-"}</td>
                  <td className="text-white/40 font-mono text-[10px]">{e.trace_id?.slice(0, 8)}…</td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr><td colSpan={6} className="text-center py-10 label-cap">Aucune preuve encore. Effectuez une action pour populer le journal.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </CardShell>
    </div>
  );
}
