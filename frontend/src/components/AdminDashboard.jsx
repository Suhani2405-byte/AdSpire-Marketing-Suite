import React, { useCallback, useEffect, useState } from "react";
import { ShieldCheck, RefreshCw, Users, Settings, Activity, LayoutDashboard, UserPlus, KeyRound, Trash2, Save } from "lucide-react";
import { Bar, Doughnut } from "react-chartjs-2";
import { api, apiError } from "../api";
import { useApp } from "../state/AppState";
import { CHART_COLORS, chartTextColor, gridColor } from "../utils/charts";

const ACTION_LABELS = {
  campaign: "Generated campaign",
  image: "Generated image",
  image_failed: "Image failed",
  login: "Logged in",
  register: "Registered",
  admin: "Admin action",
};

const SECTIONS = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "users", label: "Users", icon: Users },
  { id: "settings", label: "Settings & Features", icon: Settings },
  { id: "activity", label: "Activity Log", icon: Activity },
];

function Kpi({ label, value, sub, color }) {
  return (
    <div className={`kpi-card-box ${color}`}>
      <span className="kpi-label">{label}</span>
      <div className="kpi-number-display">{value ?? "—"}</div>
      {sub && <span className="kpi-subtext">{sub}</span>}
    </div>
  );
}

/* ------------------------------------------------------------ overview -- */
function Overview({ metrics, users }) {
  const t = metrics.totals;
  const platforms = metrics.platform_distribution || {};
  const providers = metrics.image_providers_7d || {};
  return (
    <>
      <div className="kpi-metric-strip">
        <Kpi label="USERS" value={t.users} sub={`${users.filter((u) => u.role === "admin").length} admin(s) • ${users.filter((u) => !u.is_active).length} disabled`} color="purple-border" />
        <Kpi label="CAMPAIGNS" value={t.campaigns} sub={`${t.campaigns_with_images} with images • ${t.template_fallback_campaigns} template fallbacks`} color="green-border" />
        <Kpi label="IMAGES (7 DAYS)" value={t.images_7d}
          sub={t.image_success_rate_7d != null ? `${t.image_success_rate_7d}% success • ${t.image_failures_7d} failed` : "No image requests yet"} color="blue-border" />
        <Kpi label="AVG GENERATION TIME" value={t.avg_campaign_seconds_7d != null ? `${t.avg_campaign_seconds_7d}s` : "—"}
          sub={t.avg_image_seconds_7d != null ? `Images: ${t.avg_image_seconds_7d}s` : "Campaigns, last 7 days"} color="amber-border" />
      </div>

      <div className="admin-chart-grid mt-6">
        <div className="studio-card chart-card">
          <div className="card-top-header"><h3>Last 7 Days</h3></div>
          <div className="chart-box"><Bar
            data={{
              labels: metrics.trend.labels,
              datasets: [
                { label: "Campaigns", data: metrics.trend.campaigns, backgroundColor: CHART_COLORS[0], borderRadius: 4 },
                { label: "Images", data: metrics.trend.images, backgroundColor: CHART_COLORS[1], borderRadius: 4 },
              ],
            }}
            options={{
                  maintainAspectRatio: false,
              plugins: { legend: { labels: { color: chartTextColor } } },
              scales: {
                x: { ticks: { color: chartTextColor }, grid: { color: gridColor } },
                y: { beginAtZero: true, ticks: { color: chartTextColor, precision: 0 }, grid: { color: gridColor } },
              },
            }}
          /></div>
        </div>
        <div className="studio-card chart-card">
          <div className="card-top-header"><h3>Campaigns by Platform</h3></div>
          {Object.keys(platforms).length ? (
            <div className="chart-box"><Doughnut
              data={{ labels: Object.keys(platforms), datasets: [{ data: Object.values(platforms), backgroundColor: CHART_COLORS, borderWidth: 0 }] }}
              options={{ maintainAspectRatio: false, plugins: { legend: { position: "bottom", labels: { color: chartTextColor } } }, cutout: "60%" }}
            /></div>
          ) : <p className="hint-text center">No campaigns yet.</p>}
        </div>
      </div>

      <div className="studio-card mt-6">
        <div className="card-top-header"><h3>System Status</h3></div>
        <ul className="status-list">
          <li><span>Database</span><strong>{metrics.system.database}</strong></li>
          <li><span>Gemini (campaign text)</span><strong>{metrics.system.gemini_configured ? "Configured" : "Missing key"}</strong></li>
          <li><span>Gemini images</span><strong>{metrics.system.image_providers.gemini_image ? "Available" : "No quota"}</strong></li>
          <li><span>Cloudflare FLUX (free)</span><strong>{metrics.system.image_providers.cloudflare ? "Available" : "Not set up"}</strong></li>
          <li><span>Hugging Face FLUX</span><strong>{metrics.system.image_providers.huggingface ? "Available" : "No credits"}</strong></li>
          <li><span>Pollinations</span><strong>{metrics.system.image_providers.pollinations}</strong></li>
          {Object.entries(providers).map(([p, n]) => (
            <li key={p}><span>Images via {p} (7d)</span><strong>{n}</strong></li>
          ))}
        </ul>
      </div>
    </>
  );
}

