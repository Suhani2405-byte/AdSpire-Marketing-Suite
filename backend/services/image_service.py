"""
AI image generation service.

Every image returned here is generated from the user's actual prompt by a real
text-to-image model. Providers are tried in order of output quality:

  1. Google Gemini image models  (GEMINI_API_KEY, needs image quota / billing)
  2. Hugging Face FLUX.1-schnell (HF_TOKEN, needs inference credits)
  3. Pollinations                (free: ~768px, watermark, 1 image / 45s per IP;
                                  set POLLINATIONS_API_KEY for the full endpoint)

A provider that reports "out of quota / no credits" is skipped for a cool-down
period so later requests don't wait on a call that is known to fail.
If every provider fails, an explicit error is returned. We never substitute an
unrelated stock photo.
"""
import os
import io
import time
import base64
import json
import random
import hashlib
import threading
import urllib.parse
from collections import OrderedDict

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

try:
    from google import genai
    from google.genai import types as genai_types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False


GEMINI_IMAGE_MODELS = [
    "gemini-3.1-flash-image",
    "gemini-2.5-flash-image",
    "gemini-3.1-flash-lite-image",
]
HF_IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"

# Style presets are appended AFTER the user's prompt so the subject the user
# described always stays the main instruction.
STYLE_MODIFIERS = {
    "Photorealistic": "photorealistic commercial photography, professional studio lighting, sharp focus, high detail",
    "3D Render": "high-end 3D render, octane render, ray-traced soft shadows, clean materials, high detail",
    "Cyberpunk": "cyberpunk aesthetic, dark background with neon cyan and magenta glow, glossy reflections",
    "Minimalist": "minimalist composition, clean plain backdrop, soft natural light, lots of negative space",
    "Luxury": "luxury advertising photography, dark marble, dramatic low-key lighting, gold accents",
    "Vibrant Pop": "bold vibrant colors, clean gradient background, high-contrast lighting, pop-art energy",
}

ASPECT_DIMS = {
    "1:1": (1024, 1024),
    "16:9": (1344, 768),
    "9:16": (768, 1344),
}

_CACHE_MAX = 24
_cache = OrderedDict()
_cache_lock = threading.Lock()

# provider name -> unix time until which it is skipped
_cooldown = {}
_COOLDOWN_QUOTA = 15 * 60   # out of credits / quota
_poll_lock = threading.Lock()
_poll_last_done = 0.0
_POLL_FREE_GAP = 47  # Pollinations free tier: 1 image / 45s per IP


def _env(*names):
    for n in names:
        v = os.getenv(n)
        if v and v.strip():
            return v.strip()
    return None


def build_prompt(prompt: str, style: str) -> str:
    modifier = STYLE_MODIFIERS.get(style, STYLE_MODIFIERS["Photorealistic"])
    clean = " ".join(prompt.split())
    return f"{clean}. Style: {modifier}. No text, no watermark, no logos."


def _skip(provider):
    return _cooldown.get(provider, 0) > time.time()


def _cool(provider, seconds):
    _cooldown[provider] = time.time() + seconds


def _is_quota_error(msg: str) -> bool:
    m = msg.lower()
    return any(k in m for k in ("429", "402", "resource_exhausted", "quota", "payment required", "credits"))


def _data_url(raw: bytes, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


# ---------------------------------------------------------------- providers --

def _try_gemini(full_prompt, aspect_ratio, errors):
    key = _env("GEMINI_API_KEY")
    if not key or not GENAI_AVAILABLE:
        errors.append("Gemini: GEMINI_API_KEY not configured")
        return None
    if _skip("gemini"):
        errors.append("Gemini: image quota exhausted (cooling down)")
        return None

    client = genai.Client(api_key=key)
    quota_hits = 0
    for model in GEMINI_IMAGE_MODELS:
        try:
            resp = client.models.generate_content(
                model=model,
                contents=full_prompt,
                config=genai_types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=genai_types.ImageConfig(aspect_ratio=aspect_ratio),
                ),
            )
            for cand in resp.candidates or []:
                for part in (cand.content.parts if cand.content else []) or []:
                    if part.inline_data and part.inline_data.data:
                        mime = part.inline_data.mime_type or "image/png"
                        print(f"[ImageService] Gemini {model} OK")
                        return {"image_url": _data_url(part.inline_data.data, mime),
                                "provider": f"Google Gemini ({model})",
                                "_raw": part.inline_data.data, "_mime": mime}
            errors.append(f"Gemini {model}: returned no image (possibly blocked by safety filter)")
        except Exception as e:
            msg = str(e)
            print(f"[ImageService] Gemini {model} error: {msg[:160]}")
            if _is_quota_error(msg):
                quota_hits += 1
            else:
                errors.append(f"Gemini {model}: {msg[:120]}")
    if quota_hits == len(GEMINI_IMAGE_MODELS):
        _cool("gemini", _COOLDOWN_QUOTA)
        errors.append("Gemini: image generation quota exhausted (free tier has no image quota; enable billing)")
    return None


