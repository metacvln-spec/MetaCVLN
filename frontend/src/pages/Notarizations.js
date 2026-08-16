import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { Kpi, CardShell } from "../components/Kpi";

export default function Notarizations() {
  const [data, setData] = useState(null);
  const [repos, setRepos] = useState([]);
  const [verifying, setVerifying] = useState(null);
  const [verified, setVerified] = useState({});
  const [filters, setFilters] = useState({ repo_key: "", status: "", since: "", until: "" });

  async function load(f = filters) {
    const params = Object.fromEntries(Object.entries(f).filter(([, v]) => v));
    const { data } = await api.get("/notarizations", { params });
    setData(data);
  }
  useEffect(() => {
    load();
    api.get("/registry/repositories").then((r) => setRepos(r.data.repositories));
  }, []);

  function applyFilters() { load(filters); }
  function resetFilters() {
    const empty = { repo_key: "", status: "", since: "", until: "" };
    setFilters(empty);
    load(empty);
  }

  async function verify(id) {
    setVerifying(id);
    try {
      const { data } = await api.post(`/notarizations/${id}/verify`);
      setVerified((v) => ({ ...v, [id]: data }));
      toast[data.valid ? "success" : "error"](data.valid ? "Signature valide ✓" : `Invalide: ${data.reason}`);
    } finally { setVerifying(null); }
  }

  if (!data) return <div className="label-cap">Chargement…</div>;
  const notary = data.notary || {};
  const items = data.notarizations || [];
  const localCount = items.filter((n) => (n.notary_source || "local") === "local").length;
  const frekCount = items.filter((n) => n.notary_source === "frekcore").length;

  return (
    <div data-testid="notarizations-page" className="space-y-6">
      <div>
        <div className="label-cap">Notary Ledger</div>
        <h1 className="text-3xl font-semibold text-white mt-1 tracking-tight">
          Trust chain · <span className="text-amber-400">Ed25519 signed</span>
        </h1>
        <p className="text-sm text-white/50 mt-2 max-w-3xl">
          FK Object v3 signé Ed25519. Export `.fk` par ligne. Filtrable par repo, statut, période.
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Kpi label="Total signatures" value={data.count} tone="gold" testId="notar-count" />
        <Kpi label="via FREKCORE" value={frekCount} tone="violet" testId="notar-frek" />
        <Kpi label="via Meta local" value={localCount} testId="notar-local" />
        <Kpi label="Notary DID" value={<span className="text-xs">{notary.did?.slice(0, 22) || "—"}</span>} testId="notar-did" />
      </div>

      <CardShell title="Filters" testId="notar-filters">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <div>
            <div className="label-cap mb-1">Repo</div>
            <select data-testid="filter-repo" value={filters.repo_key} onChange={(e) => setFilters({ ...filters, repo_key: e.target.value })}
              className="w-full bg-[#0F1017] border border-[#252633] rounded-sm px-3 py-2 text-sm text-white font-mono text-xs">
              <option value="">Tous</option>
              {repos.map((r) => <option key={r.key} value={r.key}>{r.key}</option>)}
            </select>
          </div>
          <div>
            <div className="label-cap mb-1">Statut</div>
            <select data-testid="filter-status" value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="w-full bg-[#0F1017] border border-[#252633] rounded-sm px-3 py-2 text-sm text-white font-mono text-xs">
              <option value="">Tous</option>
              <option value="CONNECTED">CONNECTED</option>
              <option value="ERROR">ERROR</option>
            </select>
          </div>
          <div>
            <div className="label-cap mb-1">Depuis</div>
            <input type="datetime-local" data-testid="filter-since" value={filters.since}
              onChange={(e) => setFilters({ ...filters, since: e.target.value ? new Date(e.target.value).toISOString() : "" })}
              className="w-full bg-[#0F1017] border border-[#252633] rounded-sm px-3 py-2 text-sm text-white font-mono text-xs" />
          </div>
          <div>
            <div className="label-cap mb-1">Jusqu'à</div>
            <input type="datetime-local" data-testid="filter-until" value={filters.until}
              onChange={(e) => setFilters({ ...filters, until: e.target.value ? new Date(e.target.value).toISOString() : "" })}
              className="w-full bg-[#0F1017] border border-[#252633] rounded-sm px-3 py-2 text-sm text-white font-mono text-xs" />
          </div>
          <div className="flex items-end gap-2">
            <button data-testid="filter-apply" onClick={applyFilters} className="btn-primary flex-1">Appliquer</button>
            <button data-testid="filter-reset" onClick={resetFilters} className="btn-ghost">Reset</button>
          </div>
        </div>
      </CardShell>

      <div className="surface-card p-4">
        <div className="label-cap">Meta CVLN Notary · Public Key</div>
        <div className="font-mono text-[10px] text-white/70 mt-2 break-all">{notary.public_b64 || "—"}</div>
        <div className="flex flex-wrap gap-4 mt-2 label-cap">
          <span>DID <span className="text-violet-300 normal-case tracking-normal">{notary.did || "—"}</span></span>
          <span>Algo <span className="text-white/80 normal-case tracking-normal">ed25519</span></span>
        </div>
      </div>

      <CardShell title="Ledger" testId="notar-list">
        <div className="max-h-[520px] overflow-auto scroll-thin">
          <table className="w-full text-sm">
            <thead className="label-cap sticky top-0 bg-[#13141C]">
              <tr>
                <th className="text-left py-2">Timestamp</th>
                <th className="text-left">Target</th>
                <th className="text-left">Repo</th>
                <th className="text-left">Status</th>
                <th className="text-left">Source</th>
                <th className="text-left">SHA-256</th>
                <th className="text-left">Signature</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.length === 0 && (
                <tr><td colSpan={8} className="text-center py-10 label-cap">Aucune notarisation avec ces filtres.</td></tr>
              )}
              {items.map((n) => {
                const v = verified[n.id];
                const src = n.notary_source || "local";
                return (
                  <tr key={n.id} className="border-b border-[#1A1C25] hover:bg-white/[0.02]">
                    <td className="py-2 font-mono text-[10px] text-white/60">{new Date(n.created_at).toLocaleString("fr-FR")}</td>
                    <td className="text-white/80 text-xs">{n.target_type}</td>
                    <td className="text-violet-300 text-xs">{n.target_repo_key}</td>
                    <td>
                      <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded-sm border ${
                        n.status === "CONNECTED" ? "text-emerald-400 border-emerald-500/40 bg-emerald-500/10" : "text-red-400 border-red-500/40 bg-red-500/10"
                      }`}>{n.status}</span>
                    </td>
                    <td>
                      <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded-sm border ${
                        src === "frekcore" ? "text-violet-400 border-violet-500/40 bg-violet-500/10" : "text-white/50 border-[#252633]"
                      }`}>{src}</span>
                    </td>
                    <td className="font-mono text-[10px] text-white/60 max-w-[160px] truncate" title={n.sha256}>{n.sha256?.slice(0, 20)}…</td>
                    <td className="font-mono text-[10px] text-amber-400 max-w-[160px] truncate" title={n.signature_b64}>{n.signature_b64?.slice(0, 20)}…</td>
                    <td className="text-right">
                      {v ? (
                        <span className={`text-[10px] font-mono px-2 py-0.5 rounded-sm border ${
                          v.valid ? "text-emerald-400 border-emerald-500/40 bg-emerald-500/10" : "text-red-400 border-red-500/40 bg-red-500/10"
                        }`}>{v.valid ? "VALID ✓" : "INVALID"}</span>
                      ) : (
                        <div className="flex justify-end gap-1">
                          <button data-testid={`verify-${n.id}`} onClick={() => verify(n.id)} disabled={verifying === n.id} className="btn-ghost text-[10px] disabled:opacity-50">
                            {verifying === n.id ? "…" : "Verify"}
                          </button>
                          <a data-testid={`export-${n.id}`} href={`${process.env.REACT_APP_BACKEND_URL}/api/notarizations/${n.id}/export`}
                            target="_blank" rel="noreferrer" className="btn-gold text-[10px]"
                            download={`fk-${n.id.slice(0,8)}.fk`}>.fk</a>
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </CardShell>
    </div>
  );
}
