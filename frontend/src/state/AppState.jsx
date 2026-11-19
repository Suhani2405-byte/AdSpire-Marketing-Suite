/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { api, apiError, streamCampaign } from "../api";

const AppContext = createContext(null);
export const useApp = () => useContext(AppContext);

const DEFAULT_FORM = {
  productName: "AeroPulse Pro Wireless",
  description:
    "Next-generation spatial audio wireless earbuds with 40-hour battery life, titanium build, and active environmental noise cancellation.",
  audience: "Tech professionals, commuters, and fitness enthusiasts aged 20-38",
  platform: "Instagram",
  goal: "Sales & Conversions",
  industry: "Consumer Electronics & D2C",
  tone: "Bold & Premium",
};

export function AppStateProvider({ user, settings, children }) {
  const canUse = (feature) => user.role === "admin" || settings?.[feature] !== false;
  const [activeTab, setActiveTab] = useState("studio");

  // ---- toast
  const [toast, setToast] = useState(null);
  const toastTimer = useRef(null);
  const triggerToast = useCallback((msg, ms = 3000) => {
    setToast(msg);
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), ms);
  }, []);

  // ---- campaign
  const [form, setForm] = useState(DEFAULT_FORM);
  const setField = (k, v) => setForm((f) => ({ ...f, [k]: v }));
  const [loading, setLoading] = useState(false);
  const [streamStatus, setStreamStatus] = useState("");
  const [streamText, setStreamText] = useState("");
  const [campaignResult, setCampaignResult] = useState(null);
  const [campaignMeta, setCampaignMeta] = useState(null); // {source, model, warning}
  const [currentCampaignId, setCurrentCampaignId] = useState(null);
  const abortRef = useRef(null);

  // ---- visuals
  const [visualPrompt, setVisualPrompt] = useState(
    "Editorial commercial photography of sleek matte-black titanium earbuds floating over black marble with neon cyber blue rim lighting"
  );
  const [visualStyle, setVisualStyle] = useState("Photorealistic");
  const [aspectRatio, setAspectRatio] = useState("1:1");
  const [visualMode, setVisualMode] = useState("auto"); // auto | photo | ai
  const [generatingVisual, setGeneratingVisual] = useState(false);
  const [renderedVisual, setRenderedVisual] = useState(null);
  const [visualMeta, setVisualMeta] = useState(null);
  const [visualError, setVisualError] = useState(null);

  // ---- library & brands
  const [savedCampaigns, setSavedCampaigns] = useState([]);
  const [brands, setBrands] = useState([]);

  const fetchSavedCampaigns = useCallback(async () => {
    try {
      const res = await api.get("/campaigns");
      setSavedCampaigns(res.data.campaigns || []);
    } catch (err) {
      console.error(err);
    }
  }, []);

  const fetchBrands = useCallback(async () => {
    try {
      const res = await api.get("/brands");
      setBrands(res.data.brands || []);
    } catch (err) {
      console.error(err);
    }
  }, []);

  useEffect(() => {
    fetchSavedCampaigns();
    fetchBrands();
  }, [fetchSavedCampaigns, fetchBrands]);

  // attachToCampaignId: when set, the generated image is saved onto that library campaign
  const handleGenerateVisual = async (customPrompt = null, attachToCampaignId = null) => {
    const promptToUse = (typeof customPrompt === "string" ? customPrompt : visualPrompt || "").trim();
    if (!promptToUse) {
      triggerToast("Please enter a visual description.");
      return;
    }
    setGeneratingVisual(true);
    setVisualError(null);
    try {
      const res = await api.post(
        "/image/generate",
        {
          prompt: promptToUse,
          aspect_ratio: aspectRatio,
          style: visualStyle,
          mode: visualMode,
          seed: Math.floor(Math.random() * 2_000_000_000), // new seed => new variation every click
        },
        { timeout: 240000 }
      );
      setRenderedVisual(res.data.image_url);
      setVisualMeta({
        provider: res.data.provider,
        style: res.data.style,
        aspect_ratio: res.data.aspect_ratio,
        notes: res.data.notes || [],
        verified: res.data.verified,
        subject: res.data.subject,
        simplified: res.data.simplified,
        logo: res.data.logo || null,
        kind: res.data.kind || "ai",
        attribution: res.data.attribution || null,
        resolution: res.data.resolution || null,
      });
      triggerToast(`🎨 Image generated with ${res.data.provider}`);
      if (attachToCampaignId) {
        api
          .put(`/campaigns/${attachToCampaignId}/image`, { image_url: res.data.image_url })
          .then(fetchSavedCampaigns)
          .catch((e) => console.error("Could not save image to campaign", e));
      }
    } catch (err) {
      console.error(err);
      const msg = apiError(err, "Image generation failed.");
      setVisualError(msg);
      triggerToast(msg.length > 140 ? msg.slice(0, 140) + "…" : msg, 7000);
    } finally {
      setGeneratingVisual(false);
    }
  };

  const handleGenerateCampaign = async () => {
    if (!form.productName.trim() || !form.description.trim()) {
      triggerToast("Please provide product name and description!");
      return;
    }
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    setStreamText("");
    setStreamStatus("Connecting to the AI strategist...");
    setRenderedVisual(null);
    setVisualMeta(null);
    setVisualError(null);
    try {
      const final = await streamCampaign(
        {
          product_name: form.productName,
          description: form.description,
          target_audience: form.audience,
          platform: form.platform,
          goal: form.goal,
          tone: form.tone,
          industry: form.industry,
        },
        (ev) => {
          if (ev.type === "status") setStreamStatus(ev.message);
          else if (ev.type === "chunk") setStreamText((t) => t + ev.text);
          else if (ev.type === "reset") setStreamText("");
        },
        controller.signal
      );

      setCampaignResult(final.campaign_content);
      setCampaignMeta({ source: final.source, model: final.model, warning: final.warning });
      setCurrentCampaignId(final.campaign_id || null);
      const imgPrompt = final.campaign_content?.image_prompt;
      if (imgPrompt) {
        setVisualPrompt(imgPrompt);
        if (canUse("image_generation")) handleGenerateVisual(imgPrompt, final.campaign_id);
      }
      if (final.source === "template") {
        triggerToast(`⚠ ${final.warning || "AI unavailable, generic template used."}`, 7000);
      } else {
        triggerToast("✨ Campaign ready!");
      }
      fetchSavedCampaigns();
    } catch (err) {
      if (err.name !== "AbortError") {
        console.error(err);
        triggerToast(err.message || "Campaign generation failed.", 6000);
      }
    } finally {
      setLoading(false);
      setStreamStatus("");
    }
  };

  const cancelGeneration = () => abortRef.current?.abort();

  const openedIdRef = useRef(null);
  const openSavedCampaign = (item) => {
    if (!item.campaign_content || typeof item.campaign_content !== "object") return;
    setCampaignResult(item.campaign_content);
    setCampaignMeta(item.source ? { source: item.source === "template" ? "template" : "gemini", model: item.source } : null);
    setCurrentCampaignId(item.id);
    setForm((f) => ({
      ...f,
      productName: item.product_name || "Campaign",
      audience: item.target_audience || f.audience,
      platform: item.platform || f.platform,
      goal: item.goal || f.goal,
    }));
    // Show this campaign's own image (or none) - never the previous campaign's.
    // The library list only carries a thumbnail, so the full-size image is fetched here.
    setRenderedVisual(item.image_thumb || null);
    setVisualMeta(null);
    setVisualError(null);
    if (item.campaign_content.image_prompt) setVisualPrompt(item.campaign_content.image_prompt);
    setActiveTab("studio");
    triggerToast(`Loaded: ${item.product_name}`);
    openedIdRef.current = item.id;
    if (item.has_image) {
      api
        .get(`/campaigns/${item.id}`)
        .then((res) => {
          // ignore the answer if the user opened another campaign meanwhile
          if (openedIdRef.current === item.id) setRenderedVisual(res.data.campaign?.image_url || null);
        })
        .catch((e) => console.error("Could not load full image", e));
    }
  };

  const deleteCampaign = async (id) => {
    try {
      await api.delete(`/campaigns/${id}`);
      if (id === currentCampaignId) setCurrentCampaignId(null);
      triggerToast("Campaign removed from library.");
      fetchSavedCampaigns();
    } catch (err) {
      triggerToast(apiError(err, "Could not delete campaign."));
    }
  };

  const copyText = async (content) => {
    try {
      await navigator.clipboard.writeText(typeof content === "object" ? JSON.stringify(content, null, 2) : String(content ?? ""));
      triggerToast("Copied to clipboard!");
      return true;
    } catch {
      triggerToast("Clipboard access was blocked by the browser.");
      return false;
    }
  };

  // ---- brands
  const applyBrand = (brand) => {
    setForm((f) => ({
      ...f,
      productName: brand.name || f.productName,
      description: brand.description || f.description,
      audience: brand.audience || f.audience,
      industry: brand.industry || f.industry,
      tone: brand.tone || f.tone,
    }));
    triggerToast(`Brand profile "${brand.name}" loaded`);
  };

  const saveBrandFromForm = async () => {
    const payload = {
      name: form.productName,
      description: form.description,
      audience: form.audience,
      industry: form.industry,
      tone: form.tone,
    };
    try {
      const existing = brands.find((b) => b.name.toLowerCase() === form.productName.trim().toLowerCase());
      if (existing) await api.put(`/brands/${existing.id}`, payload);
      else await api.post("/brands", payload);
      triggerToast(existing ? "Brand profile updated" : "Brand profile saved");
      fetchBrands();
    } catch (err) {
      triggerToast(apiError(err, "Could not save brand."));
    }
  };

  const deleteBrand = async (id) => {
    try {
      await api.delete(`/brands/${id}`);
      fetchBrands();
      triggerToast("Brand profile deleted");
    } catch (err) {
      triggerToast(apiError(err, "Could not delete brand."));
    }
  };

  const value = {
    user,
    settings,
    canUse,
    activeTab, setActiveTab,
    toast, triggerToast,
    form, setField,
    loading, streamStatus, streamText, cancelGeneration,
    campaignResult, campaignMeta, currentCampaignId,
    handleGenerateCampaign,
    visualPrompt, setVisualPrompt, visualStyle, setVisualStyle, aspectRatio, setAspectRatio, visualMode, setVisualMode,
    generatingVisual, renderedVisual, visualMeta, visualError, handleGenerateVisual,
    savedCampaigns, fetchSavedCampaigns, openSavedCampaign, deleteCampaign,
    brands, applyBrand, saveBrandFromForm, deleteBrand,
    copyText,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