CLOUDFLARE_MODEL = "@cf/black-forest-labs/flux-1-schnell"


def _try_cloudflare(full_prompt, seed, errors):
    """Cloudflare Workers AI: FLUX.1-schnell on a free daily allowance, no watermark (1024x1024)."""
    account, token = _env("CLOUDFLARE_ACCOUNT_ID"), _env("CLOUDFLARE_API_TOKEN")
    if not account or not token:
        errors.append("Cloudflare: CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_API_TOKEN not configured")
        return None
    if _skip("cloudflare"):
        errors.append("Cloudflare: daily free allowance used up (cooling down)")
        return None
    try:
        r = requests.post(
            f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{CLOUDFLARE_MODEL}",
            headers={"Authorization": f"Bearer {token}"},
            # this model's schema accepts only prompt + steps (no seed); every call is a new random variation
            json={"prompt": full_prompt[:2000], "steps": 6},
            timeout=90,
        )
        data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        img_b64 = (data.get("result") or {}).get("image")
        if r.ok and img_b64:
            raw = base64.b64decode(img_b64)
            print("[ImageService] Cloudflare FLUX OK")
            return {"image_url": _data_url(raw, "image/jpeg"), "provider": "FLUX.1-schnell (Cloudflare Workers AI)",
                    "_raw": raw, "_mime": "image/jpeg"}
        msg = f"HTTP {r.status_code} {json.dumps(data.get('errors') or data)[:160]}"
        print(f"[ImageService] Cloudflare error: {msg}")
        if r.status_code in (429, 402) or "neurons" in msg.lower() or "limit" in msg.lower():
            _cool("cloudflare", _COOLDOWN_QUOTA)
            errors.append("Cloudflare: daily free allowance used up")
        elif r.status_code in (401, 403):
            errors.append("Cloudflare: token or account ID rejected - check the token has 'Workers AI' permission")
        else:
            errors.append(f"Cloudflare: {msg}")
    except Exception as e:
        errors.append(f"Cloudflare: {str(e)[:120]}")
    return None


def _try_hf(full_prompt, w, h, seed, errors):
    token = _env("HF_TOKEN", "HUGGINGFACE_TOKEN", "HUGGING_FACE_HUB_TOKEN")
    if not token or not HF_AVAILABLE:
        errors.append("Hugging Face: HF_TOKEN not configured")
        return None
    if _skip("hf"):
        errors.append("Hugging Face: out of inference credits (cooling down)")
        return None
    try:
        image = InferenceClient(api_key=token).text_to_image(
            prompt=full_prompt, model=HF_IMAGE_MODEL,
            width=w, height=h, seed=seed, num_inference_steps=4,
        )
        buf = io.BytesIO()
        image.convert("RGB").save(buf, format="JPEG", quality=94)
        print("[ImageService] HF FLUX OK")
        return {"image_url": _data_url(buf.getvalue(), "image/jpeg"),
                "provider": "FLUX.1-schnell (Hugging Face)",
                "_raw": buf.getvalue(), "_mime": "image/jpeg"}
    except Exception as e:
        msg = str(e)
        print(f"[ImageService] HF error: {msg[:160]}")
        if _is_quota_error(msg):
            _cool("hf", _COOLDOWN_QUOTA)
            errors.append("Hugging Face: out of inference credits (402)")
        else:
            errors.append(f"Hugging Face: {msg[:120]}")
    return None


def _enhance(raw: bytes) -> bytes:
    """The free tier returns ~768px images: upscale 2x (Lanczos) and sharpen lightly so they
    look crisp at display/download size. Returns JPEG bytes (original bytes if PIL fails)."""
    try:
        from PIL import Image, ImageFilter
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        if max(img.size) < 1200:
            img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
            img = img.filter(ImageFilter.UnsharpMask(radius=1.6, percent=70, threshold=2))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=92, optimize=True)
        return buf.getvalue()
    except Exception as e:
        print(f"[ImageService] enhance skipped: {e}")
        return raw


