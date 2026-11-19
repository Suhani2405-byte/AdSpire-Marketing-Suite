import React, { useEffect, useRef, useState } from "react";
import {
  Target, Copy, Check, Users, Send, Calendar, Eye, Download, Image as ImageIcon,
  Sparkles, FileText, FileJson, Printer, AlertTriangle,
} from "lucide-react";
import { useApp } from "../state/AppState";
import { exportJSON, exportMarkdown, exportPDF } from "../utils/exporters";
import AdMockups from "./AdMockups";

const TABS = [
  { id: "strategy", label: "Strategy & Persona", icon: Target },
  { id: "ads", label: "Ad Copy & A/B", icon: Copy },
  { id: "socials", label: "Socials & Video", icon: Users },
  { id: "email", label: "Email Suite", icon: Send },
  { id: "calendar", label: "7-Day Plan", icon: Calendar },
  { id: "mockup", label: "Live Ad Mockups", icon: Eye },
];

function CopyButton({ text, id, copiedKey, onCopy }) {
  return (
    <button className="copy-action-btn" onClick={() => onCopy(text, id)}>
      {copiedKey === id ? <Check size={14} /> : <Copy size={14} />} Copy
    </button>
  );
}

function StreamingView({ status, text }) {
  const ref = useRef(null);
  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight;
  }, [text]);
  return (
    <div className="loading-workspace-state">
      <div className="pulsing-spinner"></div>
      <h3>{status || "Generating..."}</h3>
      <p className="stream-counter">{text ? `${text.length.toLocaleString()} characters written` : "Waiting for the first words..."}</p>
      {text && (
        <pre ref={ref} className="stream-preview">
          {text}
        </pre>
      )}
    </div>
  );
}

