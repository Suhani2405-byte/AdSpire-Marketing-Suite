// Campaign export helpers: JSON, Markdown and print-to-PDF.

const slug = (s) => (s || "campaign").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");

function download(filename, content, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

const esc = (s) =>
  String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

const list = (items) => (Array.isArray(items) ? items : []);

export function exportJSON(campaign, productName) {
  download(`${slug(productName)}_campaign.json`, JSON.stringify(campaign, null, 2), "application/json");
}

export function campaignToMarkdown(c, productName) {
  const p = c.target_persona || {};
  const ads = c.ad_copies || {};
  const s = c.social_posts || {};
  const em = c.email_newsletter || {};
  const out = [];
  out.push(`# ${c.campaign_title || productName}`, "", `> ${c.tagline || ""}`, "", c.executive_summary || "", "");
  out.push("## Target persona", `**${p.name || ""}** - ${p.demographics || ""}`, "");
  out.push("**Desires**", ...list(p.core_desires).map((d) => `- ${d}`), "");
  out.push("**Pain points**", ...list(p.pain_points).map((d) => `- ${d}`), "");
  if (p.objections_busting) out.push(`**Objection buster:** ${p.objections_busting}`, "");
  out.push("## Value propositions", ...list(c.value_propositions).map((v) => `- ${v}`), "");
  if (ads.primary_ad) {
    out.push("## Primary ad", `**${ads.primary_ad.hook || ""}**`, "", ads.primary_ad.body || "", "", `CTA: ${ads.primary_ad.cta || ""}`, "");
  }
  for (const [k, label] of [["variant_a", "Variant A"], ["variant_b", "Variant B"]]) {
    const v = ads[k];
    if (v) out.push(`### ${label} (${v.angle || ""})`, `**${v.headline || ""}**`, v.hook || "", `_Hypothesis: ${v.hypothesis || ""}_`, "");
  }
  if (s.instagram) out.push("## Instagram", s.instagram.caption || "", "", list(s.instagram.hashtags).join(" "), "");
  if (s.linkedin) out.push("## LinkedIn", s.linkedin.post || "", "");
  if (s.twitter_x) out.push("## X / Twitter", s.twitter_x.hook_tweet || "", ...list(s.twitter_x.thread), "");
  if (s.tiktok_script) {
    const t = s.tiktok_script;
    out.push(`## TikTok / Reels script (${t.duration || ""})`, `**Hook:** ${t.hook_visual || ""}`, `**Voiceover:** ${t.voiceover || ""}`,
      ...list(t.scene_breakdown).map((x) => `- ${x}`), `**Audio:** ${t.audio_recommendation || ""}`, "");
  }
  if (em.body) {
    out.push("## Email", "**Subject lines**", ...list(em.subject_lines).map((x) => `- ${x}`), "", `_Preview: ${em.preview_text || ""}_`, "", em.body, "", `CTA: ${em.cta || ""}`, "");
  }
  if (list(c.content_calendar_7day).length) {
    out.push("## 7-day content calendar", "| Day | Channel | Type | Idea |", "|---|---|---|---|",
      ...c.content_calendar_7day.map((d) => `| ${d.day} | ${d.channel} | ${d.content_type} | ${String(d.idea || "").replace(/\|/g, "/")} |`), "");
  }
  if (c.image_prompt) out.push("## Image prompt", c.image_prompt, "");
  return out.join("\n");
}

export function exportMarkdown(campaign, productName) {
  download(`${slug(productName)}_campaign.md`, campaignToMarkdown(campaign, productName), "text/markdown");
}

/** Opens a clean printable page; the browser's print dialog can "Save as PDF". */
export function exportPDF(c, productName, imageUrl) {
  const w = window.open("", "_blank");
  if (!w) return false;
  const p = c.target_persona || {};
  const ads = c.ad_copies || {};
  const s = c.social_posts || {};
  const em = c.email_newsletter || {};
  const ul = (items) => `<ul>${list(items).map((x) => `<li>${esc(x)}</li>`).join("")}</ul>`;
  const pre = (t) => `<p class="pre">${esc(t)}</p>`;

  w.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>${esc(c.campaign_title || productName)}</title>
<style>
 body{font-family:Georgia,serif;color:#1e1b2e;max-width:760px;margin:32px auto;padding:0 24px;line-height:1.55}
 h1{font-size:28px;margin:0 0 4px} h2{font-size:18px;border-bottom:2px solid #8b5cf6;padding-bottom:4px;margin-top:28px}
 h3{font-size:15px;margin:16px 0 4px} .tag{color:#6d28d9;font-style:italic;font-size:17px}
 .pre{white-space:pre-wrap} img{max-width:100%;border-radius:8px;margin:12px 0}
 table{border-collapse:collapse;width:100%;font-size:13px} td,th{border:1px solid #ccc;padding:6px;text-align:left;vertical-align:top}
 .meta{color:#555;font-size:12px} @media print{body{margin:0}}
</style></head><body>
<p class="meta">${esc(productName)} &middot; Generated with Adspire &middot; ${new Date().toLocaleDateString()}</p>
<h1>${esc(c.campaign_title)}</h1><p class="tag">&ldquo;${esc(c.tagline)}&rdquo;</p><p>${esc(c.executive_summary)}</p>
${imageUrl ? `<img src="${esc(imageUrl)}" alt="Campaign visual">` : ""}
<h2>Target persona</h2><p><b>${esc(p.name)}</b> &mdash; ${esc(p.demographics)}</p>
<h3>Core desires</h3>${ul(p.core_desires)}<h3>Pain points</h3>${ul(p.pain_points)}
${p.objections_busting ? `<p><b>Objection buster:</b> ${esc(p.objections_busting)}</p>` : ""}
<h2>Value propositions</h2>${ul(c.value_propositions)}
${ads.primary_ad ? `<h2>Primary ad</h2><p><b>${esc(ads.primary_ad.hook)}</b></p>${pre(ads.primary_ad.body)}<p><b>CTA:</b> ${esc(ads.primary_ad.cta)}</p>` : ""}
${["variant_a", "variant_b"].filter((k) => ads[k]).map((k) => `<h3>${k === "variant_a" ? "Variant A" : "Variant B"} (${esc(ads[k].angle)})</h3><p><b>${esc(ads[k].headline)}</b><br>${esc(ads[k].hook)}</p><p><i>${esc(ads[k].hypothesis)}</i></p>`).join("")}
${s.instagram ? `<h2>Instagram</h2>${pre(s.instagram.caption)}<p>${esc(list(s.instagram.hashtags).join(" "))}</p>` : ""}
${s.linkedin ? `<h2>LinkedIn</h2>${pre(s.linkedin.post)}` : ""}
${s.tiktok_script ? `<h2>TikTok / Reels script</h2><p><b>Hook:</b> ${esc(s.tiktok_script.hook_visual)}</p><p><b>Voiceover:</b> ${esc(s.tiktok_script.voiceover)}</p>${ul(s.tiktok_script.scene_breakdown)}` : ""}
${em.body ? `<h2>Email</h2><h3>Subject lines</h3>${ul(em.subject_lines)}${pre(em.body)}<p><b>CTA:</b> ${esc(em.cta)}</p>` : ""}
${list(c.content_calendar_7day).length ? `<h2>7-day content calendar</h2><table><tr><th>Day</th><th>Channel</th><th>Type</th><th>Idea</th></tr>${c.content_calendar_7day.map((d) => `<tr><td>${esc(d.day)}</td><td>${esc(d.channel)}</td><td>${esc(d.content_type)}</td><td>${esc(d.idea)}</td></tr>`).join("")}</table>` : ""}
<script>window.onload=()=>setTimeout(()=>window.print(),300)</script>
</body></html>`);
  w.document.close();
  return true;
}