def _try_pollinations(full_prompt, w, h, seed, errors, deadline):
    key = _env("POLLINATIONS_API_KEY")
    q = urllib.parse.quote(full_prompt[:1500])
    params = {"width": w, "height": h, "seed": seed, "model": "flux", "nologo": "true", "enhance": "false"}
    if key:
        url = f"https://gen.pollinations.ai/image/{q}"
        headers = {"Authorization": f"Bearer {key}"}
    else:
        url = f"https://image.pollinations.ai/prompt/{q}"
        headers = {}

    try:
        # The free API answers 402/429 "1 image every 45s" or 503 "at its limit, retry
        # after 10s", sometimes for minutes at busy times. Keep retrying until the
        # request's overall deadline instead of failing early.
        global _poll_last_done
        with _poll_lock:  # serialize: parallel calls would only burn each other's slot
            if not key:
                # Hitting the free API early just gets rejected, so wait out the 45s gap
                # since the previous image once, up front.
                gap = _poll_last_done + _POLL_FREE_GAP - time.time()
                if gap > 0:
                    if time.time() + gap + 20 > deadline:
                        errors.append("Pollinations: free tier allows 1 image per 45s, not enough time left")
                        return None
                    print(f"[ImageService] Pollinations free tier: waiting {gap:.0f}s for next slot")
                    time.sleep(gap)
            while True:
                r = requests.get(url, params=params, headers=headers, timeout=60)
                busy = r.status_code in (402, 429, 502, 503, 504)
                wait = _POLL_FREE_GAP if r.status_code in (402, 429) else 12
                if not busy or time.time() + wait + 20 > deadline:
                    break
                print(f"[ImageService] Pollinations busy ({r.status_code}), retrying in {wait}s")
                time.sleep(wait)
            _poll_last_done = time.time()
        ct = r.headers.get("content-type", "").lower()
        if r.status_code == 200 and ct.startswith("image/") and len(r.content) > 5000:
            # The free tier may ignore model=flux; report the model that was really used.
            model_used = r.headers.get("x-model-used") or "flux"
            label = f"Pollinations ({model_used}{', free tier' if not key else ''})"
            print(f"[ImageService] Pollinations OK model={model_used} ({len(r.content)//1024} KB)")
            raw, mime = _enhance(r.content), "image/jpeg"
            return {"image_url": _data_url(raw, mime), "provider": label, "_raw": raw, "_mime": mime}
        detail = r.text[:160] if not ct.startswith("image/") else "image too small"
        if r.status_code in (402, 429, 503):
            errors.append("Pollinations: free tier is rate-limited/busy right now, try again in a minute")
        else:
            errors.append(f"Pollinations: HTTP {r.status_code} {detail}")
    except Exception as e:
        errors.append(f"Pollinations: {str(e)[:120]}")
    return None


# ------------------------------------------------- prompt refinement + QA ---
# Weak free image models (e.g. Pollinations' "sana") don't know brand names and
# often draw a random portrait instead ("JBL earbuds" -> a woman). Gemini (text +
# vision, available on the free tier) fixes both ends:
#   1. rewrite the prompt into a plain visual description of the product
#   2. look at each generated image and reject it if it doesn't show the subject

QA_MODELS = ["gemini-3.1-flash-lite", "gemini-flash-lite-latest", "gemini-3-flash-preview"]
_refine_cache = OrderedDict()
_brand_info = {}  # user prompt -> {"brand", "search_query", "branded_subject"} (filled by refine_prompt)


def _qa_client():
    key = _env("GEMINI_API_KEY")
    if not key or not GENAI_AVAILABLE:
        return None
    return genai.Client(api_key=key, http_options=genai_types.HttpOptions(timeout=30_000))


def _qa_json(contents):
    """Ask a small Gemini model for JSON; returns dict or None (never raises)."""
    client = _qa_client()
    if not client:
        return None
    for model in QA_MODELS:
        try:
            r = client.models.generate_content(
                model=model, contents=contents,
                config=genai_types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2),
            )
            data = json.loads(r.text or "")
            if isinstance(data, dict):
                return data
        except Exception as e:
            print(f"[ImageService] QA model {model} error: {str(e)[:120]}")
    return None


