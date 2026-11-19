import json
import time

from flask import Blueprint, request, jsonify, g, Response, stream_with_context

from services.gemini_service import generate_marketing_campaign, stream_marketing_campaign
from services import database_service as db
from services.auth_service import login_required, feature_required
from services.rate_limit import rate_limited

campaign_bp = Blueprint("campaigns", __name__)


def _scope():
    """Admins see every campaign; marketers only their own."""
    return None if g.user.role == "admin" else g.user.id


def _read_inputs(data):
    def field(*names, default=""):
        for n in names:
            v = data.get(n)
            if isinstance(v, str) and v.strip():
                return v.strip()
        return default

    inputs = {
        "product_name": field("product_name", "productName")[:200],
        "description": field("description", "product_description", "productDescription")[:3000],
        "audience": field("target_audience", "audience")[:300],
        "platform": field("platform", default="Instagram")[:100],
        "goal": field("goal", default="Brand Awareness")[:100],
        "tone": field("tone", default="Bold & Premium")[:100],
        "industry": field("industry")[:100],
    }
    if not inputs["product_name"]:
        return None, "Product name is required."
    if not inputs["description"]:
        return None, "Product description is required."
    return inputs, None


def _save(inputs, campaign, meta, duration_ms):
    try:
        cid = db.save_campaign(
            product_name=inputs["product_name"], target_audience=inputs["audience"],
            platform=inputs["platform"], goal=inputs["goal"], campaign_content=campaign,
            user_id=g.user.id, source=meta["model"] or meta["source"],
        )
    except Exception as e:
        print(f"[CampaignRoutes] Error saving campaign: {e}")
        cid = None
    db.log_activity("campaign", user_id=g.user.id, detail=inputs["product_name"],
                    provider=meta["model"] or "template", duration_ms=duration_ms)
    return cid


@campaign_bp.route("/generate", methods=["POST"])
@login_required
@feature_required("campaign_generation")
@rate_limited("campaign", limit=lambda: db.get_settings()["campaign_limit_per_hour"], window=3600)
def generate_campaign_route():
    """Generate a campaign and return it in one response."""
    inputs, err = _read_inputs(request.get_json(silent=True) or {})
    if err:
        return jsonify({"success": False, "error": err}), 400
    try:
        t0 = time.time()
        campaign, meta = generate_marketing_campaign(**inputs)
        cid = _save(inputs, campaign, meta, (time.time() - t0) * 1000)
        return jsonify({"success": True, "campaign_id": cid, "campaign_content": campaign, **meta}), 200
    except Exception as e:
        print(f"[CampaignRoutes] Error generating campaign: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@campaign_bp.route("/generate-stream", methods=["POST"])
@login_required
@feature_required("campaign_generation")
@rate_limited("campaign", limit=lambda: db.get_settings()["campaign_limit_per_hour"], window=3600)
def generate_campaign_stream_route():
    """Same as /generate but streams progress as Server-Sent Events."""
    inputs, err = _read_inputs(request.get_json(silent=True) or {})
    if err:
        return jsonify({"success": False, "error": err}), 400
    user = g.user

    def sse(event):
        return f"data: {json.dumps(event)}\n\n"

    @stream_with_context
    def events():
        g.user = user
        t0 = time.time()
        try:
            for ev in stream_marketing_campaign(**inputs):
                if ev["type"] == "done":
                    cid = _save(inputs, ev["campaign"], ev["meta"], (time.time() - t0) * 1000)
                    yield sse({"type": "done", "campaign_id": cid, "campaign_content": ev["campaign"], **ev["meta"]})
                else:
                    yield sse(ev)
        except Exception as e:
            print(f"[CampaignRoutes] Stream error: {e}")
            yield sse({"type": "error", "error": str(e)})

    return Response(events(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@campaign_bp.route("", methods=["GET"])
@campaign_bp.route("/", methods=["GET"])
@login_required
def get_all_campaigns_route():
    # Admins see every user's campaigns; marketers only their own
    campaigns = db.get_campaigns(user_id=_scope())
    return jsonify({"success": True, "campaigns": campaigns, "count": len(campaigns)}), 200


@campaign_bp.route("/<int:campaign_id>", methods=["GET"])
@login_required
def get_single_campaign_route(campaign_id):
    campaign = db.get_campaign_by_id(campaign_id, user_id=_scope())
    if not campaign:
        return jsonify({"success": False, "error": "Campaign not found"}), 404
    return jsonify({"success": True, "campaign": campaign}), 200


@campaign_bp.route("", methods=["POST"])
@campaign_bp.route("/", methods=["POST"])
@login_required
def save_campaign_route():
    """Manually save a campaign."""
    data = request.get_json(silent=True) or {}
    product_name = str(data.get("product_name") or data.get("productName") or "").strip()
    if not product_name:
        return jsonify({"success": False, "error": "Product name is required."}), 400
    campaign_id = db.save_campaign(
        product_name=product_name,
        target_audience=data.get("target_audience") or data.get("audience") or "",
        platform=data.get("platform", "Instagram"),
        goal=data.get("goal", "Brand Awareness"),
        campaign_content=data.get("campaign_content") or data.get("campaignContent") or {},
        image_url=data.get("image_url"),
        user_id=g.user.id,
        source="manual",
    )
    return jsonify({"success": True, "message": "Campaign saved successfully.", "id": campaign_id}), 201


@campaign_bp.route("/<int:campaign_id>", methods=["DELETE"])
@login_required
def delete_campaign_route(campaign_id):
    if not db.delete_campaign(campaign_id, user_id=_scope()):
        return jsonify({"success": False, "error": "Campaign not found."}), 404
    return jsonify({"success": True, "message": "Campaign deleted successfully."}), 200


@campaign_bp.route("/<int:campaign_id>/image", methods=["PUT"])
@login_required
def update_campaign_image_route(campaign_id):
    """Attach the generated creative image to a saved campaign."""
    data = request.get_json(silent=True) or {}
    image_url = data.get("image_url")
    if not image_url or not isinstance(image_url, str):
        return jsonify({"success": False, "error": "image_url is required."}), 400
    if not (image_url.startswith("data:image/") or image_url.startswith("https://")):
        return jsonify({"success": False, "error": "image_url must be an image data URL or https URL."}), 400
    if len(image_url) > 8_000_000:
        return jsonify({"success": False, "error": "Image is too large."}), 413
    if not db.update_campaign_image(campaign_id, image_url, user_id=_scope()):
        return jsonify({"success": False, "error": "Campaign not found."}), 404
    return jsonify({"success": True}), 200


@campaign_bp.route("/stats", methods=["GET"])
@login_required
def stats_route():
    return jsonify({"success": True, "stats": db.get_database_stats(user_id=_scope())}), 200
