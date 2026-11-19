import React from "react";
import { Sliders, Sparkles, ArrowRight, RefreshCw, BookmarkPlus, Trash2, X } from "lucide-react";
import { useApp } from "../state/AppState";
import CampaignOutput from "./CampaignOutput";

const PLATFORMS = ["Instagram", "TikTok / Reels", "LinkedIn", "Google Search Ads", "Facebook Ads", "Twitter / X", "Omnichannel Suite"];
const GOALS = ["Sales & Conversions", "Lead Generation", "Brand Awareness", "Product Launch", "Viral Engagement"];
const INDUSTRIES = ["Consumer Electronics & D2C", "E-commerce & D2C", "SaaS & B2B Technology", "Fashion & Apparel", "Health & Wellness", "Fintech & Financial", "Food & Beverage", "Education"];
const TONES = ["Bold & Premium", "Professional & Authoritative", "High Energy & Dynamic", "Minimalist & Luxury", "Witty & Engaging", "Warm & Friendly"];

function Select({ label, value, options, onChange }) {
  return (
    <div className="custom-form-group">
      <label>{label}</label>
      <select value={value} onChange={(e) => onChange(e.target.value)} className="modern-select">
        {!options.includes(value) && <option>{value}</option>}
        {options.map((o) => (
          <option key={o}>{o}</option>
        ))}
      </select>
    </div>
  );
}

export function StudioHero() {
  return (
    <section className="modern-hero-section">
      <div className="hero-top-badge">
        <Sparkles size={14} /> AI MULTI-CHANNEL CAMPAIGN GENERATOR
      </div>
      <h1 className="hero-main-heading">
        Transform Ideas Into <span>High-Yield Campaigns</span>
      </h1>
      <p className="hero-lead-text">
        Generate complete marketing campaigns: audience persona, ad copy with A/B variants, social posts,
        video scripts, email, a 7-day calendar, AI product visuals and a budget simulation.
      </p>
    </section>
  );
}

export default function CampaignStudio() {
  const { form, setField, loading, handleGenerateCampaign, cancelGeneration, brands, applyBrand, saveBrandFromForm, deleteBrand } = useApp();

  return (
    <div className="campaign-studio-grid">
      <div className="studio-card config-card">
        <div className="card-top-header">
          <div className="header-title-flex">
            <Sliders size={18} className="text-purple-400" />
            <h2>Campaign Parameters</h2>
          </div>
          <span className="step-badge">STEP 01</span>
        </div>

        {/* Brand profiles */}
        <div className="custom-form-group">
          <label>BRAND PROFILE</label>
          <div className="brand-row">
            <select
              className="modern-select"
              value=""
              onChange={(e) => {
                const b = brands.find((x) => String(x.id) === e.target.value);
                if (b) applyBrand(b);
              }}
            >
              <option value="">{brands.length ? "Load a saved brand…" : "No saved brands yet"}</option>
              {brands.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
            <button type="button" className="icon-action-btn" title="Save current inputs as a brand profile" onClick={saveBrandFromForm}>
              <BookmarkPlus size={16} />
            </button>
          </div>
          {brands.length > 0 && (
            <div className="brand-chip-row">
              {brands.map((b) => (
                <span key={b.id} className="brand-chip">
                  <button type="button" onClick={() => applyBrand(b)}>{b.name}</button>
                  <button type="button" title="Delete brand" onClick={() => window.confirm(`Delete brand "${b.name}"?`) && deleteBrand(b.id)}>
                    <Trash2 size={11} />
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="custom-form-group">
          <label>PRODUCT / BRAND NAME</label>
          <input
            type="text"
            value={form.productName}
            maxLength={200}
            onChange={(e) => setField("productName", e.target.value)}
            placeholder="e.g. AeroPulse Pro Wireless"
            className="modern-input"
          />
        </div>

        <div className="custom-form-group">
          <label>VALUE PROPOSITION & PRODUCT DETAILS</label>
          <textarea
            rows={4}
            value={form.description}
            maxLength={3000}
            onChange={(e) => setField("description", e.target.value)}
            placeholder="Key features, technological advantages, and customer benefits..."
            className="modern-textarea"
          />
        </div>

        <div className="custom-form-group">
          <label>TARGET AUDIENCE</label>
          <input
            type="text"
            value={form.audience}
            maxLength={300}
            onChange={(e) => setField("audience", e.target.value)}
            placeholder="e.g. Tech professionals, commuters, creators 20-38"
            className="modern-input"
          />
        </div>

        <div className="form-two-column">
          <Select label="PRIMARY PLATFORM" value={form.platform} options={PLATFORMS} onChange={(v) => setField("platform", v)} />
          <Select label="CAMPAIGN GOAL" value={form.goal} options={GOALS} onChange={(v) => setField("goal", v)} />
        </div>
        <div className="form-two-column">
          <Select label="INDUSTRY / VERTICAL" value={form.industry} options={INDUSTRIES} onChange={(v) => setField("industry", v)} />
          <Select label="BRAND TONE" value={form.tone} options={TONES} onChange={(v) => setField("tone", v)} />
        </div>

        {loading ? (
          <div className="generate-row">
            <button className="action-btn-glow" disabled>
              <RefreshCw size={18} className="spin-animation" />
              <span>Generating Campaign...</span>
            </button>
            <button type="button" className="icon-action-btn cancel-btn" title="Cancel" onClick={cancelGeneration}>
              <X size={16} />
            </button>
          </div>
        ) : (
          <button className="action-btn-glow" onClick={handleGenerateCampaign}>
            <Sparkles size={18} />
            <span>Generate Full Campaign Suite</span>
            <ArrowRight size={16} />
          </button>
        )}
      </div>

      <CampaignOutput />
    </div>
  );
}
