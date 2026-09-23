from flask import Blueprint, request, jsonify
from services.image_service import generate_image

image_bp = Blueprint("image", __name__)


@image_bp.route("/generate", methods=["POST"])
def generate_image_route():
    try:
        data = request.get_json() or {}
        prompt = data.get("prompt", "").strip()
        aspect_ratio = data.get("aspect_ratio", "1:1")
        style = data.get("style", "Photorealistic")

        if not prompt:
            return jsonify({
                "success": False,
                "error": "Please enter an image prompt."
            }), 400

        result = generate_image(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            style=style
        )

        if result.get("success"):
            return jsonify(result), 200

        return jsonify(result), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@image_bp.route("/test", methods=["GET"])
def image_test():
    return jsonify({
        "success": True,
        "message": "AI Image Generation route is active and ready.",
        "models": ["FLUX.1-schnell", "Pollinations AI"],
        "styles": ["Photorealistic", "3D Render", "Cyberpunk", "Minimalist", "Luxury", "Vibrant Pop"]
    }), 200