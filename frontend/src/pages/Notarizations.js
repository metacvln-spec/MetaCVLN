import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { Kpi, CardShell } from "../components/Kpi";

export default function Notarizations() {
  const [data, setData] = useState(null);
  const [verifying, setVerifying] = useState(null);
  const [verified, setVerified] = useState({});

  async function load() {
    const { data } = await api.get("/notarizations");
    setData(data);
  }
  useEffect(() => { load(); }, []);

  async function verify(id) {
    setVerifying(id);
    try {
      const { data } = await api.post(`/notarizations/${id}/verify`);
      setVerified((v) => ({ ...v, [id]: data }));
      toast[data.valid ? "success" : "error"](data.valid ? "Signature valide ✓" : `Invalide: ${data.reason}`);
    } finally {
      setVerifying(null);
    }
  }

  if (!data) return <div className="label-cap">Chargement…</div>;

  const notary = data.notary || {};
  const items = data.notarizations || [];

  return (
    <div data-testid="notarizations-page" className="space-y-6">
      <div>
        <div className="label-cap">Notarization Ledger</div>
        <h1 className="text-3xl font-semibold text-white mt-1 tracking-tight">
          Trust chain · <span className="text-amber-400">Ed25519 signed</span>
        </h1>
        <p className="text-sm text-white/50 mt-2 max-w-3xl">
          Chaque événement notarisé quand FREKCORE est CONNECTED est signé
          cryptographiquement (Ed25519). Un auditeur peut vérifier chaque
          signature via <span className="font-mono text-violet-300">POST /api/notarizations/&#123;id&#125;/verify</span>.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Kpi label="Notarisations" value={data.count} tone="gold" testId="notar-count" />
        <div className="surface-card p-4 md:col-span-2">
          <div className="label-cap">Meta CVLN Notary · Public Key</div>
          <div className="font-mono text-[10px] text-white/70 mt-2 break-all">
            {notary.public_b64 || "—"}
          </div>
          <div className="flex flex-wrap gap-4 mt-2">
            <div>
              <div className="label-cap">DID</div>
              <div className="font-mono text-xs text-violet-300">{notary.did || "—"}</div>
            </div>
            <div>
              <div className="label-cap">Algorithm</div>
              <div className="font-mono text-xs text-white/80">{notary.algorithm || "ed25519"}</div>
            </div>
            <div>
              <div className="label-cap">Créé</div>
              <div className="font-mono text-xs text-white/80">
                {notary.created_at ? new Date(notary.created_at).toLocaleString("fr-FR") : "—"}
              </div>
            </div>
          </div>
        </div>
      </div>

      <CardShell title="Ledger" testId="notar-list">
        <div className="max-h-[620px] overflow-auto scroll-thin">
          <table className="w-full text-sm">
            <thead className="label-cap sticky top-0 bg-[#13141C]">
              <tr>
                <th className="text-left py-2">Timestamp</th>
                <th className="text-left">Target</th>
                <th className="text-left">Repo</th>
                <th className="text-left">Status</th>
                <th className="text-left">SHA-256</th>
                <th className="text-left">Signature (ed25519)</th>
                <th className="text-right">Verify</th>
              </tr>
            </thead>
            <tbody>
              {items.length === 0 && (
                <tr><td colSpan={7} className="text-center py-10 label-cap">
                  Aucune notarisation encore. Configurez FREKCORE puis lancez un ping.
                </td></tr>
              )}
              {items.map((n) => {
                const v = verified[n.id];
                return (
                  <tr key={n.id} className="border-b border-[#1A1C25] hover:bg-white/[0.02]">
                    <td className="py-2 font-mono text-[10px] text-white/60">
                      {new Date(n.created_at).toLocaleString("fr-FR")}
                    </td>
                    <td className="text-white/80 text-xs">{n.target_type}</td>
                    <td className="text-violet-300 text-xs">{n.target_repo_key}</td>
                    <td>
                      <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded-sm border ${
                        n.status === "CONNECTED"
                          ? "text-emerald-400 border-emerald-500/40 bg-emerald-500/10"
                          : "text-red-400 border-red-500/40 bg-red-500/10"
                      }`}>{n.status}</span>
                    </td>
                    <td className="font-mono text-[10px] text-white/60 max-w-[180px] truncate" title={n.sha256}>
                      {n.sha256?.slice(0, 24)}…
                    </td>
                    <td className="font-mono text-[10px] text-amber-400 max-w-[180px] truncate" title={n.signature_b64}>
                      {n.signature_b64?.slice(0, 24)}…
                    </td>
                    <td className="text-right">
                      {v ? (
                        <span className={`text-[10px] font-mono px-2 py-0.5 rounded-sm border ${
                          v.valid
                            ? "text-emerald-400 border-emerald-500/40 bg-emerald-500/10"
                            : "text-red-400 border-red-500/40 bg-red-500/10"
                        }`}>{v.valid ? "VALID ✓" : "INVALID"}</span>
                      ) : (
                        <button
                          data-testid={`verify-${n.id}`}
                          onClick={() => verify(n.id)}
                          disabled={verifying === n.id}
                          className="btn-ghost text-[10px] disabled:opacity-50"
                        >
                          {verifying === n.id ? "…" : "Verify"}
                        </button>
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
