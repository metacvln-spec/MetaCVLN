import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Kpi, CardShell } from "../components/Kpi";

export default function KnowledgeOS() {
  const [d, setD] = useState(null);
  useEffect(() => { api.get("/knowledge/overview").then((r) => setD(r.data)); }, []);
  if (!d) return <div className="label-cap">Chargement Knowledge OS…</div>;
  return (
    <div data-testid="knowledge-page" className="space-y-6">
      <div>
        <div className="label-cap">Knowledge OS</div>
        <h1 className="text-3xl font-semibold text-white mt-1">Mémoire opérationnelle</h1>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Kpi label="Documents" value={d.documents.length} testId="kn-docs" />
        <Kpi label="Orphelins" value={d.orphans.length} tone="red" testId="kn-orphans" />
        <Kpi label="Sources uniques" value={Object.keys(d.by_source).length} tone="violet" testId="kn-sources" />
        <Kpi label="Récents 20" value={d.recent.length} testId="kn-recent" />
      </div>
      <CardShell title="Documents · Source · Owner · Fraîcheur" testId="kn-list">
        <div className="overflow-auto scroll-thin max-h-[520px]">
          <table className="w-full text-sm">
            <thead className="label-cap sticky top-0 bg-[#13141C]">
              <tr>
                <th className="text-left py-2">Titre</th>
                <th className="text-left">Source</th>
                <th className="text-left">Owner</th>
                <th className="text-left">Version</th>
                <th className="text-right">Confiance</th>
                <th className="text-right">Fraîcheur</th>
              </tr>
            </thead>
            <tbody>
              {d.documents.map((doc) => (
                <tr key={doc.id} className="border-b border-[#1A1C25]">
                  <td className="py-2 text-white">{doc.title}</td>
                  <td className="text-white/60">{doc.source_system}</td>
                  <td className={doc.owner ? "text-white/80" : "text-red-400"}>{doc.owner || "ORPHELIN"}</td>
                  <td className="font-mono text-xs text-violet-300">v{doc.version}</td>
                  <td className="text-right font-mono text-white/80">{Math.round(doc.confidence * 100)}%</td>
                  <td className="text-right font-mono text-amber-400">{Math.round(doc.freshness * 100)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardShell>
    </div>
  );
}
