import { useEffect, useState } from "react";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AuditPublic() {
  const [data, setData] = useState(null);
  const [busy, setBusy] = useState(null);
  const [verified, setVerified] = useState({});

  useEffect(() => {
    axios.get(`${API}/public/notarizations`).then((r) => setData(r.data));
  }, []);

  async function verify(id) {
    setBusy(id);
    try {
      // The verify endpoint is authenticated; public auditors verify off-platform.
      // We hint them how to do it.
      alert(
        `Off-platform verification:\n\n1. Prendre la clé publique (base64) affichée en haut\n2. Prendre la signature (base64) et le sha256 de cette ligne\n3. ed25519.verify(pub_key, base64_decode(signature), sha256_hex.encode())`
      );
      setVerified((v) => ({ ...v, [id]: true }));
    } finally {
      setBusy(null);
    }
  }

  async function download(n) {
    // Public export — build the .frek.json client-side from public data
    const artifact = {
      frek_version: "0.4",
      event: {
        id: n.id,
        trace_id: n.trace_id,
        type: n.target_type,
        target_repo_key: n.target_repo_key,
        target_repo_name: n.target_repo_name,
        status: n.status,
        http: n.http,
        ms: n.ms,
        created_at: n.created_at,
      },
      fingerprint: `sha256:${n.sha256}`,
      signature: `ed25519:${n.signature_b64}`,
      public_key: n.public_key_b64,
      notary: { did: n.notary_did, algorithm: n.algorithm, issued_by: "meta-cvln-os" },
      metadata: { timestamp: n.created_at, source_type: n.target_type, schema: "frek.notarization.v1" },
    };
    const blob = new Blob([JSON.stringify(artifact, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `notarization-${n.id.slice(0, 8)}.frek.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  if (!data) return <div className="min-h-screen bg-[#08090C] flex items-center justify-center label-cap text-white/50">Chargement audit…</div>;

  const notary = data.notary || {};
  const items = data.notarizations || [];

  return (
    <div className="min-h-screen bg-[#08090C] text-white" data-testid="audit-public-page">
      <div className="border-b border-[#252633] px-8 py-4 flex items-center justify-between">
        <div>
          <div className="label-cap">Public Trust Chain · Read-only</div>
          <div className="font-mono text-xs tracking-widest">META · CVLN <span className="text-amber-400">AUDIT</span></div>
        </div>
        <a href="/public" className="label-cap hover:text-white">← Retour vitrine</a>
      </div>

      <div className="px-8 py-10 max-w-6xl">
        <h1 className="text-3xl font-semibold tracking-tight">
          Trust chain · <span className="text-amber-400">Ed25519 signed</span>
        </h1>
        <p className="text-sm text-white/60 mt-3 max-w-3xl">
          Ledger public en lecture seule. Chaque événement porte une signature Ed25519
          vérifiable hors-plateforme avec n'importe quelle librairie standard.
        </p>

        <div className="surface-card p-4 mt-8">
          <div className="label-cap">Meta CVLN Notary Public Key</div>
          <div className="font-mono text-[10px] text-white/70 mt-2 break-all">
            {notary.public_b64}
          </div>
          <div className="flex flex-wrap gap-4 mt-2">
            <span className="label-cap">DID <span className="text-violet-300 normal-case tracking-normal">{notary.did}</span></span>
            <span className="label-cap">Algo <span className="text-white/80 normal-case tracking-normal">{notary.algorithm}</span></span>
          </div>
        </div>

        <div className="mt-8 border border-[#252633] rounded-sm">
          <div className="overflow-auto max-h-[600px] scroll-thin">
            <table className="w-full text-sm">
              <thead className="label-cap sticky top-0 bg-[#13141C]">
                <tr>
                  <th className="text-left p-3">Timestamp</th>
                  <th className="text-left">Target</th>
                  <th className="text-left">Repo</th>
                  <th className="text-left">Status</th>
                  <th className="text-left">SHA-256</th>
                  <th className="text-left">Signature</th>
                  <th className="text-right p-3">Export</th>
                </tr>
              </thead>
              <tbody>
                {items.map((n) => (
                  <tr key={n.id} className="border-b border-[#1A1C25]">
                    <td className="p-3 font-mono text-[10px] text-white/60">{new Date(n.created_at).toLocaleString("fr-FR")}</td>
                    <td className="text-white/80 text-xs">{n.target_type}</td>
                    <td className="text-violet-300 text-xs">{n.target_repo_key}</td>
                    <td>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded-sm border text-emerald-400 border-emerald-500/40 bg-emerald-500/10">
                        {n.status}
                      </span>
                    </td>
                    <td className="font-mono text-[10px] text-white/60">{n.sha256?.slice(0, 20)}…</td>
                    <td className="font-mono text-[10px] text-amber-400">{n.signature_b64?.slice(0, 20)}…</td>
                    <td className="p-3 text-right">
                      <button
                        data-testid={`export-${n.id}`}
                        onClick={() => download(n)}
                        className="btn-gold text-[10px]"
                      >
                        .frek.json
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