/* --------------------------------------------------------------- users -- */
function UserManager({ users, reload, notify, me }) {
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "marketer" });
  const [busy, setBusy] = useState(false);
  const [filter, setFilter] = useState("");

  const run = async (fn, okMsg) => {
    try {
      await fn();
      notify(okMsg);
      reload();
    } catch (err) {
      notify(apiError(err, "Action failed."), 6000);
    }
  };

  const createUser = async (e) => {
    e.preventDefault();
    setBusy(true);
    await run(() => api.post("/admin/users", form), `Created ${form.email}`);
    setForm({ name: "", email: "", password: "", role: "marketer" });
    setBusy(false);
  };

  const shown = users.filter((u) => !filter || `${u.name} ${u.email}`.toLowerCase().includes(filter.toLowerCase()));

  return (
    <>
      <form className="studio-card admin-create-user" onSubmit={createUser}>
        <div className="card-top-header"><h3><UserPlus size={16} /> Create account</h3></div>
        <div className="admin-form-row">
          <input className="modern-input" placeholder="Full name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required minLength={2} />
          <input className="modern-input" type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          <input className="modern-input" type="text" placeholder="Password (8+ chars)" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required minLength={8} />
          <select className="modern-select" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
            <option value="marketer">Marketer</option>
            <option value="admin">Admin</option>
          </select>
          <button className="action-btn-glow compact" disabled={busy}>Create</button>
        </div>
      </form>

      <div className="studio-card mt-6">
        <div className="card-top-header admin-users-header">
          <h3>All accounts ({users.length})</h3>
          <input className="modern-input slim" placeholder="Search users..." value={filter} onChange={(e) => setFilter(e.target.value)} />
        </div>
        <div className="table-overflow-wrapper">
          <table className="modern-data-table">
            <thead>
              <tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Campaigns</th><th>Joined</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {shown.map((u) => {
                const self = u.id === me.id;
                return (
                  <tr key={u.id} className={u.is_active ? "" : "row-disabled"}>
                    <td>{u.name}{self && <span className="you-badge">you</span>}</td>
                    <td>{u.email}</td>
                    <td>
                      <select
                        className="modern-select slim"
                        value={u.role}
                        disabled={self}
                        onChange={(e) => run(() => api.patch(`/admin/users/${u.id}`, { role: e.target.value }), `${u.name} is now ${e.target.value}`)}
                      >
                        <option value="marketer">marketer</option>
                        <option value="admin">admin</option>
                      </select>
                    </td>
                    <td>
                      <button
                        className={`status-toggle ${u.is_active ? "on" : "off"}`}
                        disabled={self}
                        onClick={() => run(() => api.patch(`/admin/users/${u.id}`, { is_active: !u.is_active }), `${u.name} ${u.is_active ? "disabled" : "enabled"}`)}
                      >
                        {u.is_active ? "Active" : "Disabled"}
                      </button>
                    </td>
                    <td>{u.campaigns}</td>
                    <td>{u.created_at}</td>
                    <td className="action-cell">
                      <button
                        className="icon-action-btn"
                        title="Reset password"
                        onClick={() => {
                          const pw = window.prompt(`New password for ${u.email} (min 8 characters):`);
                          if (pw) run(() => api.post(`/admin/users/${u.id}/reset-password`, { password: pw }), `Password reset for ${u.name}`);
                        }}
                      >
                        <KeyRound size={14} />
                      </button>
                      <button
                        className="icon-action-btn danger"
                        title="Delete user and their data"
                        disabled={self}
                        onClick={() => {
                          if (window.confirm(`Delete ${u.name} (${u.email}) and ALL their ${u.campaigns} campaigns? This cannot be undone.`)) {
                            run(() => api.delete(`/admin/users/${u.id}`), `Deleted ${u.name}`);
                          }
                        }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}

/* ------------------------------------------------------------ settings -- */
const SWITCHES = [
  ["campaign_generation", "Campaign generation", "Let users generate new campaigns with AI."],
  ["image_generation", "Image generation", "Let users generate AI images (Visual Studio + mockups)."],
  ["budget_planner", "Budget planner", "Show the Budget & ROAS simulator to users."],
  ["registration_open", "Open sign-ups", "Allow new people to create accounts. When off, only admins can add users."],
];

function SettingsPanel({ notify, onSaved }) {
  const [settings, setSettings] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get("/admin/settings").then((r) => setSettings(r.data.settings)).catch((err) => notify(apiError(err)));
  }, [notify]);

  if (!settings) return <p className="hint-text center">Loading settings...</p>;

  const save = async () => {
    setSaving(true);
    try {
      const r = await api.put("/admin/settings", settings);
      setSettings(r.data.settings);
      notify("Settings saved — applied for all users");
      onSaved();
    } catch (err) {
      notify(apiError(err, "Could not save settings."), 6000);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="studio-card">
      <div className="card-top-header"><h3>Feature switches</h3></div>
      <div className="switch-list">
        {SWITCHES.map(([key, label, help]) => (
          <label key={key} className="switch-row">
            <div>
              <strong>{label}</strong>
              <span>{help}</span>
            </div>
            <input type="checkbox" className="switch-input" checked={!!settings[key]} onChange={(e) => setSettings({ ...settings, [key]: e.target.checked })} />
          </label>
        ))}
      </div>
      <p className="hint-text">Admins can always use every feature, even when it's switched off for others.</p>

      <div className="card-top-header mt-6"><h3>Usage limits (per user, per hour)</h3></div>
      <div className="form-two-column">
        <div className="custom-form-group">
          <label>CAMPAIGNS PER HOUR</label>
          <input className="modern-input" type="number" min="1" max="1000" value={settings.campaign_limit_per_hour}
            onChange={(e) => setSettings({ ...settings, campaign_limit_per_hour: e.target.value })} />
        </div>
        <div className="custom-form-group">
          <label>IMAGES PER HOUR</label>
          <input className="modern-input" type="number" min="1" max="1000" value={settings.image_limit_per_hour}
            onChange={(e) => setSettings({ ...settings, image_limit_per_hour: e.target.value })} />
        </div>
      </div>

      <div className="card-top-header mt-6"><h3>Announcement banner</h3></div>
      <div className="custom-form-group">
        <label>MESSAGE SHOWN TO ALL USERS (LEAVE EMPTY TO HIDE)</label>
        <input className="modern-input" maxLength={300} value={settings.announcement}
          placeholder="e.g. Image generation is slow today due to provider limits."
          onChange={(e) => setSettings({ ...settings, announcement: e.target.value })} />
      </div>

      <button className="action-btn-glow mt-4" onClick={save} disabled={saving}>
        {saving ? <RefreshCw size={18} className="spin-animation" /> : <Save size={18} />}
        <span>Save settings</span>
      </button>
    </div>
  );
}

/* ------------------------------------------------------------ activity -- */
function ActivityLog({ logs }) {
  const [type, setType] = useState("all");
  const shown = logs.filter((l) => type === "all" || l.action === type);
  return (
    <div className="studio-card">
      <div className="card-top-header admin-users-header">
        <h3>Recent activity</h3>
        <select className="modern-select slim" value={type} onChange={(e) => setType(e.target.value)}>
          <option value="all">All actions</option>
          {Object.entries(ACTION_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
      </div>
      <div className="table-overflow-wrapper">
        <table className="modern-data-table">
          <thead><tr><th>Time (UTC)</th><th>User</th><th>Action</th><th>Detail</th><th>Engine</th><th>Duration</th></tr></thead>
          <tbody>
            {shown.length === 0 && <tr><td colSpan={6}>No activity.</td></tr>}
            {shown.map((l) => (
              <tr key={l.id}>
                <td>{l.timestamp}</td>
                <td>{l.user}</td>
                <td><span className={l.action === "image_failed" ? "pink-tag" : l.action === "admin" ? "green-tag" : "purple-tag"}>{ACTION_LABELS[l.action] || l.action}</span></td>
                <td className="truncate-cell" title={l.detail}>{l.detail}</td>
                <td>{l.provider || "—"}</td>
                <td>{l.duration_ms ? `${(l.duration_ms / 1000).toFixed(1)}s` : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* --------------------------------------------------------------- shell -- */
export default function AdminDashboard({ onSettingsChanged }) {
  const { user, triggerToast, fetchSavedCampaigns } = useApp();
  const [section, setSection] = useState("overview");
  const [metrics, setMetrics] = useState(null);
  const [logs, setLogs] = useState([]);
  const [users, setUsers] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [m, l, u] = await Promise.all([api.get("/admin/metrics"), api.get("/admin/activity-logs?limit=200"), api.get("/admin/users")]);
      setMetrics(m.data);
      setLogs(l.data.logs || []);
      setUsers(u.data.users || []);
      setError(null);
    } catch (err) {
      setError(apiError(err, "Could not load admin data."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const reloadAll = () => {
    load();
    fetchSavedCampaigns();
  };

  return (
    <div className="library-workspace-container">
      <div className="studio-hero-center">
        <div className="hero-top-badge">
          <ShieldCheck size={14} /> ADMIN PANEL
        </div>
        <h2>Manage Adspire</h2>
        <p>Control users, features and limits, and monitor real platform usage. Manage all campaigns from the Library tab.</p>
      </div>

      <div className="admin-section-tabs">
        {SECTIONS.map(({ id, label, icon: Icon }) => (
          <button key={id} className={`sub-nav-btn ${section === id ? "active" : ""}`} onClick={() => setSection(id)}>
            <Icon size={14} /> {label}
          </button>
        ))}
        <button className="sub-nav-btn" onClick={load} disabled={loading} title="Refresh">
          <RefreshCw size={14} className={loading ? "spin-animation" : ""} /> Refresh
        </button>
      </div>

      {error && <div className="warning-banner">{error}</div>}

      {section === "overview" && metrics && <Overview metrics={metrics} users={users} />}
      {section === "users" && <UserManager users={users} reload={reloadAll} notify={triggerToast} me={user} />}
      {section === "settings" && <SettingsPanel notify={triggerToast} onSaved={() => { load(); onSettingsChanged?.(); }} />}
      {section === "activity" && <ActivityLog logs={logs} />}
    </div>
  );
}
