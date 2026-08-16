import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import CommandCenter from "./pages/CommandCenter";
import Workbench from "./pages/Workbench";
import PeopleOS from "./pages/PeopleOS";
import FinanceOS from "./pages/FinanceOS";
import LegalOS from "./pages/LegalOS";
import OpsOS from "./pages/OpsOS";
import KnowledgeOS from "./pages/KnowledgeOS";
import Ecosystem from "./pages/Ecosystem";
import AgentFactory from "./pages/AgentFactory";
import DecisionSystem from "./pages/DecisionSystem";
import EvidenceAudit from "./pages/EvidenceAudit";
import CVLBrain from "./pages/CVLBrain";
import "./App.css";

function Gate({ children }) {
  const { user } = useAuth();
  if (user === undefined) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#08090C]">
        <div className="label-cap text-white/50">Chargement OS…</div>
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            element={
              <Gate>
                <Layout />
              </Gate>
            }
          >
            <Route path="/" element={<CommandCenter />} />
            <Route path="/workbench" element={<Workbench />} />
            <Route path="/people" element={<PeopleOS />} />
            <Route path="/finance" element={<FinanceOS />} />
            <Route path="/legal" element={<LegalOS />} />
            <Route path="/ops" element={<OpsOS />} />
            <Route path="/knowledge" element={<KnowledgeOS />} />
            <Route path="/ecosystem" element={<Ecosystem />} />
            <Route path="/agents" element={<AgentFactory />} />
            <Route path="/decisions" element={<DecisionSystem />} />
            <Route path="/evidence" element={<EvidenceAudit />} />
            <Route path="/brain" element={<CVLBrain />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
