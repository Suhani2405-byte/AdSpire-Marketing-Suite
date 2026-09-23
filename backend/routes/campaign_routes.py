from flask import Blueprint, request, jsonify
from services.gemini_service import generate_marketing_campaign
from services.database_service import (
    save_campaign,
    get_campaigns,
    get_campaign_by_id,
    delete_campaign,
    get_database_stats
)

campaign_bp = Blueprint("campaigns", __name__)


@campaign_bp.route("/generate", methods=["POST"])
def generate_campaign_route():
    """Generate a multi-agent marketing campaign."""
    try:
        data = request.get_json() or {}
        product_name = data.get("product_name", "").strip() or data.get("productName", "").strip()
        description = data.get("description", "").strip()
        audience = data.get("target_audience", "").strip() or data.get("audience", "").strip()
        platform = data.get("platform", "Instagram").strip()
        goal = data.get("goal", "Brand Awareness").strip()
        auto_save = data.get("auto_save", True)

        if not product_name:
            return jsonify({"success": False, "error": "Product name is required."}), 400

        if not description:
            return jsonify({"success": False, "error": "Product description is required."}), 400

        print(f"[CampaignRoutes] Generating campaign for '{product_name}'...")
        campaign_content = generate_marketing_campaign(
            product_name=product_name,
            description=description,
            audience=audience,
            platform=platform,
            goal=goal
        )

        saved_id = None
        if auto_save:
            try:
                saved_id = save_campaign(
                    product_name=product_name,
                    target_audience=audience,
                    platform=platform,
                    goal=goal,
                    campaign_content=campaign_content
                )
            except Exception as db_err:
                print(f"[CampaignRoutes] Error auto-saving campaign: {db_err}")

        return jsonify({
            "success": True,
            "message": "Campaign generated successfully.",
            "campaign_id": saved_id,
            "campaign_content": campaign_content
        }), 200

    except Exception as e:
        print(f"[CampaignRoutes] Error generating campaign: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@campaign_bp.route("", methods=["GET"])
@campaign_bp.route("/", methods=["GET"])
def get_all_campaigns_route():
    """Retrieve all saved campaigns."""
    try:
        campaigns_list = get_campaigns()
        return jsonify({
            "success": True,
            "campaigns": campaigns_list,
            "count": len(campaigns_list)
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@campaign_bp.route("/<int:campaign_id>", methods=["GET"])
def get_single_campaign_route(campaign_id):
    """Retrieve single campaign by ID."""
    try:
        campaign = get_campaign_by_id(campaign_id)
        if not campaign:
            return jsonify({"success": False, "error": "Campaign not found"}), 404
        return jsonify({"success": True, "campaign": campaign}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@campaign_bp.route("", methods=["POST"])
@campaign_bp.route("/", methods=["POST"])
def save_campaign_route():
    """Manually save a campaign."""
    try:
        data = request.get_json() or {}
        product_name = data.get("product_name", "") or data.get("productName", "")
        audience = data.get("target_audience", "") or data.get("audience", "")
        platform = data.get("platform", "Instagram")
        goal = data.get("goal", "Brand Awareness")
        campaign_content = data.get("campaign_content") or data.get("campaignContent") or {}
        image_url = data.get("image_url")

        if not product_name:
            return jsonify({"success": False, "error": "Product name is required."}), 400

        campaign_id = save_campaign(
            product_name=product_name,
            target_audience=audience,
            platform=platform,
            goal=goal,
            campaign_content=campaign_content,
            image_url=image_url
        )

        return jsonify({
            "success": True,
            "message": "Campaign saved successfully.",
            "id": campaign_id
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@campaign_bp.route("/<int:campaign_id>", methods=["DELETE"])
def delete_campaign_route(campaign_id):
    """Delete a campaign by ID."""
    try:
        deleted = delete_campaign(campaign_id)
        if not deleted:
            return jsonify({"success": False, "error": "Campaign not found."}), 404
        return jsonify({"success": True, "message": "Campaign deleted successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@campaign_bp.route("/stats", methods=["GET"])
def stats_route():
    """Get high level marketing stats."""
    try:
        stats = get_database_stats()
        return jsonify({"success": True, "stats": stats}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