export default function CampaignOutput() {
  const {
    campaignResult: c, campaignMeta, loading, streamStatus, streamText, form, renderedVisual,
    handleGenerateCampaign, setActiveTab, triggerToast, copyText,
  } = useApp();
  const [outputTab, setOutputTab] = useState("strategy");
  const [copiedKey, setCopiedKey] = useState(null);
  const [exportOpen, setExportOpen] = useState(false);

  const onCopy = async (text, key) => {
    if (await copyText(text)) {
      setCopiedKey(key);
      setTimeout(() => setCopiedKey(null), 2000);
    }
  };

  const ads = c?.ad_copies || {};
  const social = c?.social_posts || {};
  const persona = c?.target_persona;
  const email = c?.email_newsletter;

  return (
    <div id="campaign-output-pane" className="studio-card output-card">
      <div className="output-top-bar">
        <div className="output-nav-tabs">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button key={id} className={`sub-nav-btn ${outputTab === id ? "active" : ""}`} onClick={() => setOutputTab(id)}>
              <Icon size={14} /> {label}
            </button>
          ))}
        </div>

        {c && !loading && (
          <div className="quick-action-icons">
            <div className="export-menu-wrap">
              <button className="icon-action-btn" title="Export campaign" onClick={() => setExportOpen((o) => !o)}>
                <Download size={15} />
              </button>
              {exportOpen && (
                <div className="export-menu" onMouseLeave={() => setExportOpen(false)}>
                  <button onClick={() => { if (!exportPDF(c, form.productName, renderedVisual)) triggerToast("Allow pop-ups to export PDF"); setExportOpen(false); }}>
                    <Printer size={14} /> PDF (print)
                  </button>
                  <button onClick={() => { exportMarkdown(c, form.productName); setExportOpen(false); }}>
                    <FileText size={14} /> Markdown
                  </button>
                  <button onClick={() => { exportJSON(c, form.productName); setExportOpen(false); }}>
                    <FileJson size={14} /> JSON
                  </button>
                </div>
              )}
            </div>
            <button
              className="icon-action-btn"
              title="Open prompt in Visual Studio"
              onClick={() => {
                setActiveTab("visuals");
                triggerToast("Campaign image prompt loaded into Visual Studio");
              }}
            >
              <ImageIcon size={15} />
            </button>
          </div>
        )}
      </div>

      <div className="output-content-area">
        {!c && !loading && (
          <div className="empty-workspace-state">
            <div className="empty-visual-circle">
              <Sparkles size={36} className="text-purple-400" />
            </div>
            <h3>Campaign Workspace Ready</h3>
            <p>
              Fill in your product on the left and click <strong>Generate Full Campaign Suite</strong> to produce
              creative angles, ad variants, copy, and visuals.
            </p>
            <button className="sample-run-btn" onClick={handleGenerateCampaign}>
              ✨ Generate Demo Campaign
            </button>
          </div>
        )}

        {loading && <StreamingView status={streamStatus} text={streamText} />}

        {c && !loading && (
          <div className="populated-result-view">
            {campaignMeta?.source === "template" && (
              <div className="warning-banner">
                <AlertTriangle size={16} />
                <span>
                  {campaignMeta.warning || "The AI model was unavailable, so this is a generic template."} Click Generate again to retry.
                </span>
              </div>
            )}

            {outputTab === "strategy" && (
              <div className="tab-pane-view">
                <div className="hero-strategy-card">
                  <span className="purple-tag">CAMPAIGN TITLE</span>
                  <h2>{c.campaign_title}</h2>
                  <p className="strategy-tagline">"{c.tagline}"</p>
                  <p className="strategy-summary">{c.executive_summary}</p>
                  {campaignMeta?.model && <p className="model-credit">Generated by {campaignMeta.model}</p>}
                </div>

                {persona && (
                  <div className="persona-profile-card">
                    <div className="card-sub-heading">
                      <Users size={18} />
                      <h4>Target Buyer Persona</h4>
                    </div>
                    <div className="persona-meta-grid">
                      <div className="meta-box">
                        <span className="meta-label">ARCHETYPE</span>
                        <strong>{persona.name}</strong>
                      </div>
                      <div className="meta-box">
                        <span className="meta-label">DEMOGRAPHICS</span>
                        <span>{persona.demographics}</span>
                      </div>
                    </div>
                    <div className="persona-traits-grid">
                      <div className="trait-col">
                        <span className="meta-label">CORE DRIVERS & DESIRES</span>
                        <ul>{persona.core_desires?.map((d, i) => <li key={i}>✓ {d}</li>)}</ul>
                      </div>
                      <div className="trait-col">
                        <span className="meta-label">PAIN POINTS & FRICTIONS</span>
                        <ul>{persona.pain_points?.map((p, i) => <li key={i}>⚠ {p}</li>)}</ul>
                      </div>
                    </div>
                    {persona.objections_busting && (
                      <div className="objection-buster-card">
                        <span className="meta-label">OBJECTION BUSTER STRATEGY</span>
                        <p>{persona.objections_busting}</p>
                      </div>
                    )}
                  </div>
                )}

                {c.value_propositions && (
                  <div className="usp-stack">
                    <h4>Key Value Propositions</h4>
                    <div className="usp-chips-grid">
                      {c.value_propositions.map((usp, i) => (
                        <div key={i} className="usp-chip-item">
                          <span className="usp-num">0{i + 1}</span>
                          <span>{usp}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {c.budget_recommendations?.suggested_split && (
                  <div className="usp-stack">
                    <h4>AI Budget Recommendation</h4>
                    <div className="usp-chips-grid">
                      {Object.entries(c.budget_recommendations.suggested_split).map(([ch, pct]) => (
                        <div key={ch} className="usp-chip-item">
                          <span className="usp-num">{pct}</span>
                          <span>{ch}</span>
                        </div>
                      ))}
                    </div>
                    <p className="model-credit">
                      Expected CPC {c.budget_recommendations.expected_cpc} • Expected CTR {c.budget_recommendations.expected_ctr}
                    </p>
                  </div>
                )}
              </div>
            )}

            {outputTab === "ads" && (
              <div className="tab-pane-view">
                {ads.primary_ad && (
                  <div className="ad-variant-card primary-variant">
                    <div className="ad-variant-header">
                      <span className="green-tag">PRIMARY AD COPY ({ads.primary_ad.platform || form.platform})</span>
                      <CopyButton id="primary" copiedKey={copiedKey} onCopy={onCopy}
                        text={`${ads.primary_ad.hook}\n\n${ads.primary_ad.body}\n\nCTA: ${ads.primary_ad.cta}`} />
                    </div>
                    <div className="hook-headline">"{ads.primary_ad.hook}"</div>
                    <div className="ad-body-paragraph">{ads.primary_ad.body}</div>
                    <div className="cta-callout">
                      <strong>Call-to-Action:</strong> {ads.primary_ad.cta}
                    </div>
                  </div>
                )}
                <div className="ab-grid-layout">
                  {[["variant_a", "VARIANT A", "purple-tag", "Benefit"], ["variant_b", "VARIANT B", "blue-tag", "Curiosity"]].map(([k, label, cls, fallback]) => (
                    <div key={k} className="ad-variant-card">
                      <div className="ad-variant-header">
                        <span className={cls}>{label} ({ads[k]?.angle || fallback})</span>
                        <CopyButton id={k} copiedKey={copiedKey} onCopy={onCopy} text={`${ads[k]?.headline}\n${ads[k]?.hook}`} />
                      </div>
                      <h5>{ads[k]?.headline}</h5>
                      <p className="variant-hook">"{ads[k]?.hook}"</p>
                      <small className="hypothesis-text">
                        💡 <strong>Hypothesis:</strong> {ads[k]?.hypothesis}
                      </small>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {outputTab === "socials" && (
              <div className="tab-pane-view">
                {social.instagram && (
                  <div className="ad-variant-card">
                    <div className="ad-variant-header">
                      <span className="purple-tag">📸 INSTAGRAM CAPTION & HASHTAGS</span>
                      <CopyButton id="ig" copiedKey={copiedKey} onCopy={onCopy}
                        text={`${social.instagram.caption}\n\n${social.instagram.hashtags?.join(" ") || ""}`} />
                    </div>
                    <pre className="caption-text-block">{social.instagram.caption}</pre>
                    <div className="hashtags-container">
                      {social.instagram.hashtags?.map((tag, idx) => <span key={idx} className="hashtag-badge">{tag}</span>)}
                    </div>
                  </div>
                )}

                {social.linkedin && (
                  <div className="ad-variant-card">
                    <div className="ad-variant-header">
                      <span className="blue-tag">💼 LINKEDIN POST</span>
                      <CopyButton id="li" copiedKey={copiedKey} onCopy={onCopy} text={social.linkedin.post} />
                    </div>
                    <pre className="caption-text-block">{social.linkedin.post}</pre>
                  </div>
                )}

                {social.twitter_x && (
                  <div className="ad-variant-card">
                    <div className="ad-variant-header">
                      <span className="blue-tag">𝕏 THREAD</span>
                      <CopyButton id="x" copiedKey={copiedKey} onCopy={onCopy}
                        text={[social.twitter_x.hook_tweet, ...(social.twitter_x.thread || [])].join("\n\n")} />
                    </div>
                    <ol className="thread-list">
                      {[social.twitter_x.hook_tweet, ...(social.twitter_x.thread || [])].filter(Boolean).map((t, i) => (
                        <li key={i}>{t}</li>
                      ))}
                    </ol>
                  </div>
                )}

                {social.tiktok_script && (
                  <div className="ad-variant-card tiktok-script-card">
                    <div className="ad-variant-header">
                      <span className="pink-tag">🎵 TIKTOK & REELS SCRIPT ({social.tiktok_script.duration || "20s"})</span>
                      <CopyButton id="tt" copiedKey={copiedKey} onCopy={onCopy} text={social.tiktok_script} />
                    </div>
                    <div className="script-line-item">
                      <strong>Visual Hook:</strong> {social.tiktok_script.hook_visual}
                    </div>
                    <div className="script-line-item">
                      <strong>Voiceover:</strong> "{social.tiktok_script.voiceover}"
                    </div>
                    <div className="scene-breakdown-timeline">
                      <strong>Scene Breakdown:</strong>
                      <ul>{social.tiktok_script.scene_breakdown?.map((sc, i) => <li key={i}>{sc}</li>)}</ul>
                    </div>
                    <div className="audio-recommendation-tag">
                      🎧 <strong>Audio:</strong> {social.tiktok_script.audio_recommendation}
                    </div>
                  </div>
                )}
              </div>
            )}

            {outputTab === "email" && email && (
              <div className="tab-pane-view">
                <div className="ad-variant-card">
                  <div className="ad-variant-header">
                    <span className="purple-tag">✉️ EMAIL NEWSLETTER</span>
                    <CopyButton id="em" copiedKey={copiedKey} onCopy={onCopy}
                      text={`Subject: ${email.subject_lines?.[0]}\n\n${email.body}\n\nCTA: ${email.cta}`} />
                  </div>
                  <div className="subject-line-options">
                    <span className="meta-label">SUBJECT LINE ALTERNATIVES (A/B TEST)</span>
                    {email.subject_lines?.map((subj, i) => (
                      <div key={i} className="subject-item-box">
                        <span>Option 0{i + 1}:</span> {subj}
                      </div>
                    ))}
                  </div>
                  <div className="email-preview-snippet-box">
                    <span className="meta-label">PREVIEW SNIPPET</span>
                    <p className="snippet-italic">{email.preview_text}</p>
                  </div>
                  <div className="email-body-container">
                    <span className="meta-label">EMAIL BODY</span>
                    <pre className="email-body-pre">{email.body}</pre>
                    <div className="email-cta-preview-button">{email.cta}</div>
                  </div>
                </div>
              </div>
            )}

            {outputTab === "calendar" && (
              <div className="tab-pane-view">
                <div className="calendar-card-grid">
                  {c.content_calendar_7day?.map((plan, i) => (
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

            {outputTab === "mockup" && <AdMockups />}
          </div>
        )}
      </div>
    </div>
  );
}
