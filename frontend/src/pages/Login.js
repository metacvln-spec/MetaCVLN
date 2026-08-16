import { useState } from "react";
import { useNavigate, Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { formatApiError } from "../lib/api";

export default function Login() {
  const { user, login } = useAuth();
  const [email, setEmail] = useState("metacvln@gmail.com");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState(null);
  const [busy, setBusy] = useState(false);
  const nav = useNavigate();

  if (user) return <Navigate to="/" replace />;

  async function submit(e) {
    e.preventDefault();
    setErr(null);
    setBusy(true);
    try {
      await login(email, password);
      nav("/");
    } catch (e) {
      setErr(formatApiError(e.response?.data?.detail) || e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen flex bg-[#08090C]" data-testid="login-page">
      {/* Left panel */}
      <div className="hidden md:flex md:w-1/2 relative overflow-hidden border-r border-[#252633] grain-overlay">
        <div className="relative z-10 flex flex-col justify-between p-12 w-full">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-sm bg-gradient-to-br from-violet-500 to-violet-800 flex items-center justify-center">
              <div className="w-4 h-4 rounded-sm bg-[#08090C]" />
            </div>
            <div>
              <div className="font-mono text-[10px] tracking-[0.2em] text-white/60">CVLN</div>
              <div className="font-mono text-xs tracking-[0.2em] text-white font-semibold">
                META CVLN <span className="text-violet-400">OS</span>
              </div>
            </div>
          </div>

          <div className="max-w-md">
            <div className="label-cap mb-4">Internal Operating System</div>
            <h1 className="text-4xl font-semibold text-white leading-tight tracking-tight">
              Automatiser la friction. <br />
              <span className="text-violet-400">Libérer le deep work.</span>
            </h1>
            <p className="mt-6 text-sm text-white/60 leading-relaxed">
              META CVLN OS orchestre le travail interne du groupe. Chaque donnée devient contexte,
              chaque contexte une préparation, chaque préparation une décision humaine tracée.
            </p>
            <div className="mt-8 grid grid-cols-3 gap-4">
              {["18 entités", "12 agents", "5 contrats"].map((t, i) => (
                <div key={i} className="border border-[#252633] p-3 rounded-sm">
                  <div className="label-cap">Layer {i + 1}</div>
                  <div className="font-mono text-sm text-white mt-1">{t}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="label-cap text-white/30">
            FREKCORE identity · authority_scope · least privilege · auditable
          </div>
        </div>
      </div>

      {/* Right form */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <form onSubmit={submit} className="w-full max-w-sm">
          <div className="label-cap mb-3">Accès Interne</div>
          <h2 className="text-2xl font-semibold text-white mb-8 tracking-tight">
            Authentifier votre identité
          </h2>

          <label className="label-cap block mb-2">Email</label>
          <input
            data-testid="login-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full bg-[#13141C] border border-[#252633] rounded-sm px-3 py-2.5 text-sm text-white outline-none focus:border-violet-500 mb-4"
          />

          <label className="label-cap block mb-2">Mot de passe</label>
          <input
            data-testid="login-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full bg-[#13141C] border border-[#252633] rounded-sm px-3 py-2.5 text-sm text-white outline-none focus:border-violet-500 mb-2"
          />

          {err && (
            <div
              data-testid="login-error"
              className="mt-3 text-xs text-red-400 border border-red-500/30 bg-red-500/10 px-3 py-2 rounded-sm"
            >
              {err}
            </div>
          )}

          <button
            data-testid="login-submit"
            type="submit"
            disabled={busy}
            className="btn-gold w-full mt-6 disabled:opacity-50"
          >
            {busy ? "Vérification..." : "Entrer dans le OS"}
          </button>

          <div className="mt-8 pt-6 border-t border-[#252633] label-cap text-white/40">
            FREKCORE Identity · trace_id activé · signed session
          </div>
        </form>
      </div>
    </div>
  );
}
