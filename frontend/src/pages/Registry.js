import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { CardShell, Kpi, StatusDot } from "../components/Kpi";

const STATUS_COLORS = {
  CONNECTED: "text-emerald-400 border-emerald-500/40 bg-emerald-500/10",
  NOT_CONNECTED: "text-white/50 border-[#252633] bg-transparent",
  ERROR: "text-red-400 border-red-500/40 bg-red-500/10",
};

export default function Registry() {
  const [repos, setRepos] = useState([]);
  const [busy, setBusy] = useState(null);
  const [expanded, setExpanded] = useState(null);
  const [drafts, setDrafts] = useState({});

  async function load() {
    const { data } = await api.get("/registry/repositories");
    setRepos(data.repositories);
  }
  useEffect(() => { load(); }, []);

  async function ping(id) {
    setBusy(id);
    try {
      const { data } = await api.post(`/registry/repositories/${id}/ping`);
      toast[data.status === "CONNECTED" ? "success" : "error"](
        `${data.status} · HTTP ${data.http ?? "—"} · ${data.ms}ms`
      );
      await load();
    } catch (e) {
      toast.error(`Ping failed: ${e.response?.data?.detail || e.message}`);
    } finally {
      setBusy(null);
    }
  }

  async function save(id) {
    const body = drafts[id] || {};
    setBusy(id);
    try {
      await api.patch(`/registry/repositories/${id}`, body);
      toast.success("Configuration enregistrée");
      setDrafts((d) => ({ ...d, [id]: {} }));
      await load();
    } catch (e) {
      toast.error(`Save failed: ${e.response?.data?.detail || e.message}`);
    } finally {
      setBusy(null);
    }
  }

  function updateDraft(id, field, value) {
    setDrafts((d) => ({ ...d, [id]: { ...(d[id] || {}), [field]: value } }));
  }

  const connected = repos.filter((r) => r.adapter_status === "CONNECTED").length;
  const errored = repos.filter((r) => r.adapter_status === "ERROR").length;

  return (
    <div data-testid="registry-page" className="space-y-6">
      <div>
        <div className="label-cap">Registry · Source Systems</div>
        <h1 className="text-3xl font-semibold text-white mt-1 tracking-tight">
          Écosystème CVLN · <span className="text-violet-400">Integrate. Do not rebuild.</span>
        </h1>
        <p className="text-sm text-white/50 mt-2 max-w-3xl">
          6 dépôts existants recensés depuis GitHub. Meta CVLN OS ne réécrit rien — il
          les découvre, les ping en temps réel et propage le contexte via adapters + 5 contrats.
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Kpi label="Repositories" value={repos.length} tone="violet" testId="reg-total" />
        <Kpi label="Connected" value={connected} tone="green" testId="reg-connected" />
        <Kpi label="Not connected" value={repos.length - connected - errored} testId="reg-nc" />
        <Kpi label="Errors" value={errored} tone="red" testId="reg-err" />
      </div>

      <div className="space-y-3">
        {repos.map((r) => {
          const isOpen = expanded === r.id;
          const draft = drafts[r.id] || {};
          return (
            <div key={r.id} data-testid={`repo-${r.key}`} className="surface-card">
              <button
                onClick={() => setExpanded(isOpen ? null : r.id)}
                className="w-full flex items-center gap-4 p-5 text-left hover:bg-white/[0.02] transition-colors"
              >
                <StatusDot health={r.health} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3">
                    <div className="text-white font-semibold">{r.name}</div>
                    <span className={`px-2 py-0.5 rounded-sm border text-[10px] font-mono uppercase tracking-widest ${STATUS_COLORS[r.adapter_status] || STATUS_COLORS.NOT_CONNECTED}`}>
                      {r.adapter_status}
                    </span>
                  </div>
                  <div className="label-cap mt-1">
                    {r.org}/{r.github_url.split("/").pop()} · {r.layer} · {r.role}
                  </div>
                </div>
                <div className="text-right">
                  {r.last_ping ? (
                    <>
                      <div className="font-mono text-xs text-white/80">
                        {r.last_ping_http ?? "—"} · {r.last_ping_ms ?? "—"}ms
                      </div>
                      <div className="label-cap">
                        {new Date(r.last_ping).toLocaleString("fr-FR")}
                      </div>
                    </>
                  ) : (
                    <div className="label-cap">Jamais pingé</div>
                  )}
                </div>
                <div className="text-white/40 font-mono text-xs">
                  {isOpen ? "▾" : "▸"}
                </div>
              </button>

              {isOpen && (
                <div className="border-t border-[#252633] p-5 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="md:col-span-2">
                      <div className="label-cap mb-1">Description</div>
                      <p className="text-sm text-white/85">{r.description}</p>
                    </div>
                    <div>
                      <div className="label-cap mb-1">GitHub</div>
                      <a
                        href={r.github_url}
                        target="_blank"
                        rel="noreferrer"
                        data-testid={`repo-github-${r.key}`}
                        className="font-mono text-xs text-violet-300 hover:text-violet-200 break-all"
                      >
                        {r.github_url}
                      </a>
                      <div className="label-cap mt-2">branch · {r.branch}</div>
                    </div>
                  </div>

                  {r.tech_stack && (
                    <div>
                      <div className="label-cap mb-2">Stack technique</div>
                      <div className="flex flex-wrap gap-1.5">
                        {r.tech_stack.map((t) => (
                          <span key={t} className="text-[10px] font-mono px-2 py-0.5 rounded-sm border border-[#252633] text-white/70">
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {r.capabilities && (
                    <div>
                      <div className="label-cap mb-2">Capabilities exposées</div>
                      <div className="flex flex-wrap gap-1.5">
                        {r.capabilities.map((c) => (
                          <span key={c} className="text-[10px] font-mono px-2 py-0.5 rounded-sm bg-violet-500/10 border border-violet-500/30 text-violet-200">
                            {c}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {r.adapters_declared && (
                    <div>
                      <div className="label-cap mb-2">Adapters déclarés</div>
                      <div className="flex flex-wrap gap-1.5">
                        {r.adapters_declared.map((a) => (
                          <span key={a} className="text-[10px] font-mono px-2 py-0.5 rounded-sm bg-amber-500/10 border border-amber-500/30 text-amber-300">
                            {a}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {r.open_questions && (
                    <div>
                      <div className="label-cap mb-2 text-amber-400">Questions ouvertes</div>
                      <ul className="text-sm text-white/80 space-y-1">
                        {r.open_questions.map((q, i) => (
                          <li key={i} className="flex gap-2">
                            <span className="text-amber-400">?</span>
                            <span>{q}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 border-t border-[#252633] pt-4">
                    <div>
                      <div className="label-cap mb-1">Preview URL</div>
                      <input
                        data-testid={`repo-url-${r.key}`}
                        value={draft.preview_url ?? r.preview_url ?? ""}
                        onChange={(e) => updateDraft(r.id, "preview_url", e.target.value)}
                        placeholder="https://…preview.emergentagent.com"
                        className="w-full bg-[#0F1017] border border-[#252633] rounded-sm px-3 py-2 text-sm text-white outline-none focus:border-violet-500 font-mono text-xs"
                      />
                    </div>
                    <div>
                      <div className="label-cap mb-1">Auth Type</div>
                      <select
                        data-testid={`repo-auth-${r.key}`}
                        value={draft.auth_type ?? r.auth_type ?? "none"}
                        onChange={(e) => updateDraft(r.id, "auth_type", e.target.value)}
                        className="w-full bg-[#0F1017] border border-[#252633] rounded-sm px-3 py-2 text-sm text-white outline-none focus:border-violet-500 font-mono text-xs"
                      >
                        <option value="none">none</option>
                        <option value="api_key">api_key (X-API-Key)</option>
                        <option value="bearer">bearer (Authorization)</option>
                        <option value="mtls">mtls</option>
                      </select>
                    </div>
                    <div>
                      <div className="label-cap mb-1">API Key / Token</div>
                      <input
                        data-testid={`repo-key-${r.key}`}
                        type="password"
                        value={draft.api_key ?? ""}
                        onChange={(e) => updateDraft(r.id, "api_key", e.target.value)}
                        placeholder="•••••••••"
                        className="w-full bg-[#0F1017] border border-[#252633] rounded-sm px-3 py-2 text-sm text-white outline-none focus:border-violet-500 font-mono text-xs"
                      />
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <button
                      data-testid={`repo-save-${r.key}`}
                      onClick={() => save(r.id)}
                      disabled={busy === r.id}
                      className="btn-primary disabled:opacity-50"
                    >
                      Enregistrer
                    </button>
                    <button
                      data-testid={`repo-ping-${r.key}`}
                      onClick={() => ping(r.id)}
                      disabled={busy === r.id}
                      className="btn-gold disabled:opacity-50"
                    >
                      {busy === r.id ? "…" : "Tester la connexion"}
                    </button>
                    {r.last_ping_error && (
                      <span className="text-xs text-red-400 font-mono self-center">
                        {r.last_ping_error}
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
