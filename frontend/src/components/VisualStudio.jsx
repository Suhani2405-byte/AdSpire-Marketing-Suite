import React, { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { Image as ImageIcon, RefreshCw, Download, X, Maximize2 } from "lucide-react";
import { useApp } from "../state/AppState";

const STYLES = ["Photorealistic", "3D Render", "Cyberpunk", "Minimalist", "Luxury", "Vibrant Pop"];
const RATIOS = [
  { id: "1:1", label: "1:1 Square (Feed)" },
  { id: "16:9", label: "16:9 Banner" },
  { id: "9:16", label: "9:16 Story" },
];
const MODES = [
  { id: "auto", label: "Auto", help: "Real photo for brand-name products (JBL, Sony, Nike…), AI for everything else" },
  { id: "photo", label: "Real Photo", help: "Search licensed HD photos of the exact product, checked by AI" },
  { id: "ai", label: "AI Generate", help: "Create a new image from your description" },
];
const TEMPLATES = [
  "Portable bluetooth speaker on a wooden desk",
  "Matte-black wireless earbuds with charging case",
  "Luxury chronograph wristwatch on dark stone",
  "Red running shoes on a wet track",
  "Glass perfume bottle with gold cap",
  "Amber skincare serum dropper bottle",
];

async function downloadImage(url, triggerToast) {
  try {
    const blob = await (await fetch(url)).blob();
    const ext = (blob.type.split("/")[1] || "jpg").replace("jpeg", "jpg");
    const href = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = href;
    a.download = `adspire_asset_${Date.now()}.${ext}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(href), 1000);
    triggerToast("Image downloaded!");
  } catch {
    window.open(url, "_blank");
  }
}

export default function VisualStudio() {
  const {
    visualPrompt, setVisualPrompt, visualStyle, setVisualStyle, aspectRatio, setAspectRatio, visualMode, setVisualMode,
    generatingVisual, renderedVisual, visualMeta, visualError, handleGenerateVisual,
    campaignResult, triggerToast,
  } = useApp();
  const [zoomed, setZoomed] = useState(false);

  // full-screen viewer: close with Esc, and never stay open for an image that is gone
  useEffect(() => {
    if (!zoomed) return undefined;
    const onKey = (e) => e.key === "Escape" && setZoomed(false);
    window.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [zoomed]);
  useEffect(() => {
    if (!renderedVisual || generatingVisual) setZoomed(false);
  }, [renderedVisual, generatingVisual]);

  const shownRatio = visualMeta?.aspect_ratio || aspectRatio;

  return (
    <div className="visual-studio-container">
      <div className="studio-hero-center">
        <div className="hero-top-badge">
          <ImageIcon size={14} /> AI VISUAL GENERATOR
        </div>
        <h2>Advertising Visuals From Your Prompt</h2>
        <p>Describe exactly what you want to see. Each click generates a new variation.</p>
      </div>

      <div className="campaign-studio-grid">
        <div className="studio-card">
          <div className="card-top-header">
            <h3>Visual Asset Controls</h3>
          </div>

          <div className="custom-form-group">
            <label>CREATIVE PROMPT</label>
            <textarea
              rows={5}
              value={visualPrompt}
              maxLength={2000}
              onChange={(e) => setVisualPrompt(e.target.value)}
              placeholder="Describe the subject, setting, lighting and camera angle..."
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

          <div className="custom-form-group mt-2">
            <label>IMAGE SOURCE</label>
            <div className="style-preset-grid mode-grid">
              {MODES.map((m) => (
                <button key={m.id} type="button" title={m.help} className={`style-chip-btn ${visualMode === m.id ? "active" : ""}`} onClick={() => setVisualMode(m.id)}>
                  {m.label}
                </button>
              ))}
            </div>
          </div>

          <div className="custom-form-group mt-2">
            <label>QUICK TEMPLATES</label>
            <div className="template-pill-row">
              {TEMPLATES.map((item) => (
                <button key={item} type="button" className="template-pill" onClick={() => setVisualPrompt(item)}>
                  + {item}
                </button>
              ))}
            </div>
          </div>

          <div className="custom-form-group mt-3">
            <label>STYLE PRESET</label>
            <div className="style-preset-grid">
              {STYLES.map((st) => (
                <button key={st} className={`style-chip-btn ${visualStyle === st ? "active" : ""}`} onClick={() => setVisualStyle(st)}>
                  {st}
                </button>
              ))}
            </div>
          </div>

          <div className="custom-form-group mt-3">
            <label>ASPECT RATIO</label>
            <div className="ratio-selector-grid">
              {RATIOS.map((asp) => (
                <button key={asp.id} className={`ratio-btn ${aspectRatio === asp.id ? "active" : ""}`} onClick={() => setAspectRatio(asp.id)}>
                  {asp.label}
                </button>
              ))}
            </div>
          </div>

          <button className="action-btn-glow mt-4" onClick={() => handleGenerateVisual()} disabled={generatingVisual}>
            {generatingVisual ? (
              <>
                <RefreshCw size={18} className="spin-animation" />
                <span>Generating Visual...</span>
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
              <h3>Generating your visual...</h3>
              <p>Generating and checking the image. This usually takes 15-90 seconds.</p>
            </div>
          ) : visualError && !renderedVisual ? (
            <div className="empty-workspace-state">
              <div className="empty-visual-circle">
                <ImageIcon size={36} className="text-purple-400" />
              </div>
              <h3>Image generation failed</h3>
              <p style={{ whiteSpace: "pre-wrap" }}>{visualError}</p>
            </div>
          ) : renderedVisual ? (
            <div className="visual-render-preview-wrapper">
              <div
                className="visual-image-frame"
                style={{
                  aspectRatio: shownRatio === "16:9" ? "16 / 9" : shownRatio === "9:16" ? "9 / 16" : "1 / 1",
                  maxWidth: shownRatio === "9:16" ? "320px" : "480px",
                }}
              >
                <img
                  src={renderedVisual}
                  alt="Generated visual"
                  title="Click to view full size"
                  onClick={() => setZoomed(true)}
                  className={`rendered-asset-img zoomable ${visualMeta?.kind === "photo" ? "contain" : ""}`}
                />
                <button type="button" className="zoom-hint" title="View full size" onClick={() => setZoomed(true)}>
                  <Maximize2 size={15} />
                </button>
                <div className="visual-download-overlay">
                  <button type="button" onClick={() => downloadImage(renderedVisual, triggerToast)} className="download-asset-pill">
                    <Download size={16} /> Download
                  </button>
                  <button type="button" onClick={() => handleGenerateVisual()} className="download-asset-pill alt">
                    <RefreshCw size={16} /> Regenerate
                  </button>
                </div>
              </div>
              {/* rendered into <body>: the panel's backdrop-filter would otherwise trap a fixed overlay inside it */}
              {zoomed && createPortal(
                <div className="lightbox" role="dialog" aria-modal="true" aria-label="Full size image" onClick={() => setZoomed(false)}>
                  <img src={renderedVisual} alt="Generated visual, full size" className="lightbox-img" onClick={(e) => e.stopPropagation()} />
                  <div className="lightbox-actions" onClick={(e) => e.stopPropagation()}>
                    <button type="button" className="download-asset-pill" onClick={() => downloadImage(renderedVisual, triggerToast)}>
                      <Download size={16} /> Download
                    </button>
                    <button type="button" className="download-asset-pill" onClick={() => setZoomed(false)}>
                      <X size={16} /> Close
                    </button>
                  </div>
                  <button type="button" className="lightbox-close" aria-label="Close" onClick={() => setZoomed(false)}>
                    <X size={22} />
                  </button>
                </div>,
                document.body
              )}
              {visualMeta?.attribution?.source === "Unsplash" ? (
                <p className="photo-credit">
                  Photo by{" "}
                  <a href={visualMeta.attribution.creator_url || visualMeta.attribution.page_url} target="_blank" rel="noreferrer">
                    {visualMeta.attribution.creator}
                  </a>{" "}
                  on{" "}
                  <a href="https://unsplash.com/?utm_source=adspire&utm_medium=referral" target="_blank" rel="noreferrer">Unsplash</a>
                </p>
              ) : visualMeta?.attribution && (
                <p className="photo-credit">
                  Photo: “{visualMeta.attribution.title}” by {visualMeta.attribution.creator} ·{" "}
                  {visualMeta.attribution.license_url ? (
                    <a href={visualMeta.attribution.license_url} target="_blank" rel="noreferrer">{visualMeta.attribution.license}</a>
                  ) : visualMeta.attribution.license}{" "}
                  · {visualMeta.attribution.page_url ? <a href={visualMeta.attribution.page_url} target="_blank" rel="noreferrer">source</a> : visualMeta.attribution.source}
                  {!visualMeta.attribution.commercial_ok && <strong className="nc-warning"> · Non-commercial licence: fine for demos, not for paid ads</strong>}
                </p>
              )}
            </div>
          ) : (
            <div className="empty-workspace-state">
              <div className="empty-visual-circle">
                <ImageIcon size={36} className="text-purple-400" />
              </div>
              <h3>Visual Canvas Idle</h3>
              <p>Enter your creative description and click Generate.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
