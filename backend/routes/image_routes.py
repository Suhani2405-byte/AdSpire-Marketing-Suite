import time

from flask import Blueprint, request, jsonify, g

from services.image_service import generate_image, provider_status, STYLE_MODIFIERS
from services import database_service as db
from services.auth_service import login_required, feature_required
from services.rate_limit import rate_limited

image_bp = Blueprint("image", __name__)


@image_bp.route("/generate", methods=["POST"])
@login_required
@feature_required("image_generation")
@rate_limited("image", limit=lambda: db.get_settings()["image_limit_per_hour"], window=3600)
def generate_image_route():
    try:
        data = request.get_json(silent=True) or {}
        prompt = str(data.get("prompt", "")).strip()[:2000]
        if not prompt:
            return jsonify({"success": False, "error": "Please enter an image prompt."}), 400

        t0 = time.time()
        result = generate_image(
            prompt=prompt,
            aspect_ratio=data.get("aspect_ratio", "1:1"),
            style=data.get("style", "Photorealistic"),
            seed=data.get("seed"),
            mode=data.get("mode", "auto"),
        )
        ms = (time.time() - t0) * 1000
        if result.get("success"):
            db.log_activity("image", user_id=g.user.id, detail=prompt[:120],
                            provider=result.get("provider"), duration_ms=ms)
            return jsonify(result), 200

        db.log_activity("image_failed", user_id=g.user.id, detail=result.get("error", "")[:300], duration_ms=ms)
        # 503: all upstream providers unavailable (quota / rate limit), not a server bug
        return jsonify(result), 503

    except Exception as e:
        print(f"[ImageRoutes] Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@image_bp.route("/test", methods=["GET"])
def image_test():
    return jsonify({
        "success": True,
        "message": "AI Image Generation route is active.",
        "providers": provider_status(),
        "styles": list(STYLE_MODIFIERS.keys()),
    }), 200
