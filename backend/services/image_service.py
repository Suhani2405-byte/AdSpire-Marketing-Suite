import os
import io
import base64
import random
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


def generate_image(prompt, aspect_ratio="1:1", style="Photorealistic"):
    """
    Generate an AI marketing visual matching the exact user prompt & style.
    """
    if not prompt or not prompt.strip():
        return {
            "success": False,
            "error": "Please enter an image prompt."
        }

    # Style modifiers that enhance without altering user prompt intent
    style_modifiers = {
        "Photorealistic": "commercial product photography, 8k resolution, cinematic studio lighting, hyperrealistic, high-end commercial ad, elegant depth of field",
        "3D Render": "3D render, octane render, smooth lighting, modern C4D style, futuristic aesthetic, vibrant colors, ray tracing",
        "Cyberpunk": "cyberpunk neon glow, dark futuristic aesthetic, synthwave colors, sharp volumetric light, vibrant highlights",
        "Minimalist": "minimalist aesthetic, clean pastel background, soft diffuse shadows, Scandinavian design, premium simplicity",
        "Luxury": "luxury editorial advertisement, gold and obsidian tones, high-fashion magazine style, dramatic lighting",
        "Vibrant Pop": "vibrant pop art colors, high contrast, dynamic marketing visual, bold gradients, energetic composition"
    }

    modifier = style_modifiers.get(style, style_modifiers["Photorealistic"])
    
    # Preserve user prompt exactly and append style enhancement
    enhanced_prompt = f"{prompt.strip()}, {modifier}"

    # Aspect ratio dimensions
    dim_map = {
        "1:1": (1024, 1024),
        "16:9": (1024, 576),
        "9:16": (576, 1024),
        "4:3": (1024, 768)
    }
    width, height = dim_map.get(aspect_ratio, (1024, 1024))

    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")

    # 1. Hugging Face FLUX.1 (if token configured)
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
            print(f"[ImageService] Hugging Face error: {e}. Falling back to high-speed AI engine...")

    # 2. Pollinations AI Generator (Instant, high-speed, direct prompt fidelity)
    seed = random.randint(1000, 9999999)
    encoded_prompt = urllib.parse.quote(enhanced_prompt)
    pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}"

    browser_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
    }

    try:
        print(f"[ImageService] Fetching from Pollinations AI (seed={seed})...")
        response = requests.get(pollinations_url, headers=browser_headers, timeout=12)
        content_type = response.headers.get("content-type", "").lower()

        if response.status_code == 200 and ("image" in content_type) and len(response.content) > 1000:
            mime_type = "image/png" if "png" in content_type else "image/jpeg"
            image_base64 = base64.b64encode(response.content).decode("utf-8")
            image_url = f"data:{mime_type};base64,{image_base64}"
            return {
                "success": True,
                "image_url": image_url,
                "provider": "Pollinations AI",
                "prompt": enhanced_prompt
            }
    except Exception as e:
        print(f"[ImageService] Binary fetch error: {e}. Returning direct AI image URL...")

    # If server binary fetch timed out or was blocked, return the direct URL for browser rendering
    return {
        "success": True,
        "image_url": pollinations_url,
        "provider": "Pollinations AI (Direct)",
        "prompt": enhanced_prompt
    }