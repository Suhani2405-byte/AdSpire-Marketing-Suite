import os
import json
import re
import time
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

# Check if google-genai is available
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def _clean_json_string(raw_text: str) -> str:
    """Extract and clean JSON content from model response."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def generate_fallback_campaign(product_name, description, audience, platform, goal):
    """Fallback campaign generator in case of network/quota issues during demo."""
    return {
        "campaign_title": f"{product_name} - Unleash Your Potential",
        "tagline": f"The Smarter Way to Experience {product_name}",
        "executive_summary": f"A targeted, multi-touchpoint marketing campaign designed to maximize {goal.lower()} for {audience} through persuasive storytelling and high-converting creative angles.",
        "target_persona": {
            "name": f"The Ambitious {audience.split()[0] if audience else 'Consumer'}",
            "demographics": audience or "Digital Natives, 22-45",
            "core_desires": [
                "Efficiency and saving time",
                "High quality without friction",
                "Modern, trustworthy solutions"
            ],
            "pain_points": [
                "Overwhelmed by complex or outdated alternatives",
                "Lack of reliable results from current products",
                "Needs seamless integration into daily routine"
            ],
            "objections_busting": f"Highlights the unmatched simplicity and proven benefits of {product_name}."
        },
        "value_propositions": [
            f"Tailored specifically for {audience or 'modern users'}",
            "Engineered for maximum reliability and ease of use",
            "Instant impact with demonstrable results"
        ],
        "ad_copies": {
            "primary_ad": {
                "hook": f"Stop settling for less. Discover {product_name}.",
                "body": f"{description}\n\nDesigned specifically for {audience}, {product_name} delivers unmatched performance so you can focus on what truly matters.",
                "cta": "Get Started Today →",
                "platform": platform or "Instagram"
            },
            "variant_a": {
                "angle": "Direct Benefit & Speed",
                "headline": f"Transform Your Workflow with {product_name}",
                "hook": f"What if you could solve your biggest bottlenecks today?",
                "hypothesis": "Focuses on immediate gratification and measurable time saved."
            },
            "variant_b": {
                "angle": "Social Proof & FOMO",
                "headline": f"Why Everyone is Switching to {product_name}",
                "hook": f"Don't get left behind using outdated tools.",
                "hypothesis": "Appeals to curiosity and peer validation."
            }
        },
        "social_posts": {
            "instagram": {
                "caption": f"✨ Introducing {product_name}! ✨\n\n{description}\n\n🎯 Perfect for {audience}.\n👇 Tap the link in bio to claim your exclusive early-bird offer!",
                "hashtags": [f"#{product_name.replace(' ', '')}", "#Innovation", "#Growth", "#Trending", "#Productivity"],
                "visual_concept": f"Clean aesthetic shot of {product_name} in a modern workspace environment with vibrant lighting."
            },
            "linkedin": {
                "post": f"🚀 Exciting announcement: Introducing {product_name}.\n\nIn today's fast-paced environment, {audience} need solutions that actually deliver.\n\nKey advantages:\n• Streamlined experience\n• Proven results\n• Built for scale\n\nHow is your team tackling this challenge? Let's discuss in the comments.",
                "professional_takeaway": "Focus on ROI, scalability, and measurable competitive edge."
            },
            "twitter_x": {
                "hook_tweet": f"1/5 Most people struggle with this every single day. Here is how {product_name} changes the game 🧵👇",
                "thread": [
                    f"2/5 The problem: Traditional solutions are slow and built for yesterday's workflows.",
                    f"3/5 {product_name} fixes this by offering: {description[:100]}...",
                    f"4/5 Built specifically for {audience} who demand performance.",
                    f"5/5 Try it today and experience the difference for yourself."
                ]
            },
            "tiktok_script": {
                "duration": "20 seconds",
                "hook_visual": "Fast-paced zoom-in on the common struggle before cutting to the solution.",
                "voiceover": f"If you're part of {audience}, stop scrolling! Here's the secret tool everyone is talking about...",
                "scene_breakdown": [
                    "0-3s: Hook - 'You need to see this.'",
                    "3-12s: Showcase the product solving the main pain point.",
                    "12-20s: Strong CTA - 'Check link in bio before it sells out!'"
                ],
                "audio_recommendation": "Trending upbeat electronic / lo-fi beats"
            }
        },
        "email_newsletter": {
            "subject_lines": [
                f"Meet {product_name}: The upgrade you've been waiting for",
                f"How {audience} are saving hours each week with {product_name}",
                f"Inside: Exclusive access to {product_name}"
            ],
            "preview_text": f"Discover how {product_name} simplifies your daily routine.",
            "body": f"Hi there,\n\nWe built {product_name} with one clear mission: to give {audience} the ultimate advantage.\n\n{description}\n\nReady to see what it can do for you?",
            "cta": f"Explore {product_name} Now"
        },
        "content_calendar_7day": [
            {"day": "Day 1", "channel": "Instagram / TikTok", "content_type": "Teaser & Problem Hook", "idea": f"Highlight the top frustration faced by {audience}."},
            {"day": "Day 2", "channel": "LinkedIn", "content_type": "Founder Story / USP", "idea": f"Why we built {product_name} and what makes it different."},
            {"day": "Day 3", "channel": "Email Newsletter", "content_type": "Feature Deep Dive", "idea": "Step-by-step walkthrough of core product benefits."},
            {"day": "Day 4", "channel": "Twitter / X Thread", "content_type": "Value Thread", "idea": "5 tips for productivity, showcasing the product naturally."},
            {"day": "Day 5", "channel": "Instagram Story & Poll", "content_type": "Interactive Q&A", "idea": "Engage followers with before/after comparisons."},
            {"day": "Day 6", "channel": "TikTok / Reels", "content_type": "Social Proof", "idea": "Live reaction and user demo."},
            {"day": "Day 7", "channel": "Omnichannel", "content_type": "Limited Time Offer CTA", "idea": "Final push with special discount code."}
        ],
        "image_prompt": f"Professional commercial product photography of {product_name}, modern minimalist aesthetic, sleek studio lighting, 8k resolution, elegant hyperrealistic depth of field, vibrant colors, premium branding presentation.",
        "budget_recommendations": {
            "suggested_split": {
                "Meta (IG/FB)": "40%",
                "Google Search": "25%",
                "TikTok Ads": "20%",
                "Email/Retargeting": "15%"
            },
            "expected_cpc": "$0.85 - $1.40",
            "expected_ctr": "2.4% - 3.8%"
        }
    }


# Ordered by preference. Several Gemini models regularly return 503 "high demand",
# so the list ends with lighter models that are usually available.
TEXT_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
    "gemini-flash-latest",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
]

REQUIRED_KEYS = ("campaign_title", "tagline", "ad_copies", "social_posts", "image_prompt")

# model -> time until which it is skipped after a 503/429/404, so every request
# doesn't waste seconds re-trying a model that is known to be down right now
_model_cooldown = {}
_MODEL_COOLDOWN_SECONDS = 120


def _available_models():
    now = time.time()
    models = [m for m in TEXT_MODELS if _model_cooldown.get(m, 0) <= now]
    return models or list(TEXT_MODELS)


def _mark_down(model, msg):
    m = msg.lower()
    if any(k in m for k in ("503", "unavailable", "429", "resource_exhausted", "404", "not_found")):
        _model_cooldown[model] = time.time() + _MODEL_COOLDOWN_SECONDS


def build_campaign_prompt(product_name, description, audience, platform, goal, tone, industry):
    return f"""