def refine_prompt(user_prompt: str, style: str):
    """Returns (prompt_for_image_model, subject, people_requested, simple_prompt)."""
    modifier = STYLE_MODIFIERS.get(style, STYLE_MODIFIERS["Photorealistic"])
    clean = " ".join(user_prompt.split())
    key = f"{clean}|{style}"
    if key in _refine_cache:
        return _refine_cache[key]

    data = _qa_json(
        "You write prompts for a basic text-to-image model that does NOT know brand or product names "
        "and tends to draw a random person when confused.\n"
        f'User request: "{clean}"\n'
        "Return JSON with:\n"
        '  "subject": the main product TYPE to show, 1-4 generic words, no brand, count, packaging or adjectives (e.g. "bamboo toothbrush", "wireless earbuds"),\n'
        '  "people_requested": true only if the user explicitly asks for a person, model, hand, face or body,\n'
        '  "prompt": 30-55 words. Start with the subject. Replace every brand/model name with a plain visual '
        "description of that product's shape, colors and materials. Keep the user's setting, colors, lighting and "
        "camera angle. If people_requested is false, describe an object-only still-life product packshot and do not "
        "mention people at all. Never use portrait-photography words (editorial, portrait, rim lighting, beauty, "
        "cinematic, model, sleek, elegant, floating). Wearable items such as earbuds, headphones, watches, jewellery, "
        "glasses or clothing must be shown on a stand, in their case or laid flat, never worn. "
        "No text, letters or logos in the image.\n"
        '  "simple_prompt": max 14 words: the subject, then "product packshot on" a plain background matching the colors the user asked for.\n'
        '  "brand": the company/brand name if the user names a real brand or product line (any company), otherwise "",\n'
        '  "search_query": 2-6 words to find a real photo of exactly this product, brand first (e.g. "Sony WH-1000XM5 headphones"),\n'
        '  "branded_subject": brand + product type using ONLY details the user actually wrote, never add a model, size or '
        'form factor they did not mention (e.g. user "Bowers & Wilkins speakers" -> "Bowers & Wilkins speakers").\n'
        '  "custom_scene": true if the user describes their own scene - specific setting, lighting, camera angle, '
        'smoke, reflections or composition - i.e. they want a newly created image rather than an existing photo.'
    )
    if data and data.get("prompt") and data.get("subject"):
        subject = str(data["subject"]).strip()
        simple = str(data.get("simple_prompt") or f"{subject}, product packshot on a plain background").strip()
        result = (f"{data['prompt'].strip()} Product photography packshot. {modifier}.", subject,
                  bool(data.get("people_requested")), f"{simple}, studio product photography, sharp focus")
        _brand_info[clean] = {
            "brand": str(data.get("brand") or "").strip(),
            "search_query": str(data.get("search_query") or clean[:60]).strip(),
            "branded_subject": str(data.get("branded_subject") or subject).strip(),
            "custom_scene": bool(data.get("custom_scene")),
        }
    else:  # Gemini unavailable -> plain prompt
        plain = f"{clean}. Style: {modifier}. No text, no watermark, no logos."
        result = (plain, clean[:60], False, plain)

    _refine_cache[key] = result
    while len(_refine_cache) > 200:
        _refine_cache.popitem(last=False)
    return result


def verify_image(raw: bytes, mime: str, subject: str, people_requested: bool, brand: str = ""):
    """Returns (ok, description). ok=None when verification wasn't possible.
    With `brand`, the image must also show that brand's logo spelled correctly."""
    if not raw:
        return None, ""
    logo_q = (f'"logo_text": "the brand/logo text visible on the product exactly as written, or empty", '
              f'"logo_correct": bool (true only if a logo on the product clearly reads "{brand}", spelled correctly, '
              'not garbled or misspelled), ') if brand else ""
    data = _qa_json([
        genai_types.Part.from_bytes(data=raw, mime_type=mime or "image/jpeg"),
        f'The user wanted an image of: "{subject}". Look at the image and reply JSON: '
        '{"shows_subject": bool (is that kind of object recognizably the main subject? ignore exact count, '
        'packaging, colors, background and small details), '
        '"contains_person": bool (is any human face or body visible?), ' + logo_q +
        '"description": "what the image actually shows, max 15 words"}',
    ])
    if not data:
        return None, ""
    desc = str(data.get("description", ""))[:150]
    ok = bool(data.get("shows_subject")) and (people_requested or not data.get("contains_person"))
    if ok and brand and not data.get("logo_correct"):
        seen_logo = str(data.get("logo_text") or "").strip()
        return False, f"{brand} logo missing or misspelled" + (f" (reads '{seen_logo[:30]}')" if seen_logo else "")
    return ok, desc


