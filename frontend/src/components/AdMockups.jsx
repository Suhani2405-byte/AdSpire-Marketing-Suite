import React, { useState } from "react";
import { RefreshCw, Sparkles, ArrowRight, Heart, MessageCircle, Share2, Bookmark, Play, Volume2 } from "lucide-react";
import { useApp } from "../state/AppState";

const handleOf = (name) => (name || "brand").toLowerCase().replace(/[^a-z0-9]+/g, "_");

export default function AdMockups() {
  const { campaignResult: c, form, generatingVisual, renderedVisual, visualPrompt, currentCampaignId, handleGenerateVisual } = useApp();
  const [mockupType, setMockupType] = useState("instagram");
  const [isLiked, setIsLiked] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);

  const generate = () => handleGenerateVisual(c?.image_prompt || visualPrompt, currentCampaignId);
  const handle = handleOf(form.productName);
  const initial = (form.productName || "?").charAt(0);

  const media = (imgClass, spinnerClass, label) =>
    generatingVisual ? (
      <div className="media-placeholder-state">
        <RefreshCw size={26} className={`spin-animation ${spinnerClass}`} />
        <span>Generating ad creative...</span>
      </div>
    ) : renderedVisual ? (
      <img src={renderedVisual} alt="Campaign visual" className={imgClass} />
    ) : (
      <div className="media-placeholder-state">
        <Sparkles size={28} className="text-purple-400" />
        <span>Creative Visual Asset</span>
        <button className="sample-run-btn mini-btn" onClick={generate}>
          🎨 {label}
        </button>
      </div>
    );

  return (
    <div className="tab-pane-view flex-center-pane">
      <div className="mockup-platform-switcher">
        {[["instagram", "Instagram Feed Ad"], ["tiktok", "TikTok Video Reel"], ["linkedin", "LinkedIn Post"], ["google", "Google Search Ad"]].map(([id, label]) => (
          <button key={id} className={`platform-btn ${mockupType === id ? "active" : ""}`} onClick={() => setMockupType(id)}>
            {label}
          </button>
        ))}
      </div>

      {mockupType === "instagram" && (
        <div className="phone-device-frame">
          <div className="ig-feed-card">
            <div className="ig-top-header">
              <div className="ig-avatar-circle">{initial}</div>
              <div className="ig-user-info">
                <div className="ig-brand-handle">{handle}</div>
                <div className="ig-sponsored-label">Sponsored</div>
              </div>
            </div>
            <div className="ig-media-slot">{media("ig-media-img", "text-purple-400", "Generate Ad Photo")}</div>
            <div className="ig-cta-action-bar">
              <span>{c.ad_copies?.primary_ad?.cta || "Shop Now"}</span>
              <ArrowRight size={14} />
            </div>
            <div className="ig-interaction-icons">
              <div className="left-icons">
                <button className={`icon-btn ${isLiked ? "liked" : ""}`} onClick={() => setIsLiked(!isLiked)}>
                  <Heart size={20} fill={isLiked ? "#ef4444" : "none"} />
                </button>
                <button className="icon-btn"><MessageCircle size={20} /></button>
                <button className="icon-btn"><Share2 size={20} /></button>
              </div>
              <button className={`icon-btn ${isBookmarked ? "bookmarked" : ""}`} onClick={() => setIsBookmarked(!isBookmarked)}>
                <Bookmark size={20} fill={isBookmarked ? "#fff" : "none"} />
              </button>
            </div>
            <div className="ig-caption-container">
              <strong>{handle}</strong> {c.social_posts?.instagram?.caption?.slice(0, 140)}...
            </div>
          </div>
        </div>
      )}

      {mockupType === "tiktok" && (
        <div className="phone-device-frame tiktok-reel-frame">
          <div className="tt-player-screen">
            {generatingVisual ? (
              <div className="tt-video-placeholder">
                <RefreshCw size={32} className="spin-animation text-pink-400" />
              </div>
            ) : renderedVisual ? (
              <img src={renderedVisual} alt="TikTok background" className="tt-media-video-img" />
            ) : (
              <div className="tt-video-placeholder">
                <Play size={40} className="text-pink-400" />
                <button className="sample-run-btn mini-btn" onClick={generate}>🎨 Generate Visual</button>
              </div>
            )}
            <div className="tt-overlay-hud">
              <div className="tt-action-column">
                <div className="tt-hud-btn" onClick={() => setIsLiked(!isLiked)}>
                  <Heart size={24} fill={isLiked ? "#ef4444" : "#fff"} color={isLiked ? "#ef4444" : "#fff"} />
                </div>
                <div className="tt-hud-btn"><MessageCircle size={24} /></div>
                <div className="tt-hud-btn"><Share2 size={24} /></div>
              </div>
              <div className="tt-bottom-details">
                <div className="tt-handle">@{handle}</div>
                <p className="tt-script-snippet">{c.social_posts?.tiktok_script?.voiceover?.slice(0, 85)}...</p>
                <div className="tt-audio-strip">
                  <Volume2 size={13} />
                  <span>{c.social_posts?.tiktok_script?.audio_recommendation || "Trending audio"}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {mockupType === "linkedin" && (
        <div className="desktop-card-frame">
          <div className="linkedin-card-box">
            <div className="li-user-head">
              <div className="li-avatar-square">{initial}</div>
              <div>
                <div className="li-company-title">{form.productName}</div>
                <div className="li-subtext">Promoted</div>
              </div>
            </div>
            <p className="li-body-copy">{c.social_posts?.linkedin?.post || c.executive_summary}</p>
            <div className="li-banner-slot">
              {generatingVisual ? (
                <div className="li-placeholder-box">
                  <RefreshCw size={24} className="spin-animation text-blue-400" />
                </div>
              ) : renderedVisual ? (
                <img src={renderedVisual} alt="Banner" className="li-banner-img" />
              ) : (
                <div className="li-placeholder-box">
                  <h4>{c.campaign_title}</h4>
                  <p>{c.tagline}</p>
                  <button className="sample-run-btn mini-btn" onClick={generate}>🎨 Generate Banner</button>
                </div>
              )}
            </div>
            <div className="li-cta-button-strip">
              <span>{c.ad_copies?.primary_ad?.cta || "Learn More"}</span>
            </div>
          </div>
        </div>
      )}

      {mockupType === "google" && (
        <div className="desktop-card-frame">
          <div className="google-serp-card">
            <div className="google-ad-badge">Sponsored • www.{(form.productName || "brand").toLowerCase().replace(/[^a-z0-9]+/g, "")}.com</div>
            <div className="google-title-link">{c.ad_copies?.variant_a?.headline || c.campaign_title}</div>
            <div className="google-description-text">
              {c.tagline} {c.value_propositions?.slice(0, 2).join(". ")}
            </div>
            <div className="google-sitelinks-row">
              <span>Shop Now</span>
              <span>Key Features</span>
              <span>Reviews</span>
              <span>Offers</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
