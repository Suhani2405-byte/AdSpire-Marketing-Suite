import React, { useCallback, useEffect, useState } from "react";
import { Sparkles, DollarSign, Image as ImageIcon, FolderArchive, Flame, ShieldCheck, LogOut, RefreshCw, Megaphone, Ban } from "lucide-react";
import "./App.css";
import { api, getToken, setToken, setUnauthorizedHandler } from "./api";
import { AppStateProvider, useApp } from "./state/AppState";
import LoginPage from "./components/LoginPage";
import CampaignStudio, { StudioHero } from "./components/CampaignStudio";
import VisualStudio from "./components/VisualStudio";
import BudgetPlanner from "./components/BudgetPlanner";
import Library from "./components/Library";
import AdminDashboard from "./components/AdminDashboard";

function Disabled({ name }) {
  return (
    <div className="studio-card empty-workspace-state p-12">
      <div className="empty-visual-circle">
        <Ban size={36} className="text-purple-400" />
      </div>
      <h3>{name} is turned off</h3>
      <p>The administrator has temporarily disabled this feature.</p>
    </div>
  );
}

function Shell({ onLogout, reloadSettings }) {
  const { user, settings, canUse, activeTab, setActiveTab, toast, savedCampaigns, fetchSavedCampaigns } = useApp();
  const isAdmin = user.role === "admin";

  const tabs = [
    { id: "studio", label: "Campaign Studio", icon: Sparkles },
    { id: "visuals", label: "Visual Studio", icon: ImageIcon, hidden: !canUse("image_generation") },
    { id: "budget", label: "Budget Planner", icon: DollarSign, hidden: !canUse("budget_planner") },
    { id: "library", label: isAdmin ? "All Campaigns" : "Library", icon: FolderArchive, count: savedCampaigns.length },
    { id: "admin", label: "Admin Panel", icon: ShieldCheck, hidden: !isAdmin },
  ].filter((t) => !t.hidden);

  return (
    <div className="app-shell">
      {toast && (
        <div className="toast-pill" role="status">
          <Sparkles size={16} />
          <span>{toast}</span>
        </div>
      )}

      {settings?.announcement && (
        <div className="announcement-bar">
          <Megaphone size={15} />
          <span>{settings.announcement}</span>
        </div>
      )}

      <header className="main-navbar">
        <div className="nav-brand-group">
          <div className="brand-icon-box">
            <Flame size={22} className="text-purple-400" />
          </div>
          <div>
            <div className="brand-main-title">
              Ad<span>spire</span>
            </div>
            <div className="brand-sub-title">AI Marketing Campaign Suite</div>
          </div>
        </div>

        <nav className="desktop-nav-tabs">
          {tabs.map(({ id, label, icon: Icon, count }) => (
            <button
              key={id}
              className={`nav-pill-btn ${activeTab === id ? "active" : ""}`}
              onClick={() => {
                setActiveTab(id);
                if (id === "library") fetchSavedCampaigns();
              }}
            >
              <Icon size={15} />
              <span>{label}</span>
              {count > 0 && <span className="library-counter">{count}</span>}
            </button>
          ))}
        </nav>

        <div className="user-menu">
          <div className="user-avatar" title={`${user.name} (${user.email})`}>{user.avatar}</div>
          <div className="user-meta">
            <strong>{user.name}</strong>
            <span>{user.role}</span>
          </div>
          <button className="icon-action-btn" title="Log out" onClick={onLogout}>
            <LogOut size={15} />
          </button>
        </div>
      </header>

      {activeTab === "studio" && <StudioHero />}

      <main className="main-content-layout">
        {activeTab === "studio" && (canUse("campaign_generation") ? <CampaignStudio /> : <Disabled name="Campaign generation" />)}
        {activeTab === "visuals" && (canUse("image_generation") ? <VisualStudio /> : <Disabled name="Image generation" />)}
        {activeTab === "budget" && (canUse("budget_planner") ? <BudgetPlanner /> : <Disabled name="The budget planner" />)}
        {activeTab === "library" && <Library />}
        {activeTab === "admin" && isAdmin && <AdminDashboard onSettingsChanged={reloadSettings} />}
      </main>

      <footer className="main-footer">
        <div className="footer-inner-content">
          <div className="brand-main-title">
            Ad<span>spire</span>
          </div>
          <p>AI Marketing Campaign Generator</p>
          <div className="tech-badge-tags">
            <span>React 19</span> • <span>Flask</span> • <span>Google Gemini</span> • <span>FLUX image models</span> • <span>SQLAlchemy</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [settings, setSettings] = useState(null);
  const [checking, setChecking] = useState(() => Boolean(getToken()));

  const logout = () => {
    setToken(null);
    setUser(null);
  };

  const loadSettings = useCallback(() => {
    api
      .get("/settings/public")
      .then((r) => setSettings(r.data.settings))
      .catch(() => setSettings(null));
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(logout);
    loadSettings();
    if (!getToken()) return;
    api
      .get("/auth/me")
      .then((res) => setUser(res.data.user))
      .catch(() => setToken(null))
      .finally(() => setChecking(false));
  }, [loadSettings]);

  if (checking) {
    return (
      <div className="auth-screen">
        <RefreshCw size={28} className="spin-animation text-purple-400" />
      </div>
    );
  }

  if (!user) return <LoginPage onLoggedIn={setUser} registrationOpen={settings?.registration_open !== false} />;

  return (
    <AppStateProvider key={user.id} user={user} settings={settings}>
      <Shell onLogout={logout} reloadSettings={loadSettings} />
    </AppStateProvider>
  );
}