def verify_photo(raw: bytes, mime: str, subject: str):
    """Stricter check for real photos: must show this exact (branded) product clearly."""
    data = _qa_json([
        genai_types.Part.from_bytes(data=raw, mime_type=mime or "image/jpeg"),
        f'Is this a good product photo of: "{subject}"? Reply JSON: '
        '{"shows_product": bool (that general kind of product is clearly the main subject; any model, size or '
        'form factor of it counts, e.g. bookshelf or floorstanding both count as speakers; but false for a toy, '
        'LEGO or scale model, a spare part, battery, accessory or packaging of the product, or a different '
        'product of the same brand, e.g. a games console when a controller was asked for), '
        '"brand_consistent": bool (false only if a visible logo/design clearly belongs to a DIFFERENT brand), '
        '"usable": bool (sharp photo, not a collage, screenshot, drawing or text-heavy advert), '
        '"ad_score": integer 1-10 (how good this is as a product advertising photo: product isolated and '
        'clearly the hero, well lit, attractive; a product hidden in a car, room or crowd scores low), '
        '"description": "max 15 words"}',
    ])
    if not data:
        return None, "", 0
    ok = bool(data.get("shows_product")) and data.get("brand_consistent", True) is not False and bool(data.get("usable", True))
    try:
        score = int(data.get("ad_score") or 0)
    except (TypeError, ValueError):
        score = 0
    return ok, str(data.get("description", ""))[:150], score


# --------------------------------------------------------------------- API ---

def provider_status():
    return {
        "gemini_image": bool(_env("GEMINI_API_KEY")) and not _skip("gemini"),
        "cloudflare": bool(_env("CLOUDFLARE_ACCOUNT_ID") and _env("CLOUDFLARE_API_TOKEN")) and not _skip("cloudflare"),
        "huggingface": bool(_env("HF_TOKEN", "HUGGINGFACE_TOKEN", "HUGGING_FACE_HUB_TOKEN")) and not _skip("hf"),
        "pollinations": "keyed" if _env("POLLINATIONS_API_KEY") else "free tier",
        "image_verification": bool(_env("GEMINI_API_KEY")) and GENAI_AVAILABLE,
    }


MAX_ATTEMPTS = 3
TIME_BUDGET = 210  # seconds per request (frontend waits 240s, gunicorn 300s)


