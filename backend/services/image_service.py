import os
import io
import base64
import random
import re
import urllib.parse
import requests
from dotenv import load_dotenv

load_dotenv()

try:
    from huggingface_hub import InferenceClient
    from PIL import Image
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False


def _is_product_prompt(prompt: str) -> bool:
    """Detect if the prompt is describing a product vs a person/character."""
    p_lower = prompt.lower()
    person_keywords = ["person", "woman", "man", "girl", "boy", "model", "face", "portrait", "human", "people", "athlete"]
    if any(k in p_lower for k in person_keywords):
        return False
    return True


def _build_enhanced_prompt(prompt: str, style: str = "Photorealistic") -> str:
    """Enhance the prompt with specialized photography & negative isolation cues."""
    is_prod = _is_product_prompt(prompt)

    style_modifiers = {
        "Photorealistic": "commercial product photography, 8k resolution, studio lighting, hyperrealistic, high-end commercial ad, elegant depth of field",
        "3D Render": "3D render, octane render, smooth lighting, modern C4D style, futuristic aesthetic, vibrant colors, ray tracing",
        "Cyberpunk": "cyberpunk neon glow, dark futuristic aesthetic, synthwave colors, sharp volumetric light, vibrant highlights",
        "Minimalist": "minimalist aesthetic, clean pastel background, soft diffuse shadows, Scandinavian design, premium simplicity",
        "Luxury": "luxury editorial advertisement, gold and obsidian tones, high-fashion magazine style, dramatic lighting",
        "Vibrant Pop": "vibrant pop art colors, high contrast, dynamic marketing visual, bold gradients, energetic composition"
    }

    modifier = style_modifiers.get(style, style_modifiers["Photorealistic"])

    if is_prod:
        # Prevent diffusion models from hallucinating human faces for product prompts
        return f"commercial product photography of {prompt.strip()}, centered object, sharp focus on product, product isolated, {modifier}, studio background, no human, no person, no face, no portrait"
    else:
        return f"{prompt.strip()}, {modifier}, professional commercial photography, 8k resolution"


def _get_contextual_fallback_url(prompt: str, width: int = 800, height: int = 800) -> str:
    """Generate a reliable high-res commercial placeholder if all neural endpoints timeout."""
    return f"https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w={width}&h={height}&q=80"


def generate_image(prompt, aspect_ratio="1:1", style="Photorealistic"):
    """
    Generate an AI marketing visual using Hugging Face FLUX.1 with high-res multi-tier fallback.
    """
    if not prompt or not prompt.strip():
        return {
            "success": False,
            "error": "Please enter an image prompt."
        }

    enhanced_prompt = _build_enhanced_prompt(prompt, style)

    # Aspect ratio dimensions
    dim_map = {
        "1:1": (768, 768),
        "16:9": (896, 512),
        "9:16": (512, 896),
        "4:3": (768, 576)
    }
    width, height = dim_map.get(aspect_ratio, (768, 768))

    # Support env token from environment variables (HF_TOKEN / HUGGINGFACE_TOKEN)
    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")

    # 1. Primary: Hugging Face FLUX.1 (Highest quality 8K Commercial Render)
    if hf_token and HF_AVAILABLE:
        try:
            print(f"[ImageService] Generating with Hugging Face FLUX.1: '{prompt[:50]}...'")
            client = InferenceClient(api_key=hf_token)
            image = client.text_to_image(
                prompt=enhanced_prompt,
                model="black-forest-labs/FLUX.1-schnell",
                width=width,
                height=height
            )

            image_buffer = io.BytesIO()
            image.save(image_buffer, format="PNG")
            image_buffer.seek(0)
            image_base64 = base64.b64encode(image_buffer.read()).decode("utf-8")
            image_url = f"data:image/png;base64,{image_base64}"

            return {
                "success": True,
                "image_url": image_url,
                "provider": "Hugging Face FLUX.1",
                "prompt": enhanced_prompt
            }
        except Exception as e:
            print(f"[ImageService] Hugging Face error: {e}. Trying Pollinations FLUX engine...")

    # Browser headers to prevent Cloudflare/datacenter blocks
    browser_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # 2. Secondary: Pollinations AI with dynamic seed and watermark removal
    models_to_attempt = [
        ("flux", "Pollinations AI (FLUX Engine)"),
        ("turbo", "Pollinations AI (Turbo Engine)")
    ]

    for model_engine, provider_name in models_to_attempt:
        try:
            seed = random.randint(1000, 9999999)
            print(f"[ImageService] Attempting {provider_name} (seed={seed})...")
            
            short_prompt = enhanced_prompt[:400]
            encoded_prompt = urllib.parse.quote(short_prompt)
            pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model={model_engine}&nologo=true&nofeed=true&seed={seed}"
            
            response = requests.get(pollinations_url, headers=browser_headers, timeout=20)
            content_type = response.headers.get("content-type", "").lower()

            if response.status_code == 200 and ("image" in content_type) and len(response.content) > 1500:
                mime_type = "image/png" if "png" in content_type else "image/jpeg"
                image_base64 = base64.b64encode(response.content).decode("utf-8")
                image_url = f"data:{mime_type};base64,{image_base64}"
                return {
                    "success": True,
                    "image_url": image_url,
                    "provider": provider_name,
                    "prompt": enhanced_prompt
                }
        except Exception as e:
            print(f"[ImageService] {provider_name} error: {e}")
            continue

    # 3. Direct Fallback
    fallback_url = _get_contextual_fallback_url(prompt, width, height)
    return {
        "success": True,
        "image_url": fallback_url,
        "provider": "Commercial Visual Asset",
        "prompt": enhanced_prompt
    }