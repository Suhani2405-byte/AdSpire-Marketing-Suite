import os
import io
import time
import base64
import hashlib
import urllib.parse
import requests
from dotenv import load_dotenv

load_dotenv()

try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False


# In-memory cache to prevent redundant requests and stay within free rate limits
_IMAGE_CACHE = {}

# Style modifier presets engineered specifically for commercial product photography
STYLE_MODIFIERS = {
    "Photorealistic": (
        "commercial studio product photography, softbox diffused lighting, "
        "crisp product reflections, tack-sharp macro detail, 8K ultra-realistic"
    ),
    "3D Render": (
        "photorealistic 3D product render, Octane render, ray-traced shadows, "
        "subsurface scattering, sleek industrial design aesthetics, 8K"
    ),
    "Cyberpunk": (
        "futuristic product showcase, dark background with subtle neon-cyan and magenta rim highlights, "
        "clean glossy reflective pedestal, high-tech luxury commercial shoot, 8K"
    ),
    "Minimalist": (
        "minimalist Scandinavian product catalog photography, clean monochromatic studio backdrop, "
        "soft natural directional lighting, high-end design aesthetic, 8K"
    ),
    "Luxury": (
        "ultra-luxury product advertisement, dark polished marble pedestal, "
        "dramatic chiaroscuro studio lighting, gold and obsidian undertones, 8K"
    ),
    "Vibrant Pop": (
        "bold commercial product photography, vibrant clean gradient background, "
        "high-contrast studio strobe lighting, dynamic angle, modern commercial packaging, 8K"
    ),
}


def _make_seed(text: str) -> int:
    """Deterministic seed — same prompt always produces the same image."""
    h = hashlib.sha256(text.strip().lower().encode()).hexdigest()
    return int(h[:8], 16) % 2_147_483_647


def _dims(aspect_ratio: str):
    return {
        "1:1":  (1024, 1024),
        "16:9": (1280, 720),
        "9:16": (720, 1280),
    }.get(aspect_ratio, (1024, 1024))


def _clean_product_prompt(prompt: str, modifier: str) -> str:
    """
    Format prompt specifically for product-only photography.
    Excludes human faces/models to prevent model from hallucinating portraits.
    """
    clean = prompt.strip()
    # Strip any redundant leading tags
    for prefix in ["isolated commercial product photography of", "commercial photography of"]:
        if clean.lower().startswith(prefix):
            clean = clean[len(prefix):].strip()

    return (
        f"isolated commercial product photography of {clean}, "
        f"studio tabletop setup, {modifier}, "
        f"clean backdrop, product only, sharp focus, 8k, "
        f"no people, no human, no woman, no man, no face, no model, no watermark"
    )


def _pollinations_url(prompt: str, w: int, h: int, seed: int) -> str:
    """
    Build clean Pollinations URL.
    CRITICAL: Never include model=flux or enhance=true:
    - model=flux causes HTTP 402 on unauthenticated tiers.
    - enhance=true triggers an LLM rewriter that turns product prompts into human portraits.
    """
    safe = prompt[:350]
    enc = urllib.parse.quote(safe)
    return (
        f"https://image.pollinations.ai/prompt/{enc}"
        f"?width={w}&height={h}&seed={seed}&nologo=true"
    )


def generate_image(prompt: str, aspect_ratio: str = "1:1", style: str = "Photorealistic") -> dict:
    """
    Generate an ultra high-quality AI marketing product visual.
    1. Check memory cache (instant response, zero rate-limit issues).
    2. Try HuggingFace FLUX.1 (if valid credentials present).
    3. Fetch from Pollinations AI with product-isolated prompt and embed as base64.
    4. Fall back to returning direct high-resolution Pollinations URL.
    """
    if not prompt or not prompt.strip():
        return {"success": False, "error": "Please enter an image prompt."}

    modifier = STYLE_MODIFIERS.get(style, STYLE_MODIFIERS["Photorealistic"])
    product_prompt = _clean_product_prompt(prompt, modifier)
    seed = _make_seed(product_prompt)
    w, h = _dims(aspect_ratio)

    cache_key = f"{seed}_{w}_{h}_{style}"
    if cache_key in _IMAGE_CACHE:
        print(f"[ImageService] Serving from cache: {cache_key}")
        return _IMAGE_CACHE[cache_key]

    hf_token = (
        os.getenv("HF_TOKEN")
        or os.getenv("HUGGINGFACE_TOKEN")
        or os.getenv("HUGGING_FACE_HUB_TOKEN")
    )

    # 1. Try Hugging Face if token configured
    if hf_token and HF_AVAILABLE:
        result = _try_hf(product_prompt, w, h, seed, hf_token)
        if result:
            _IMAGE_CACHE[cache_key] = result
            return result

    # 2. Pollinations AI (embedded base64)
    result = _try_pollinations(product_prompt, w, h, seed)
    if result:
        _IMAGE_CACHE[cache_key] = result
        return result

    # 3. Direct URL fallback (no model=flux or enhance=true)
    url = _pollinations_url(product_prompt, w, h, seed)
    print(f"[ImageService] Direct URL fallback | seed={seed} | {w}x{h}")
    fallback_res = {
        "success": True,
        "image_url": url,
        "provider": "Pollinations AI (Product Engine)",
        "seed": seed,
        "resolution": f"{w}x{h}",
    }
    _IMAGE_CACHE[cache_key] = fallback_res
    return fallback_res


def _try_hf(prompt: str, w: int, h: int, seed: int, token: str):
    try:
        print(f"[ImageService] Attempting HF | seed={seed} | {w}x{h}")
        client = InferenceClient(api_key=token)
        image = client.text_to_image(
            prompt=prompt[:250],
            model="black-forest-labs/FLUX.1-schnell",
            width=w, height=h, seed=seed,
            num_inference_steps=4,
        )
        buf = io.BytesIO()
        image.save(buf, format="PNG", compress_level=1)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        print(f"[ImageService] HF OK — {len(b64)//1024} KB")
        return {
            "success": True,
            "image_url": f"data:image/png;base64,{b64}",
            "provider": "FLUX.1-schnell (HuggingFace)",
            "seed": seed,
            "resolution": f"{w}x{h}",
        }
    except Exception as e:
        msg = str(e)
        if "402" in msg or "Payment" in msg or "credits" in msg.lower():
            print("[ImageService] HF: insufficient credits, skipping.")
        else:
            print(f"[ImageService] HF error: {e}")
        return None


def _try_pollinations(prompt: str, w: int, h: int, seed: int):
    url = _pollinations_url(prompt, w, h, seed)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Referer": "https://pollinations.ai/",
    }
    try:
        print(f"[ImageService] Requesting Pollinations Product Render | seed={seed} | {w}x{h}")
        r = requests.get(url, headers=headers, timeout=45, allow_redirects=True)
        ct = r.headers.get("content-type", "").lower()
        kb = len(r.content) / 1024

        if r.status_code == 200 and "image" in ct and kb > 15:
            mime = "image/png" if "png" in ct else "image/jpeg"
            b64 = base64.b64encode(r.content).decode()
            print(f"[ImageService] Pollinations Product Render OK — {kb:.0f} KB")
            return {
                "success": True,
                "image_url": f"data:{mime};base64,{b64}",
                "provider": "Pollinations AI (Product Engine)",
                "seed": seed,
                "resolution": f"{w}x{h}",
            }
        print(f"[ImageService] Pollinations non-image/rate-limited response: status={r.status_code}, {kb:.0f}KB, ct={ct}")
    except Exception as e:
        print(f"[ImageService] Pollinations connection error: {e}")
    return None
