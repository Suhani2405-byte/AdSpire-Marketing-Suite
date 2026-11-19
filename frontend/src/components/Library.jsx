import React, { useMemo, useState } from "react";
import { FolderArchive, Layers, Trash2, Search, Image as ImageIcon } from "lucide-react";
import { useApp } from "../state/AppState";

export default function Library() {
  const { user, savedCampaigns, openSavedCampaign, deleteCampaign, setActiveTab } = useApp();
  const isAdmin = user.role === "admin";
  const [query, setQuery] = useState("");
  const [owner, setOwner] = useState("all");

  const owners = useMemo(
    () => [...new Set(savedCampaigns.map((c) => c.owner_name).filter(Boolean))].sort(),
    [savedCampaigns]
  );

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return savedCampaigns.filter(
      (c) =>
        (owner === "all" || c.owner_name === owner) &&
        (!q ||
          [c.product_name, c.target_audience, c.platform, c.goal, c.owner_name, c.campaign_content?.campaign_title]
            .some((v) => String(v || "").toLowerCase().includes(q)))
    );
  }, [savedCampaigns, query, owner]);

  return (
    <div className="library-workspace-container">
      <div className="studio-hero-center">
        <div className="hero-top-badge">
          <FolderArchive size={14} /> YOUR CAMPAIGN LIBRARY
        </div>
        <h2>{isAdmin ? "All Campaigns (Admin View)" : "Saved Marketing Campaigns"}</h2>
        <p>
          {isAdmin
            ? `Every campaign from all ${owners.length} users. Showing ${filtered.length} of ${savedCampaigns.length}.`
            : "Every campaign you generate is saved here with its image. Click one to reopen it."}
        </p>
      </div>

      {savedCampaigns.length > 0 && (
        <div className="library-toolbar">
          <div className="library-search">
            <Search size={16} />
            <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search by product, platform, goal, user..." />
          </div>
          {isAdmin && (
            <select className="modern-select owner-filter" value={owner} onChange={(e) => setOwner(e.target.value)}>
              <option value="all">All users ({savedCampaigns.length})</option>
              {owners.map((o) => (
                <option key={o} value={o}>
                  {o} ({savedCampaigns.filter((c) => c.owner_name === o).length})
                </option>
              ))}
            </select>
          )}
        </div>
      )}

      {savedCampaigns.length === 0 ? (
        <div className="studio-card empty-workspace-state p-12">
          <div className="empty-visual-circle">
            <Layers size={36} className="text-purple-400" />
          </div>
          <h3>No Campaigns Saved Yet</h3>
          <p>Generate your first marketing campaign to start your library.</p>
          <button className="action-btn-glow" onClick={() => setActiveTab("studio")}>
            🚀 Open Campaign Studio
          </button>
        </div>
      ) : filtered.length === 0 ? (
        <p className="hint-text center">No campaigns match "{query}".</p>
      ) : (
        <div className="library-cards-grid">
          {filtered.map((item) => (
            <div key={item.id} className="library-item-card" onClick={() => openSavedCampaign(item)}>
              {item.image_thumb ? (
                <img className="library-thumb" src={item.image_thumb} alt={item.product_name} loading="lazy" />
              ) : (
                <div className="library-thumb placeholder"><ImageIcon size={22} /></div>
              )}
              <div className="item-card-top">
                <span className="purple-tag">{item.platform}</span>
                <span className="item-date">{item.created_at || "Recent"}</span>
              </div>
              <h3 className="item-title">{item.product_name}</h3>
              {item.campaign_content?.campaign_title && <p className="item-sub"><em>{item.campaign_content.campaign_title}</em></p>}
              <p className="item-sub"><strong>Goal:</strong> {item.goal}</p>
              {isAdmin && <p className="item-sub"><strong>By:</strong> {item.owner_name}</p>}
              <div className="item-card-footer">
                <span className="item-open-hint">{item.source === "template" ? "Template • " : ""}Open in Studio →</span>
                <button
                  className="delete-icon-btn"
                  title="Delete campaign"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (window.confirm(`Delete "${item.product_name}"?`)) deleteCampaign(item.id);
                  }}
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
