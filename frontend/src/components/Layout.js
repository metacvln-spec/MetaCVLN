import { NavLink, useNavigate, Outlet } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Toaster } from "sonner";

const NAV = [
  { to: "/", label: "Command Center", scope: "command_center" },
  { to: "/workbench", label: "My Workbench", scope: "workbench" },
  { to: "/people", label: "People OS", scope: "people_os" },
  { to: "/finance", label: "Finance OS", scope: "finance_os" },
  { to: "/legal", label: "Legal OS", scope: "legal_os" },
  { to: "/ops", label: "Operations OS", scope: "ops_os" },
  { to: "/knowledge", label: "Knowledge OS", scope: "knowledge_os" },
  { to: "/ecosystem", label: "Work Graph", scope: "work_graph" },
  { to: "/registry", label: "Registry", scope: "registry" },
  { to: "/agents", label: "Agent Factory", scope: "agent_factory" },
  { to: "/decisions", label: "Decision System", scope: "decisions" },
  { to: "/evidence", label: "Evidence & Audit", scope: "evidence" },
  { to: "/notarizations", label: "Notary Ledger", scope: "notarizations" },
  { to: "/weekly-report", label: "Weekly Report", scope: "weekly_report" },
  { to: "/brain", label: "CVL Brain", scope: "brain" },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const nav = useNavigate();

  async function handleLogout() {
    await logout();
    nav("/login");
  }

  return (
    <div className="min-h-screen flex bg-[#08090C]">
      <Toaster theme="dark" position="top-right" richColors />

      {/* Sidebar */}
      <aside
        data-testid="app-sidebar"
        className="w-64 shrink-0 border-r border-[#252633] bg-[#0A0B10] flex flex-col"
      >
        <div className="px-5 py-5 border-b border-[#252633]">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-sm bg-gradient-to-br from-violet-500 to-violet-800 flex items-center justify-center">
              <div className="w-3 h-3 rounded-sm bg-[#08090C]" />
            </div>
            <div>
              <div className="font-mono text-[10px] tracking-[0.2em] text-white/60">CVLN</div>
              <div className="font-mono text-[10px] tracking-[0.2em] text-white font-semibold">
                META · CVLN <span className="text-violet-400">OS</span>
              </div>
            </div>
          </div>
        </div>

        <nav className="flex-1 py-4 overflow-y-auto scroll-thin">
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.to === "/"}
              data-testid={`nav-${n.scope}`}
              className={({ isActive }) => `sidebar-item ${isActive ? "active" : ""}`}
            >
              <span className="w-1 h-1 rounded-full bg-current opacity-60" />
              {n.label}
            </NavLink>
          ))}
        </nav>

        <div className="px-4 py-4 border-t border-[#252633]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-amber-500 flex items-center justify-center text-[10px] font-mono font-semibold uppercase">
              {(user?.name || user?.email || "?").slice(0, 2)}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs text-white truncate">{user?.name || user?.email}</div>
              <div className="text-[10px] font-mono uppercase tracking-widest text-white/40">
                {user?.role}
              </div>
            </div>
          </div>
          <button
            data-testid="logout-btn"
            onClick={handleLogout}
            className="btn-ghost w-full mt-3 text-[10px]"
          >
            Se déconnecter
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col min-w-0">
        <div className="border-b border-[#252633] bg-[#0A0B10]/60 backdrop-blur px-8 py-3 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="label-cap">Meta CVLN OS · Internal</div>
            <div className="flex items-center gap-2">
              <span className="dot-status dot-green" />
              <span className="label-cap">System Nominal</span>
            </div>
          </div>
          <div className="flex items-center gap-6 label-cap">
            <span>{new Date().toLocaleString("fr-FR", { dateStyle: "medium", timeStyle: "short" })}</span>
            <span className="text-white/40">v1.0 · Doctrine · Architecture · Systems · Ops</span>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto scroll-thin p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
