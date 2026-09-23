import os
import io
import base64
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
    Generate an AI marketing visual using Hugging Face FLUX.1 with fallback to Pollinations AI.
    """
    if not prompt or not prompt.strip():
        return {
            "success": False,
            "error": "Please enter an image prompt."
        }

    # Enhance prompt with style modifiers
    style_modifiers = {
        "Photorealistic": "commercial product photography, 8k resolution, studio lighting, hyperrealistic, high-end commercial",
        "3D Render": "3D render, octane render, smooth lighting, modern C4D style, futuristic aesthetic, vibrant colors",
        "Cyberpunk": "cyberpunk neon glow, dark futuristic aesthetic, synthwave colors, sharp volumetric light",
        "Minimalist": "minimalist aesthetic, clean pastel background, soft diffuse shadows, Scandinavian design",
        "Luxury": "luxury editorial advertisement, gold and obsidian tones, high-fashion magazine style, dramatic lighting",
        "Vibrant Pop": "vibrant pop art colors, high contrast, dynamic marketing visual, bold gradients"
    }

    modifier = style_modifiers.get(style, style_modifiers["Photorealistic"])
    enhanced_prompt = f"{prompt.strip()}, {modifier}"

    # Aspect ratio dimensions
    dim_map = {
        "1:1": (1024, 1024),
        "16:9": (1024, 576),
        "9:16": (576, 1024),
        "4:3": (1024, 768)
    }
    width, height = dim_map.get(aspect_ratio, (1024, 1024))

    hf_token = os.getenv("HF_TOKEN")

    # 1. Try Hugging Face FLUX.1
    if hf_token and HF_AVAILABLE:
        try:
            print(f"[ImageService] Generating with Hugging Face FLUX.1: '{prompt[:40]}...'")
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
            print(f"[ImageService] Hugging Face generation error: {e}. Trying fallback generator...")

    # 2. Try Pollinations AI generator (High-speed zero-auth fallback)
    try:
        print("[ImageService] Generating with Pollinations AI...")
        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed=42"
        
        response = requests.get(pollinations_url, timeout=25)
        if response.status_code == 200 and len(response.content) > 1000:
            image_base64 = base64.b64encode(response.content).decode("utf-8")
            image_url = f"data:image/png;base64,{image_base64}"
            return {
                "success": True,
                "image_url": image_url,
                "provider": "Pollinations AI (FLUX Engine)",
                "prompt": enhanced_prompt
            }
        else:
            # If binary fetch failed, return direct secure image URL
            return {
                "success": True,
                "image_url": pollinations_url,
                "provider": "Pollinations AI",
                "prompt": enhanced_prompt
            }
    except Exception as e:
        print(f"[ImageService] Pollinations generation error: {e}")

    return {
        "success": False,
        "error": "Failed to generate image across all AI endpoints. Please check network connectivity or HF_TOKEN."
    }