def generate_image(prompt: str, aspect_ratio: str = "1:1", style: str = "Photorealistic", seed=None,
                   mode: str = "auto") -> dict:
    """
    mode: "auto"  - real photo for branded products, AI generation otherwise
          "photo" - real product photo only
          "ai"    - AI generation only
    """
    if not prompt or not prompt.strip():
        return {"success": False, "error": "Please enter an image prompt."}

    if aspect_ratio not in ASPECT_DIMS:
        aspect_ratio = "1:1"
    if style not in STYLE_MODIFIERS:
        style = "Photorealistic"
    try:
        seed = int(seed) % 2_147_483_647 if seed is not None else random.randint(1, 2_147_483_646)
    except (TypeError, ValueError):
        seed = random.randint(1, 2_147_483_646)

    deadline = time.time() + TIME_BUDGET
    w, h = ASPECT_DIMS[aspect_ratio]
    model_prompt, subject, people_requested, simple_prompt = refine_prompt(prompt, style)
    gemini_prompt = build_prompt(prompt, style)  # Gemini image models understand brands directly

    if mode not in ("auto", "photo", "ai"):
        mode = "auto"
    cache_key = hashlib.sha256(f"{prompt.strip()}|{style}|{aspect_ratio}|{seed}|{mode}".encode()).hexdigest()
    with _cache_lock:
        if cache_key in _cache:
            _cache.move_to_end(cache_key)
            return _cache[cache_key]

    errors, rejected = [], []

    # ---- real product photo (branded products) ----
    info = _brand_info.get(" ".join(prompt.split()), {})
    # Auto: real photos only for plain product requests; a described scene needs a created image
    if mode == "photo" or (mode == "auto" and info.get("brand") and not info.get("custom_scene")):
        from services.photo_service import find_product_photo, query_variants
        photo, photo_notes = find_product_photo(
            query_variants(info.get("search_query") or prompt.strip()[:80], info.get("brand", ""), subject),
            info.get("branded_subject") or subject,
            verify_photo,
            deadline=min(deadline, time.time() + 100),
            min_score=1 if mode == "photo" else 5,  # Auto: a weak photo is worse than a clean AI image
        )
        if photo:
            photo.update({"success": True, "verified": True, "subject": info.get("branded_subject") or subject,
                          "style": style, "seed": seed, "attempts": 1, "simplified": False, "notes": []})
            with _cache_lock:
                _cache[cache_key] = photo
            return photo
        if mode == "photo":
            return {"success": False, "error": "No matching real photo found. " + " ".join(photo_notes) +
                    " Try AI Generate, or a more common product name.", "details": photo_notes}
        errors.append("No verified real photo found, so it was generated with AI instead")
    result, used_prompt, logo_shown = None, model_prompt, False
    brand = (info.get("brand") or "").strip()
    for attempt in range(MAX_ATTEMPTS):
        attempt_seed = (seed + attempt * 7919) % 2_147_483_647
        # first try the detailed prompt; if the model drew the wrong thing, retry with a
        # very plain "product packshot" prompt, which weak models follow much more reliably
        bare_prompt = f"{subject}, product packshot, plain white background, studio product photography, sharp focus"
        attempt_prompt = [model_prompt, simple_prompt, bare_prompt][min(attempt, 2)]
        # FLUX (Cloudflare / Hugging Face) can render short logo text, so for a branded request it
        # gets the logo back; the last attempt drops it so the user still gets an image. The weak
        # free fallback (Pollinations "sana") always gets the brand-free prompt - brand names make
        # it draw unrelated portraits.
        want_logo = bool(brand) and attempt < MAX_ATTEMPTS - 1
        logo_prompt = (f'{attempt_prompt} The "{brand}" brand logo is printed clearly on the product '
                       f'in clean, correctly spelled letters.') if want_logo else attempt_prompt
        candidate = (
            _try_gemini(gemini_prompt, aspect_ratio, errors)
            or _try_cloudflare(logo_prompt, attempt_seed, errors)
            or _try_hf(logo_prompt, w, h, attempt_seed, errors)
            or _try_pollinations(attempt_prompt, w, h, attempt_seed, errors, deadline)
        )
        if not candidate:
            break  # no provider could produce anything; retrying won't help

        check_logo = want_logo and "Pollinations" not in candidate.get("provider", "")
        ok, seen = verify_image(candidate.get("_raw"), candidate.get("_mime"), subject, people_requested,
                                **({"brand": brand} if check_logo else {}))
        if ok and check_logo:
            logo_shown = True
            attempt_prompt = logo_prompt
        candidate["verified"] = ok
        if ok is False:
            print(f"[ImageService] Rejected attempt {attempt + 1}: wanted '{subject}', got '{seen}'")
            rejected.append(seen or "an unrelated image")
            if time.time() + 60 > deadline:
                break
            continue
        result = candidate
        used_prompt = attempt_prompt
        break

    if not result:
        if rejected:
            return {
                "success": False,
                "error": (f"The image engine kept producing the wrong picture ({rejected[-1]}) instead of "
                          f"\"{subject}\", so it was not shown. Try again or simplify the prompt."),
                "details": errors,
            }
        return {
            "success": False,
            "error": "No image provider is currently available. " + " | ".join(errors),
            "details": errors,
        }

    result.pop("_raw", None)
    result.pop("_mime", None)
    result.update({
        "success": True,
        "seed": seed,
        "style": style,
        "aspect_ratio": aspect_ratio,
        "subject": subject,
        "prompt_used": used_prompt,
        "simplified": len(rejected) >= 2,  # fell back to a plain-background packshot
        "logo": brand if logo_shown else None,  # brand logo verified as correctly spelled
        "attempts": len(rejected) + 1,
        "notes": errors,  # why higher-quality providers were skipped
    })
    with _cache_lock:
        _cache[cache_key] = result
        while len(_cache) > _CACHE_MAX:
            _cache.popitem(last=False)
    return result