You are MarketAI, an elite Autonomous Marketing Director and Chief Marketing Officer.
Generate a comprehensive, world-class marketing campaign strategy and multi-platform creative suite for the following product:

Product Name: {product_name}
Description: {description}
Target Audience: {audience or "Not specified - infer the most likely buyers"}
Industry: {industry or "Not specified"}
Primary Platform: {platform}
Campaign Goal: {goal}
Brand Tone of Voice: {tone}

Write every piece of copy in the "{tone}" tone and make it specific to this exact product
(use its real features from the description; do not write generic filler).

You MUST return STRICT JSON adhering precisely to the following structure with zero markdown or conversational text outside the JSON:

{{
  "campaign_title": "Catchy and memorable campaign title",
  "tagline": "Powerful 1-sentence tagline / hook",
  "executive_summary": "2-3 sentences summarizing the strategic marketing angle",
  "target_persona": {{
    "name": "Persona Name/Title (e.g. Modern Professional Maya)",
    "demographics": "Age, occupation, location, mindset",
    "core_desires": ["Desire 1", "Desire 2", "Desire 3"],
    "pain_points": ["Pain point 1", "Pain point 2", "Pain point 3"],
    "objections_busting": "Key message that overcomes customer doubt"
  }},
  "value_propositions": ["USP 1", "USP 2", "USP 3"],
  "ad_copies": {{
    "primary_ad": {{
      "hook": "Attention grabbing opening hook",
      "body": "Persuasive ad body copy highlighting benefits",
      "cta": "Actionable Call To Action",
      "platform": "{platform}"
    }},
    "variant_a": {{
      "angle": "Direct Benefit / Problem Solution",
      "headline": "Variant A Headline",
      "hook": "Variant A Hook",
      "hypothesis": "Conversion hypothesis for Variant A"
    }},
    "variant_b": {{
      "angle": "Social Proof / Storytelling / Curiosity",
      "headline": "Variant B Headline",
      "hook": "Variant B Hook",
      "hypothesis": "Conversion hypothesis for Variant B"
    }}
  }},
  "social_posts": {{
    "instagram": {{
      "caption": "Full Instagram caption with line breaks and strategic emoji usage",
      "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
      "visual_concept": "Description of the visual carousel/post"
    }},
    "linkedin": {{
      "post": "Thought leadership and professional value proposition post",
      "professional_takeaway": "Key B2B / career value insight"
    }},
    "twitter_x": {{
      "hook_tweet": "Viral-style opening tweet",
      "thread": ["Tweet 2", "Tweet 3", "Tweet 4", "Tweet 5 with CTA"]
    }},
    "tiktok_script": {{
      "duration": "15-30 seconds",
      "hook_visual": "Visual cue for the first 3 seconds",
      "voiceover": "Full spoken voiceover script",
      "scene_breakdown": ["0-3s: Hook", "3-15s: Problem/Solution", "15-30s: CTA"],
      "audio_recommendation": "Suggested audio style or trending sound archetype"
    }}
  }},
  "email_newsletter": {{
    "subject_lines": ["Subject Option 1", "Subject Option 2 (High Open Rate)", "Subject Option 3 (Curiosity)"],
    "preview_text": "Short inbox preview snippet",
    "body": "Engaging email copy with greeting, story/value, and clear offer",
    "cta": "Email button CTA text"
  }},
  "content_calendar_7day": [
    {{"day": "Day 1", "channel": "Channel", "content_type": "Type", "idea": "Post idea"}},
    {{"day": "Day 2", "channel": "Channel", "content_type": "Type", "idea": "Post idea"}},
    {{"day": "Day 3", "channel": "Channel", "content_type": "Type", "idea": "Post idea"}},
    {{"day": "Day 4", "channel": "Channel", "content_type": "Type", "idea": "Post idea"}},
    {{"day": "Day 5", "channel": "Channel", "content_type": "Type", "idea": "Post idea"}},
    {{"day": "Day 6", "channel": "Channel", "content_type": "Type", "idea": "Post idea"}},
    {{"day": "Day 7", "channel": "Channel", "content_type": "Type", "idea": "Post idea"}}
  ],
  "image_prompt": "A 40-70 word text-to-image prompt. It MUST start by literally describing the physical product ({product_name}) - its type, shape, colors, materials - as the clear hero subject, then the setting, lighting and camera angle. No brand logos, no text in the image.",
  "budget_recommendations": {{
    "suggested_split": {{
      "Meta (Instagram & Facebook)": "40%",
      "Google Search / Performance Max": "30%",
      "TikTok / Short Video": "20%",
      "Email & Retargeting": "10%"
    }},
    "expected_cpc": "Estimated CPC range (e.g. $0.65 - $1.20)",
    "expected_ctr": "Estimated CTR range (e.g. 2.5% - 4.1%)"
  }}
}}
"""


def _template_result(product_name, description, audience, platform, goal, warning):
    return {
        "type": "done",
        "campaign": generate_fallback_campaign(product_name, description, audience, platform, goal),
        "meta": {"source": "template", "model": None, "warning": warning},
    }


def stream_marketing_campaign(product_name, description, audience, platform="Instagram",
                              goal="Brand Awareness", tone="Bold & Premium", industry=""):
    """
    Generator of progress events for a campaign:
      {"type": "status", "message": str}
      {"type": "chunk",  "text": str}          raw JSON text as Gemini writes it
      {"type": "reset"}                        a model failed mid-stream; discard chunks so far
      {"type": "done",   "campaign": dict, "meta": {...}}   always the last event
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not GENAI_AVAILABLE:
        yield _template_result(product_name, description, audience, platform, goal,
                               "GEMINI_API_KEY is not configured, so a generic template was used.")
        return

    prompt = build_campaign_prompt(product_name, description, audience, platform, goal, tone, industry)
    # 60s timeout: an overloaded model that stalls is abandoned and the next one is tried
    client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=60_000))
    config = types.GenerateContentConfig(response_mime_type="application/json", temperature=0.7)

    for model_name in _available_models():
        yield {"type": "status", "message": f"Writing campaign with {model_name}..."}
        text_parts = []
        try:
            print(f"[GeminiService] Streaming from {model_name}...")
            for chunk in client.models.generate_content_stream(model=model_name, contents=prompt, config=config):
                piece = chunk.text or ""
                if piece:
                    text_parts.append(piece)
                    yield {"type": "chunk", "text": piece}

            parsed = json.loads(_clean_json_string("".join(text_parts)))
            if not isinstance(parsed, dict) or not all(k in parsed for k in REQUIRED_KEYS):
                raise ValueError("response JSON is missing required campaign fields")
            print(f"[GeminiService] Campaign generated via {model_name}")
            yield {"type": "done", "campaign": parsed,
                   "meta": {"source": "gemini", "model": model_name, "warning": None}}
            return
        except Exception as e:
            msg = str(e)
            print(f"[GeminiService] Error with {model_name}: {msg[:200]}")
            _mark_down(model_name, msg)
            if text_parts:
                yield {"type": "reset"}
            yield {"type": "status", "message": f"{model_name} unavailable, trying another model..."}

    print("[GeminiService] All Gemini models failed. Falling back to template generation.")
    yield _template_result(product_name, description, audience, platform, goal,
                           "All Gemini models were unavailable (overloaded or quota), so a generic "
                           "template was used. Try again in a minute.")


def generate_marketing_campaign(product_name, description, audience, platform="Instagram",
                                goal="Brand Awareness", tone="Bold & Premium", industry=""):
    """Non-streaming wrapper. Returns (campaign_dict, meta)."""
    for event in stream_marketing_campaign(product_name, description, audience, platform, goal, tone, industry):
        if event["type"] == "done":
            return event["campaign"], event["meta"]
    raise RuntimeError("campaign generator ended without a result")
