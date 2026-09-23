import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Sparkles,
  Layers,
  DollarSign,
  BarChart3,
  Image as ImageIcon,
  Copy,
  Check,
  Download,
  Trash2,
  ExternalLink,
  RefreshCw,
  Send,
  Calendar,
  Users,
  Target,
  ArrowRight,
  TrendingUp,
  Zap,
  Eye,
  Sliders,
  CheckCircle2,
  FolderArchive,
  Play,
  Heart,
  MessageCircle,
  Share2,
  Bookmark,
  Volume2,
  ChevronRight,
  ShieldCheck,
  Globe,
  SlidersHorizontal,
  Flame,
  Award
} from "lucide-react";
import "./App.css";

const API_BASE = "http://127.0.0.1:5000/api";

export default function App() {
  // Navigation State: 'overview' | 'studio' | 'visuals' | 'budget' | 'library'
  const [activeTab, setActiveTab] = useState("studio");

  // Output Sub-Tabs
  const [outputTab, setOutputTab] = useState("strategy"); // 'strategy' | 'ads' | 'socials' | 'email' | 'calendar' | 'mockup'
  const [mockupType, setMockupType] = useState("instagram"); // 'instagram' | 'tiktok' | 'linkedin' | 'google'

  // Interactive Mockup States
  const [isLiked, setIsLiked] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [isPlayingVideo, setIsPlayingVideo] = useState(true);

  // Form Parameters
  const [productName, setProductName] = useState("AeroPulse Pro Wireless");
  const [description, setDescription] = useState(
    "Next-generation spatial audio wireless earbuds with 40-hour battery life, titanium build, and active environmental noise cancellation."
  );
  const [audience, setAudience] = useState("Tech professionals, commuters, and fitness enthusiasts aged 20-38");
  const [platform, setPlatform] = useState("Instagram");
  const [goal, setGoal] = useState("Sales & Conversions");
  const [industry, setIndustry] = useState("Consumer Electronics & D2C");
  const [tone, setTone] = useState("Bold & Premium");

  // Generator State
  const [loading, setLoading] = useState(false);
  const [campaignResult, setCampaignResult] = useState(null);
  const [copiedKey, setCopiedKey] = useState(null);
  const [toast, setToast] = useState(null);

  // Visual Studio State
  const [visualPrompt, setVisualPrompt] = useState(
    "Editorial commercial photography of sleek matte-black titanium earbuds floating over black marble with neon cyber blue rim lighting, 8k resolution"
  );
  const [visualStyle, setVisualStyle] = useState("Photorealistic");
  const [aspectRatio, setAspectRatio] = useState("1:1");
  const [generatingVisual, setGeneratingVisual] = useState(false);
  const [renderedVisual, setRenderedVisual] = useState(null);

  // Budget Planner State
  const [budgetAmount, setBudgetAmount] = useState(3500);
  const [budgetDuration, setBudgetDuration] = useState(30);
  const [budgetGoal, setBudgetGoal] = useState("Sales");
  const [budgetPlan, setBudgetPlan] = useState(null);

  // Saved Library State
  const [savedCampaigns, setSavedCampaigns] = useState([]);

  // Toast Trigger
  const triggerToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  // Initial Data Fetch
  useEffect(() => {
    fetchBudgetCalculations(budgetAmount, budgetGoal, budgetDuration);
    fetchSavedCampaigns();
  }, []);

  // -----------------------------
  // API CALLS
  // -----------------------------
  const handleGenerateCampaign = async () => {
    if (!productName.trim() || !description.trim()) {
      triggerToast("Please provide product name and description!");
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/campaigns/generate`, {
        product_name: productName,
        description: description,
        target_audience: audience,
        platform: platform,
        goal: goal,
        tone: tone,
        industry: industry,
      });

      if (res.data && res.data.campaign_content) {
        setCampaignResult(res.data.campaign_content);
        if (res.data.campaign_content.image_prompt) {
          setVisualPrompt(res.data.campaign_content.image_prompt);
        }
        triggerToast("✨ Campaign Strategy & Creative Assets Ready!");
        fetchSavedCampaigns();
        // Smooth scroll to output on mobile
        if (window.innerWidth < 1024) {
          const outEl = document.getElementById("campaign-output-pane");
          if (outEl) outEl.scrollIntoView({ behavior: "smooth" });
        }
      }
    } catch (err) {
      console.error(err);
      triggerToast("Generation failed. Check server connection.");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateVisual = async () => {
    if (!visualPrompt.trim()) {
      triggerToast("Please enter a visual description.");
      return;
    }

    setGeneratingVisual(true);
    try {
      const res = await axios.post(`${API_BASE}/image/generate`, {
        prompt: visualPrompt,
        aspect_ratio: aspectRatio,
        style: visualStyle,
      });

      if (res.data && res.data.image_url) {
        setRenderedVisual(res.data.image_url);
        triggerToast("🎨 High-Resolution Creative Asset Synthesized!");
      } else {
        triggerToast("Creative rendering issue. Please retry.");
      }
    } catch (err) {
      console.error(err);
      triggerToast("Error synthesizing creative visual.");
    } finally {
      setGeneratingVisual(false);
    }
  };

  const fetchBudgetCalculations = async (amount, g, dur) => {
    try {
      const res = await axios.post(`${API_BASE}/budget/plan`, {
        total_budget: amount,
        goal: g,
        industry: "Consumer Electronics & D2C",
        duration_days: dur,
      });
      if (res.data && res.data.success) {
        setBudgetPlan(res.data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchSavedCampaigns = async () => {
    try {
      const res = await axios.get(`${API_BASE}/campaigns`);
      if (res.data && res.data.campaigns) {
        setSavedCampaigns(res.data.campaigns);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteCampaign = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this campaign?")) return;
    try {
      await axios.delete(`${API_BASE}/campaigns/${id}`);
      triggerToast("Campaign removed from library.");
      fetchSavedCampaigns();
    } catch (err) {
      console.error(err);
      triggerToast("Could not delete campaign.");
    }
  };

  const copyText = (content, key) => {
    navigator.clipboard.writeText(typeof content === "object" ? JSON.stringify(content, null, 2) : content);
    setCopiedKey(key);
    triggerToast("Copied to clipboard!");
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const downloadBriefJSON = () => {
    if (!campaignResult) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(campaignResult, null, 2));
    const a = document.createElement("a");
    a.setAttribute("href", dataStr);
    a.setAttribute("download", `${productName.toLowerCase().replace(/\s+/g, "_")}_campaign_brief.json`);
    document.body.appendChild(a);
    a.click();
    a.remove();
    triggerToast("Campaign brief downloaded!");
  };

  return (
    <div className="app-shell">
      {/* Toast Notification */}
      {toast && (
        <div className="toast-pill">
          <Sparkles size={16} />
          <span>{toast}</span>
        </div>
      )}

      {/* ========================================================
          TOP MODERN HEADER / NAVBAR
      ======================================================== */}
      <header className="main-navbar">
        <div className="nav-brand-group">
          <div className="brand-icon-box">
            <Flame size={22} className="text-purple-400" />
          </div>
          <div>
            <div className="brand-main-title">
              Ad<span>spire</span>
            </div>
            <div className="brand-sub-title">Autonomous Growth & Marketing Suite</div>
          </div>
        </div>

        <nav className="desktop-nav-tabs">
          <button
            className={`nav-pill-btn ${activeTab === "studio" ? "active" : ""}`}
            onClick={() => setActiveTab("studio")}
          >
            <Sparkles size={15} />
            <span>Campaign Studio</span>
          </button>

          <button
            className={`nav-pill-btn ${activeTab === "visuals" ? "active" : ""}`}
            onClick={() => setActiveTab("visuals")}
          >
            <ImageIcon size={15} />
            <span>Creative Visual Studio</span>
          </button>

          <button
            className={`nav-pill-btn ${activeTab === "budget" ? "active" : ""}`}
            onClick={() => setActiveTab("budget")}
          >
            <DollarSign size={15} />
            <span>Budget & ROAS Planner</span>
          </button>

          <button
            className={`nav-pill-btn ${activeTab === "library" ? "active" : ""}`}
            onClick={() => {
              setActiveTab("library");
              fetchSavedCampaigns();
            }}
          >
            <FolderArchive size={15} />
            <span>Campaign Library</span>
            {savedCampaigns.length > 0 && (
              <span className="library-counter">{savedCampaigns.length}</span>
            )}
          </button>
        </nav>

        <div className="engine-badge-status">
          <span className="active-glow-dot"></span>
          <span>Engine Online • v3.8</span>
        </div>
      </header>

      {/* ========================================================
          HERO BANNER
      ======================================================== */}
      {activeTab === "studio" && (
        <section className="modern-hero-section">
          <div className="hero-top-badge">
            <Zap size={14} /> AUTONOMOUS MULTI-CHANNEL CAMPAIGN ARCHITECTURE
          </div>
          <h1 className="hero-main-heading">
            Transform Ideas Into <span>High-Yield Campaigns</span>
          </h1>
          <p className="hero-lead-text">
            Orchestrate complete multi-channel marketing campaigns: audience psychology, high-converting ad copy,
            viral video scripts, generative imagery, and predictive ROI modeling.
          </p>

          <div className="hero-metrics-bar">
            <div className="metric-chip">
              <span className="chip-number">10x</span>
              <span className="chip-label">Faster Go-to-Market</span>
            </div>
            <div className="metric-separator"></div>
            <div className="metric-chip">
              <span className="chip-number">6+</span>
              <span className="chip-label">Omnichannel Formats</span>
            </div>
            <div className="metric-separator"></div>
            <div className="metric-chip">
              <span className="chip-number">8K</span>
              <span className="chip-label">Visual Synthesis</span>
            </div>
            <div className="metric-separator"></div>
            <div className="metric-chip">
              <span className="chip-number">4.2x</span>
              <span className="chip-label">Benchmark ROAS</span>
            </div>
          </div>
        </section>
      )}

      {/* ========================================================
          MAIN WORKSPACE CONTENT
      ======================================================== */}
      <main className="main-content-layout">
        {/* ======================================================
            TAB 1: CAMPAIGN STUDIO
        ====================================================== */}
        {activeTab === "studio" && (
          <div className="campaign-studio-grid">
            {/* Left: Input Form Card */}
            <div className="studio-card config-card">
              <div className="card-top-header">
                <div className="header-title-flex">
                  <Sliders size={18} className="text-purple-400" />
                  <h2>Campaign Parameters</h2>
                </div>
                <span className="step-badge">STEP 01</span>
              </div>

              <div className="custom-form-group">
                <label>PRODUCT / BRAND NAME</label>
                <input
                  type="text"
                  value={productName}
                  onChange={(e) => setProductName(e.target.value)}
                  placeholder="e.g. AeroPulse Pro Wireless"
                  className="modern-input"
                />
              </div>

              <div className="custom-form-group">
                <label>VALUE PROPOSITION & PRODUCT DETAILS</label>
                <textarea
                  rows={4}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Key features, technological advantages, and customer benefits..."
                  className="modern-textarea"
                />
              </div>

              <div className="custom-form-group">
                <label>TARGET AUDIENCE PSYCHOGRAPHIC</label>
                <input
                  type="text"
                  value={audience}
                  onChange={(e) => setAudience(e.target.value)}
                  placeholder="e.g. Tech professionals, commuters, creators 20-38"
                  className="modern-input"
                />
              </div>

              <div className="form-two-column">
                <div className="custom-form-group">
                  <label>PRIMARY PLATFORM</label>
                  <select
                    value={platform}
                    onChange={(e) => setPlatform(e.target.value)}
                    className="modern-select"
                  >
                    <option>Instagram</option>
                    <option>TikTok / Reels</option>
                    <option>LinkedIn</option>
                    <option>Google Search Ads</option>
                    <option>Facebook Ads</option>
                    <option>Twitter / X</option>
                    <option>Omnichannel Suite</option>
                  </select>
                </div>

                <div className="custom-form-group">
                  <label>CAMPAIGN GOAL</label>
                  <select
                    value={goal}
                    onChange={(e) => setGoal(e.target.value)}
                    className="modern-select"
                  >
                    <option>Sales & Conversions</option>
                    <option>Lead Generation</option>
                    <option>Brand Awareness</option>
                    <option>Product Launch</option>
                    <option>Viral Engagement</option>
                  </select>
                </div>
              </div>

              <div className="form-two-column">
                <div className="custom-form-group">
                  <label>INDUSTRY / VERTICAL</label>
                  <select
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    className="modern-select"
                  >
                    <option>Consumer Electronics & D2C</option>
                    <option>SaaS & B2B Technology</option>
                    <option>Fashion & Apparel</option>
                    <option>Health & Wellness</option>
                    <option>Fintech & Financial</option>
                  </select>
                </div>

                <div className="custom-form-group">
                  <label>BRAND TONE</label>
                  <select
                    value={tone}
                    onChange={(e) => setTone(e.target.value)}
                    className="modern-select"
                  >
                    <option>Bold & Premium</option>
                    <option>Professional & Authoritative</option>
                    <option>High Energy & Dynamic</option>
                    <option>Minimalist & Luxury</option>
                    <option>Witty & Engaging</option>
                  </select>
                </div>
              </div>

              <button
                className="action-btn-glow"
                onClick={handleGenerateCampaign}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <RefreshCw size={18} className="spin-animation" />
                    <span>Synthesizing Campaign Strategy...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={18} />
                    <span>Generate Full Campaign Suite</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </div>

            {/* Right: Output Workspace */}
            <div id="campaign-output-pane" className="studio-card output-card">
              <div className="output-top-bar">
                <div className="output-nav-tabs">
                  <button
                    className={`sub-nav-btn ${outputTab === "strategy" ? "active" : ""}`}
                    onClick={() => setOutputTab("strategy")}
                  >
                    <Target size={14} /> Strategy & Persona
                  </button>
                  <button
                    className={`sub-nav-btn ${outputTab === "ads" ? "active" : ""}`}
                    onClick={() => setOutputTab("ads")}
                  >
                    <Copy size={14} /> Ad Copy & A/B
                  </button>
                  <button
                    className={`sub-nav-btn ${outputTab === "socials" ? "active" : ""}`}
                    onClick={() => setOutputTab("socials")}
                  >
                    <Users size={14} /> Socials & TikTok
                  </button>
                  <button
                    className={`sub-nav-btn ${outputTab === "email" ? "active" : ""}`}
                    onClick={() => setOutputTab("email")}
                  >
                    <Send size={14} /> Email Suite
                  </button>
                  <button
                    className={`sub-nav-btn ${outputTab === "calendar" ? "active" : ""}`}
                    onClick={() => setOutputTab("calendar")}
                  >
                    <Calendar size={14} /> 7-Day Plan
                  </button>
                  <button
                    className={`sub-nav-btn ${outputTab === "mockup" ? "active" : ""}`}
                    onClick={() => setOutputTab("mockup")}
                  >
                    <Eye size={14} /> Live Ad Mockups
                  </button>
                </div>

                {campaignResult && (
                  <div className="quick-action-icons">
                    <button
                      className="icon-action-btn"
                      title="Export Campaign Brief as JSON"
                      onClick={downloadBriefJSON}
                    >
                      <Download size={15} />
                    </button>
                    <button
                      className="icon-action-btn"
                      title="Transfer Prompt to Visual Studio"
                      onClick={() => {
                        setActiveTab("visuals");
                        triggerToast("Visual prompt loaded into Visual Studio!");
                      }}
                    >
                      <ImageIcon size={15} />
                    </button>
                  </div>
                )}
              </div>

              <div className="output-content-area">
                {/* Empty State */}
                {!campaignResult && !loading && (
                  <div className="empty-workspace-state">
                    <div className="empty-visual-circle">
                      <Sparkles size={36} className="text-purple-400" />
                    </div>
                    <h3>Campaign Workspace Ready</h3>
                    <p>
                      Configure your product on the left and click <strong>Generate Full Campaign Suite</strong> to produce
                      creative angles, ad variants, copy, and visuals.
                    </p>
                    <button className="sample-run-btn" onClick={handleGenerateCampaign}>
                      ✨ Generate AeroPulse Demo Campaign
                    </button>
                  </div>
                )}

                {/* Loading State */}
                {loading && (
                  <div className="loading-workspace-state">
                    <div className="pulsing-spinner"></div>
                    <h3>Synthesizing Strategic Deliverables...</h3>
                    <div className="progress-step-list">
                      <div className="progress-step-item active">
                        <CheckCircle2 size={16} /> Formulating psychological angles & hooks
                      </div>
                      <div className="progress-step-item active">
                        <CheckCircle2 size={16} /> Mapping buyer persona & objection busters
                      </div>
                      <div className="progress-step-item active">
                        <CheckCircle2 size={16} /> Generating multi-platform scripts & copy
                      </div>
                      <div className="progress-step-item active">
                        <CheckCircle2 size={16} /> Formulating 7-day distribution calendar
                      </div>
                    </div>
                  </div>
                )}

                {/* Populated Result Content */}
                {campaignResult && !loading && (
                  <div className="populated-result-view">
                    {/* 1. STRATEGY & PERSONA */}
                    {outputTab === "strategy" && (
                      <div className="tab-pane-view">
                        <div className="hero-strategy-card">
                          <span className="purple-tag">CAMPAIGN TITLE</span>
                          <h2>{campaignResult.campaign_title}</h2>
                          <p className="strategy-tagline">"{campaignResult.tagline}"</p>
                          <p className="strategy-summary">{campaignResult.executive_summary}</p>
                        </div>

                        {campaignResult.target_persona && (
                          <div className="persona-profile-card">
                            <div className="card-sub-heading">
                              <Users size={18} />
                              <h4>Target Buyer Persona Profiler</h4>
                            </div>

                            <div className="persona-meta-grid">
                              <div className="meta-box">
                                <span className="meta-label">ARCHETYPE</span>
                                <strong>{campaignResult.target_persona.name}</strong>
                              </div>
                              <div className="meta-box">
                                <span className="meta-label">DEMOGRAPHICS</span>
                                <span>{campaignResult.target_persona.demographics}</span>
                              </div>
                            </div>

                            <div className="persona-traits-grid">
                              <div className="trait-col">
                                <span className="meta-label">CORE DRIVERS & DESIRES</span>
                                <ul>
                                  {campaignResult.target_persona.core_desires?.map((d, i) => (
                                    <li key={i}>✓ {d}</li>
                                  ))}
                                </ul>
                              </div>
                              <div className="trait-col">
                                <span className="meta-label">PAIN POINTS & FRICTIONS</span>
                                <ul>
                                  {campaignResult.target_persona.pain_points?.map((p, i) => (
                                    <li key={i}>⚠ {p}</li>
                                  ))}
                                </ul>
                              </div>
                            </div>

                            {campaignResult.target_persona.objections_busting && (
                              <div className="objection-buster-card">
                                <span className="meta-label">OBJECTION BUSTER STRATEGY</span>
                                <p>{campaignResult.target_persona.objections_busting}</p>
                              </div>
                            )}
                          </div>
                        )}

                        {campaignResult.value_propositions && (
                          <div className="usp-stack">
                            <h4>Key Value Propositions</h4>
                            <div className="usp-chips-grid">
                              {campaignResult.value_propositions.map((usp, i) => (
                                <div key={i} className="usp-chip-item">
                                  <span className="usp-num">0{i + 1}</span>
                                  <span>{usp}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* 2. AD COPIES & A/B */}
                    {outputTab === "ads" && (
                      <div className="tab-pane-view">
                        {campaignResult.ad_copies?.primary_ad && (
                          <div className="ad-variant-card primary-variant">
                            <div className="ad-variant-header">
                              <span className="green-tag">
                                PRIMARY AD COPY ({campaignResult.ad_copies.primary_ad.platform})
                              </span>
                              <button
                                className="copy-action-btn"
                                onClick={() =>
                                  copyText(
                                    `${campaignResult.ad_copies.primary_ad.hook}\n\n${campaignResult.ad_copies.primary_ad.body}\n\nCTA: ${campaignResult.ad_copies.primary_ad.cta}`,
                                    "primary"
                                  )
                                }
                              >
                                {copiedKey === "primary" ? <Check size={14} /> : <Copy size={14} />} Copy
                              </button>
                            </div>
                            <div className="hook-headline">"{campaignResult.ad_copies.primary_ad.hook}"</div>
                            <div className="ad-body-paragraph">{campaignResult.ad_copies.primary_ad.body}</div>
                            <div className="cta-callout">
                              <strong>Call-to-Action:</strong> {campaignResult.ad_copies.primary_ad.cta}
                            </div>
                          </div>
                        )}

                        <div className="ab-grid-layout">
                          <div className="ad-variant-card">
                            <div className="ad-variant-header">
                              <span className="purple-tag">
                                VARIANT A ({campaignResult.ad_copies?.variant_a?.angle || "Benefit"})
                              </span>
                              <button
                                className="copy-action-btn"
                                onClick={() =>
                                  copyText(
                                    `${campaignResult.ad_copies?.variant_a?.headline}\n${campaignResult.ad_copies?.variant_a?.hook}`,
                                    "var_a"
                                  )
                                }
                              >
                                {copiedKey === "var_a" ? <Check size={14} /> : <Copy size={14} />} Copy
                              </button>
                            </div>
                            <h5>{campaignResult.ad_copies?.variant_a?.headline}</h5>
                            <p className="variant-hook">"{campaignResult.ad_copies?.variant_a?.hook}"</p>
                            <small className="hypothesis-text">
                              💡 <strong>Hypothesis:</strong> {campaignResult.ad_copies?.variant_a?.hypothesis}
                            </small>
                          </div>

                          <div className="ad-variant-card">
                            <div className="ad-variant-header">
                              <span className="blue-tag">
                                VARIANT B ({campaignResult.ad_copies?.variant_b?.angle || "Curiosity"})
                              </span>
                              <button
                                className="copy-action-btn"
                                onClick={() =>
                                  copyText(
                                    `${campaignResult.ad_copies?.variant_b?.headline}\n${campaignResult.ad_copies?.variant_b?.hook}`,
                                    "var_b"
                                  )
                                }
                              >
                                {copiedKey === "var_b" ? <Check size={14} /> : <Copy size={14} />} Copy
                              </button>
                            </div>
                            <h5>{campaignResult.ad_copies?.variant_b?.headline}</h5>
                            <p className="variant-hook">"{campaignResult.ad_copies?.variant_b?.hook}"</p>
                            <small className="hypothesis-text">
                              💡 <strong>Hypothesis:</strong> {campaignResult.ad_copies?.variant_b?.hypothesis}
                            </small>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* 3. SOCIALS & TIKTOK */}
                    {outputTab === "socials" && (
                      <div className="tab-pane-view">
                        {campaignResult.social_posts?.instagram && (
                          <div className="ad-variant-card">
                            <div className="ad-variant-header">
                              <span className="purple-tag">📸 INSTAGRAM CAPTION & HASHTAGS</span>
                              <button
                                className="copy-action-btn"
                                onClick={() =>
                                  copyText(
                                    `${campaignResult.social_posts.instagram.caption}\n\n${campaignResult.social_posts.instagram.hashtags?.join(" ")}`,
                                    "ig"
                                  )
                                }
                              >
                                {copiedKey === "ig" ? <Check size={14} /> : <Copy size={14} />} Copy
                              </button>
                            </div>
                            <pre className="caption-text-block">{campaignResult.social_posts.instagram.caption}</pre>
                            <div className="hashtags-container">
                              {campaignResult.social_posts.instagram.hashtags?.map((tag, idx) => (
                                <span key={idx} className="hashtag-badge">{tag}</span>
                              ))}
                            </div>
                          </div>
                        )}

                        {campaignResult.social_posts?.linkedin && (
                          <div className="ad-variant-card">
                            <div className="ad-variant-header">
                              <span className="blue-tag">💼 LINKEDIN THOUGHT LEADERSHIP</span>
                              <button
                                className="copy-action-btn"
                                onClick={() => copyText(campaignResult.social_posts.linkedin.post, "li")}
                              >
                                {copiedKey === "li" ? <Check size={14} /> : <Copy size={14} />} Copy
                              </button>
                            </div>
                            <pre className="caption-text-block">{campaignResult.social_posts.linkedin.post}</pre>
                          </div>
                        )}

                        {campaignResult.social_posts?.tiktok_script && (
                          <div className="ad-variant-card tiktok-script-card">
                            <div className="ad-variant-header">
                              <span className="pink-tag">
                                🎵 TIKTOK & REELS SCRIPT ({campaignResult.social_posts.tiktok_script.duration || "20s"})
                              </span>
                              <button
                                className="copy-action-btn"
                                onClick={() =>
                                  copyText(JSON.stringify(campaignResult.social_posts.tiktok_script, null, 2), "tt")
                                }
                              >
                                {copiedKey === "tt" ? <Check size={14} /> : <Copy size={14} />} Copy
                              </button>
                            </div>
                            <div className="script-line-item">
                              <strong>Visual Hook:</strong> {campaignResult.social_posts.tiktok_script.hook_visual}
                            </div>
                            <div className="script-line-item">
                              <strong>Voiceover:</strong> "{campaignResult.social_posts.tiktok_script.voiceover}"
                            </div>
                            <div className="scene-breakdown-timeline">
                              <strong>Scene Breakdown:</strong>
                              <ul>
                                {campaignResult.social_posts.tiktok_script.scene_breakdown?.map((sc, i) => (
                                  <li key={i}>{sc}</li>
                                ))}
                              </ul>
                            </div>
                            <div className="audio-recommendation-tag">
                              🎧 <strong>Audio:</strong> {campaignResult.social_posts.tiktok_script.audio_recommendation}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* 4. EMAIL SUITE */}
                    {outputTab === "email" && (
                      <div className="tab-pane-view">
                        {campaignResult.email_newsletter && (
                          <div className="ad-variant-card">
                            <div className="ad-variant-header">
                              <span className="purple-tag">✉️ HIGH-CONVERTING EMAIL NEWSLETTER</span>
                              <button
                                className="copy-action-btn"
                                onClick={() =>
                                  copyText(
                                    `Subject: ${campaignResult.email_newsletter.subject_lines?.[0]}\n\n${campaignResult.email_newsletter.body}\n\nCTA: ${campaignResult.email_newsletter.cta}`,
                                    "em"
                                  )
                                }
                              >
                                {copiedKey === "em" ? <Check size={14} /> : <Copy size={14} />} Copy
                              </button>
                            </div>

                            <div className="subject-line-options">
                              <span className="meta-label">SUBJECT LINE ALTERNATIVES (A/B TESTED)</span>
                              {campaignResult.email_newsletter.subject_lines?.map((subj, i) => (
                                <div key={i} className="subject-item-box">
                                  <span>Option 0{i + 1}:</span> {subj}
                                </div>
                              ))}
                            </div>

                            <div className="email-preview-snippet-box">
                              <span className="meta-label">PREVIEW SNIPPET</span>
                              <p className="snippet-italic">{campaignResult.email_newsletter.preview_text}</p>
                            </div>

                            <div className="email-body-container">
                              <span className="meta-label">EMAIL BODY</span>
                              <pre className="email-body-pre">{campaignResult.email_newsletter.body}</pre>
                              <div className="email-cta-preview-button">
                                {campaignResult.email_newsletter.cta}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* 5. 7-DAY CALENDAR */}
                    {outputTab === "calendar" && (
                      <div className="tab-pane-view">
                        <div className="calendar-card-grid">
                          {campaignResult.content_calendar_7day?.map((plan, i) => (
                            <div key={i} className="day-schedule-card">
                              <div className="day-card-header">
                                <span className="day-number-tag">{plan.day}</span>
                                <span className="channel-badge-pill">{plan.channel}</span>
                              </div>
                              <div className="content-type-title">{plan.content_type}</div>
                              <p className="day-idea-text">{plan.idea}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 6. LIVE AD MOCKUPS */}
                    {outputTab === "mockup" && (
                      <div className="tab-pane-view flex-center-pane">
                        <div className="mockup-platform-switcher">
                          <button
                            className={`platform-btn ${mockupType === "instagram" ? "active" : ""}`}
                            onClick={() => setMockupType("instagram")}
                          >
                            Instagram Feed Ad
                          </button>
                          <button
                            className={`platform-btn ${mockupType === "tiktok" ? "active" : ""}`}
                            onClick={() => setMockupType("tiktok")}
                          >
                            TikTok Video Reel
                          </button>
                          <button
                            className={`platform-btn ${mockupType === "linkedin" ? "active" : ""}`}
                            onClick={() => setMockupType("linkedin")}
                          >
                            LinkedIn Post
                          </button>
                          <button
                            className={`platform-btn ${mockupType === "google" ? "active" : ""}`}
                            onClick={() => setMockupType("google")}
                          >
                            Google Search Ad
                          </button>
                        </div>

                        {/* INSTAGRAM MOCKUP */}
                        {mockupType === "instagram" && (
                          <div className="phone-device-frame">
                            <div className="ig-feed-card">
                              <div className="ig-top-header">
                                <div className="ig-avatar-circle">{productName.charAt(0)}</div>
                                <div className="ig-user-info">
                                  <div className="ig-brand-handle">{productName.toLowerCase().replace(/\s+/g, "_")}</div>
                                  <div className="ig-sponsored-label">Sponsored • Adspire</div>
                                </div>
                              </div>

                              <div className="ig-media-slot">
                                {renderedVisual ? (
                                  <img src={renderedVisual} alt="Campaign Visual" className="ig-media-img" />
                                ) : (
                                  <div className="media-placeholder-state">
                                    <Sparkles size={28} />
                                    <span>Creative Visual Asset</span>
                                    <small>{campaignResult.campaign_title}</small>
                                  </div>
                                )}
                              </div>

                              <div className="ig-cta-action-bar">
                                <span>{campaignResult.ad_copies?.primary_ad?.cta || "Shop Now"}</span>
                                <ArrowRight size={14} />
                              </div>

                              <div className="ig-interaction-icons">
                                <div className="left-icons">
                                  <button
                                    className={`icon-btn ${isLiked ? "liked" : ""}`}
                                    onClick={() => setIsLiked(!isLiked)}
                                  >
                                    <Heart size={20} fill={isLiked ? "#ef4444" : "none"} />
                                  </button>
                                  <button className="icon-btn">
                                    <MessageCircle size={20} />
                                  </button>
                                  <button className="icon-btn">
                                    <Share2 size={20} />
                                  </button>
                                </div>
                                <button
                                  className={`icon-btn ${isBookmarked ? "bookmarked" : ""}`}
                                  onClick={() => setIsBookmarked(!isBookmarked)}
                                >
                                  <Bookmark size={20} fill={isBookmarked ? "#fff" : "none"} />
                                </button>
                              </div>

                              <div className="ig-caption-container">
                                <strong>{productName.toLowerCase().replace(/\s+/g, "_")}</strong>{" "}
                                {campaignResult.social_posts?.instagram?.caption?.slice(0, 140)}...
                              </div>
                            </div>
                          </div>
                        )}

                        {/* TIKTOK REEL MOCKUP */}
                        {mockupType === "tiktok" && (
                          <div className="phone-device-frame tiktok-reel-frame">
                            <div className="tt-player-screen">
                              {renderedVisual ? (
                                <img src={renderedVisual} alt="TikTok Background" className="tt-media-video-img" />
                              ) : (
                                <div className="tt-video-placeholder">
                                  <Play size={40} className="text-pink-400" />
                                </div>
                              )}

                              <div className="tt-overlay-hud">
                                <div className="tt-action-column">
                                  <div className="tt-hud-btn" onClick={() => setIsLiked(!isLiked)}>
                                    <Heart size={24} fill={isLiked ? "#ef4444" : "#fff"} color={isLiked ? "#ef4444" : "#fff"} />
                                    <span>28.4K</span>
                                  </div>
                                  <div className="tt-hud-btn">
                                    <MessageCircle size={24} />
                                    <span>1.4K</span>
                                  </div>
                                  <div className="tt-hud-btn">
                                    <Share2 size={24} />
                                    <span>9.2K</span>
                                  </div>
                                </div>

                                <div className="tt-bottom-details">
                                  <div className="tt-handle">@{productName.toLowerCase().replace(/\s+/g, "_")}</div>
                                  <p className="tt-script-snippet">
                                    {campaignResult.social_posts?.tiktok_script?.voiceover?.slice(0, 85)}... #growth #viral
                                  </p>
                                  <div className="tt-audio-strip">
                                    <Volume2 size={13} />
                                    <span>{campaignResult.social_posts?.tiktok_script?.audio_recommendation || "Trending Commercial Audio"}</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* LINKEDIN MOCKUP */}
                        {mockupType === "linkedin" && (
                          <div className="desktop-card-frame">
                            <div className="linkedin-card-box">
                              <div className="li-user-head">
                                <div className="li-avatar-square">{productName.charAt(0)}</div>
                                <div>
                                  <div className="li-company-title">{productName} Official</div>
                                  <div className="li-subtext">32,800 followers • Promoted</div>
                                </div>
                              </div>

                              <p className="li-body-copy">
                                {campaignResult.social_posts?.linkedin?.post || campaignResult.executive_summary}
                              </p>

                              <div className="li-banner-slot">
                                {renderedVisual ? (
                                  <img src={renderedVisual} alt="Banner" className="li-banner-img" />
                                ) : (
                                  <div className="li-placeholder-box">
                                    <h4>{campaignResult.campaign_title}</h4>
                                    <p>{campaignResult.tagline}</p>
                                  </div>
                                )}
                              </div>

                              <div className="li-cta-button-strip">
                                <span>{campaignResult.ad_copies?.primary_ad?.cta || "Learn More"}</span>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* GOOGLE SEARCH MOCKUP */}
                        {mockupType === "google" && (
                          <div className="desktop-card-frame">
                            <div className="google-serp-card">
                              <div className="google-ad-badge">Sponsored • https://www.{productName.toLowerCase().replace(/\s+/g, "")}.com</div>
                              <div className="google-title-link">{campaignResult.campaign_title} | Official Store</div>
                              <div className="google-description-text">
                                {description} {campaignResult.value_propositions?.join(". ")}
                              </div>
                              <div className="google-sitelinks-row">
                                <span>Shop Now</span>
                                <span>Key Features</span>
                                <span>Verified Reviews</span>
                                <span>Limited Time Offer</span>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ======================================================
            TAB 2: CREATIVE VISUAL STUDIO
        ====================================================== */}
        {activeTab === "visuals" && (
          <div className="visual-studio-container">
            <div className="studio-hero-center">
              <div className="hero-top-badge">
                <ImageIcon size={14} /> GENERATIVE VISUAL CREATIVE ENGINE
              </div>
              <h2>High-Resolution Advertising Visuals</h2>
              <p>Synthesize commercial product visuals, 3D renderings, and high-impact social creatives.</p>
            </div>

            <div className="campaign-studio-grid">
              <div className="studio-card">
                <div className="card-top-header">
                  <h3>Visual Asset Controls</h3>
                </div>

                <div className="custom-form-group">
                  <label>CREATIVE PROMPT & COMPOSITION</label>
                  <textarea
                    rows={5}
                    value={visualPrompt}
                    onChange={(e) => setVisualPrompt(e.target.value)}
                    placeholder="Describe lighting, composition, camera angle, and subject matter..."
                    className="modern-textarea"
                  />
                </div>

                {campaignResult?.image_prompt && (
                  <button
                    className="link-prompt-btn"
                    onClick={() => {
                      setVisualPrompt(campaignResult.image_prompt);
                      triggerToast("Loaded prompt from active campaign!");
                    }}
                  >
                    ✦ Use Active Campaign Prompt
                  </button>
                )}

                <div className="custom-form-group mt-3">
                  <label>ARTISTIC STYLE PRESET</label>
                  <div className="style-preset-grid">
                    {["Photorealistic", "3D Render", "Cyberpunk", "Minimalist", "Luxury", "Vibrant Pop"].map((st) => (
                      <button
                        key={st}
                        className={`style-chip-btn ${visualStyle === st ? "active" : ""}`}
                        onClick={() => setVisualStyle(st)}
                      >
                        {st}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="custom-form-group mt-3">
                  <label>ASPECT RATIO DIMENSIONS</label>
                  <div className="ratio-selector-grid">
                    {[
                      { id: "1:1", label: "1:1 Square (Feed)" },
                      { id: "16:9", label: "16:9 Banner (Landscape)" },
                      { id: "9:16", label: "9:16 Story (Portrait)" },
                    ].map((asp) => (
                      <button
                        key={asp.id}
                        className={`ratio-btn ${aspectRatio === asp.id ? "active" : ""}`}
                        onClick={() => setAspectRatio(asp.id)}
                      >
                        {asp.label}
                      </button>
                    ))}
                  </div>
                </div>

                <button
                  className="action-btn-glow mt-4"
                  onClick={handleGenerateVisual}
                  disabled={generatingVisual}
                >
                  {generatingVisual ? (
                    <>
                      <RefreshCw size={18} className="spin-animation" />
                      <span>Synthesizing High-Res Visual...</span>
                    </>
                  ) : (
                    <>
                      <ImageIcon size={18} />
                      <span>Generate Creative Asset</span>
                    </>
                  )}
                </button>
              </div>

              <div className="studio-card flex-center-card">
                {generatingVisual ? (
                  <div className="loading-workspace-state">
                    <div className="pulsing-spinner"></div>
                    <h3>Synthesizing 8K Creative Visual...</h3>
                    <p>Executing neural rendering & lighting calculations...</p>
                  </div>
                ) : renderedVisual ? (
                  <div className="visual-render-preview-wrapper">
                    <div className="visual-image-frame">
                      <img src={renderedVisual} alt="Creative visual asset" className="rendered-asset-img" />
                      <div className="visual-download-overlay">
                        <a
                          href={renderedVisual}
                          download={`adspire_creative_${Date.now()}.png`}
                          target="_blank"
                          rel="noreferrer"
                          className="download-asset-pill"
                        >
                          <Download size={16} /> Download High-Res PNG
                        </a>
                      </div>
                    </div>
                    <div className="asset-metadata-bar">
                      <span><strong>Style:</strong> {visualStyle}</span>
                      <span><strong>Format:</strong> {aspectRatio}</span>
                      <span><strong>Status:</strong> Synthesized</span>
                    </div>
                  </div>
                ) : (
                  <div className="empty-workspace-state">
                    <div className="empty-visual-circle">
                      <ImageIcon size={36} className="text-purple-400" />
                    </div>
                    <h3>Visual Canvas Idle</h3>
                    <p>Enter your creative description and click Generate to produce advertising assets.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ======================================================
            TAB 3: BUDGET & ROAS SIMULATOR
        ====================================================== */}
        {activeTab === "budget" && (
          <div className="budget-workspace-container">
            <div className="studio-hero-center">
              <div className="hero-top-badge">
                <DollarSign size={14} /> MATHEMATICAL ROAS & SPEND ENGINE
              </div>
              <h2>Predictive Ad Budget & Revenue Simulator</h2>
              <p>Simulate CPC, impressions, conversions, and expected net profit across 6 major advertising networks.</p>
            </div>

            {/* Slider Controls */}
            <div className="studio-card mb-6">
              <div className="budget-sliders-grid">
                <div className="custom-form-group">
                  <div className="flex-label-row">
                    <label>TOTAL CAMPAIGN BUDGET</label>
                    <span className="highlight-metric-val">${budgetAmount.toLocaleString()}</span>
                  </div>
                  <input
                    type="range"
                    min="300"
                    max="30000"
                    step="100"
                    value={budgetAmount}
                    onChange={(e) => {
                      const val = Number(e.target.value);
                      setBudgetAmount(val);
                      fetchBudgetCalculations(val, budgetGoal, budgetDuration);
                    }}
                    className="modern-range-slider"
                  />
                </div>

                <div className="custom-form-group">
                  <div className="flex-label-row">
                    <label>CAMPAIGN DURATION</label>
                    <span className="highlight-metric-val">{budgetDuration} Days</span>
                  </div>
                  <input
                    type="range"
                    min="7"
                    max="90"
                    step="1"
                    value={budgetDuration}
                    onChange={(e) => {
                      const val = Number(e.target.value);
                      setBudgetDuration(val);
                      fetchBudgetCalculations(budgetAmount, budgetGoal, val);
                    }}
                    className="modern-range-slider"
                  />
                </div>

                <div className="custom-form-group">
                  <label>OPTIMIZATION GOAL</label>
                  <select
                    value={budgetGoal}
                    onChange={(e) => {
                      setBudgetGoal(e.target.value);
                      fetchBudgetCalculations(budgetAmount, e.target.value, budgetDuration);
                    }}
                    className="modern-select"
                  >
                    <option>Sales</option>
                    <option>Lead Generation</option>
                    <option>Brand Awareness</option>
                  </select>
                </div>
              </div>
            </div>

            {/* KPI Cards */}
            {budgetPlan && (
              <div className="kpi-metric-strip">
                <div className="kpi-card-box purple-border">
                  <span className="kpi-label">PROJECTED ROAS</span>
                  <div className="kpi-number-display">{budgetPlan.summary?.projected_roas}</div>
                  <span className="kpi-subtext">Return on Ad Spend</span>
                </div>

                <div className="kpi-card-box green-border">
                  <span className="kpi-label">PROJECTED REVENUE</span>
                  <div className="kpi-number-display">${budgetPlan.summary?.projected_revenue?.toLocaleString()}</div>
                  <span className="kpi-subtext">Net Profit: +${budgetPlan.summary?.net_profit?.toLocaleString()}</span>
                </div>

                <div className="kpi-card-box blue-border">
                  <span className="kpi-label">AUDIENCE REACH</span>
                  <div className="kpi-number-display">{budgetPlan.summary?.total_reach?.toLocaleString()}</div>
                  <span className="kpi-subtext">Estimated Ad Impressions</span>
                </div>

                <div className="kpi-card-box amber-border">
                  <span className="kpi-label">ESTIMATED CONVERSIONS</span>
                  <div className="kpi-number-display">{budgetPlan.summary?.total_conversions?.toLocaleString()}</div>
                  <span className="kpi-subtext">Avg CPA: ${budgetPlan.summary?.avg_cpa}</span>
                </div>
              </div>
            )}

            {/* Breakdown Table */}
            <div className="studio-card mt-6">
              <div className="card-top-header">
                <h3>Channel Allocation & Unit Economics</h3>
              </div>

              <div className="table-overflow-wrapper">
                <table className="modern-data-table">
                  <thead>
                    <tr>
                      <th>Channel</th>
                      <th>Share</th>
                      <th>Allocated Budget</th>
                      <th>Est. CPC</th>
                      <th>Est. Clicks</th>
                      <th>Est. Conversions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {budgetPlan?.channels?.map((ch, idx) => (
                      <tr key={idx}>
                        <td><strong>{ch.name}</strong></td>
                        <td><span className="purple-tag">{ch.percentage}%</span></td>
                        <td>${ch.budget}</td>
                        <td>${ch.cpc}</td>
                        <td>{ch.estimated_clicks?.toLocaleString()}</td>
                        <td><strong className="text-emerald-400">{ch.estimated_conversions?.toLocaleString()}</strong></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="strategic-tips-container mt-6">
                <h4>✦ Strategic Budget Insights</h4>
                <ul>
                  {budgetPlan?.strategic_tips?.map((tip, i) => (
                    <li key={i}>
                      <TrendingUp size={15} className="text-emerald-400" />
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* ======================================================
            TAB 4: CAMPAIGN LIBRARY
        ====================================================== */}
        {activeTab === "library" && (
          <div className="library-workspace-container">
            <div className="studio-hero-center">
              <div className="hero-top-badge">
                <FolderArchive size={14} /> PERSISTENT CAMPAIGN REPOSITORY
              </div>
              <h2>Saved Marketing Campaigns</h2>
              <p>Review, reload, or manage past generated marketing campaigns.</p>
            </div>

            {savedCampaigns.length === 0 ? (
              <div className="studio-card empty-workspace-state p-12">
                <div className="empty-visual-circle">
                  <Layers size={36} className="text-purple-400" />
                </div>
                <h3>No Campaigns Saved Yet</h3>
                <p>Generate your first marketing campaign to begin building your growth repository!</p>
                <button className="action-btn-glow" onClick={() => setActiveTab("studio")}>
                  🚀 Open Campaign Studio
                </button>
              </div>
            ) : (
              <div className="library-cards-grid">
                {savedCampaigns.map((item) => (
                  <div
                    key={item.id}
                    className="library-item-card"
                    onClick={() => {
                      if (typeof item.campaign_content === "object") {
                        setCampaignResult(item.campaign_content);
                        setProductName(item.product_name || "Campaign");
                        setActiveTab("studio");
                        triggerToast(`Loaded: ${item.product_name}`);
                      }
                    }}
                  >
                    <div className="item-card-top">
                      <span className="purple-tag">{item.platform}</span>
                      <span className="item-date">{item.created_at || "Recent"}</span>
                    </div>

                    <h3 className="item-title">{item.product_name}</h3>
                    <p className="item-sub">
                      <strong>Audience:</strong> {item.target_audience || "General"}
                    </p>
                    <p className="item-sub">
                      <strong>Goal:</strong> {item.goal}
                    </p>

                    <div className="item-card-footer">
                      <span className="item-open-hint">Open in Studio →</span>
                      <button
                        className="delete-icon-btn"
                        title="Delete campaign"
                        onClick={(e) => handleDeleteCampaign(item.id, e)}
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      {/* ========================================================
          GLOBAL FOOTER
      ======================================================== */}
      <footer className="main-footer">
        <div className="footer-inner-content">
          <div className="brand-main-title">
            Ad<span>spire</span>
          </div>
          <p>Autonomous Campaign Architecture & Strategic Marketing Platform</p>
          <div className="tech-badge-tags">
            <span>React 19</span> • <span>Tailwind CSS</span> • <span>FLUX.1 Neural Engine</span> • <span>Financial ROAS Solvers</span> • <span>SQLite</span>
          </div>
        </div>
      </footer>
    </div>
  );
}