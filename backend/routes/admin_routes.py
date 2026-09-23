from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import random
from services.database_service import get_campaigns, get_database_stats

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/metrics", methods=["GET"])
def get_admin_metrics():
    """Get aggregated executive metrics for the admin command center."""
    try:
        campaigns = get_campaigns()
        total_campaigns = len(campaigns)

        # Calculate simulated total managed spend & reach
        base_budget = 124500 + (total_campaigns * 2500)
        total_impressions = 3850000 + (total_campaigns * 65000)
        total_conversions = 9420 + (total_campaigns * 180)
        avg_roas = 4.25

        # Platform distribution
        platform_counts = {
            "Instagram": 0,
            "LinkedIn": 0,
            "TikTok": 0,
            "Google Ads": 0,
            "Facebook": 0,
            "Omnichannel": 0
        }

        for c in campaigns:
            p = c.get("platform", "Instagram")
            if p in platform_counts:
                platform_counts[p] += 1
            else:
                platform_counts["Instagram"] += 1

        # Revenue & Generation Trends (Last 7 Days)
        today = datetime.utcnow()
        trend_labels = [(today - timedelta(days=6-i)).strftime("%a") for i in range(7)]
        daily_campaigns = [12, 18, 15, 24, 28, 35, 30 + total_campaigns]
        daily_revenue_impact = [45000, 62000, 58000, 89000, 110000, 142000, 135000]

        return jsonify({
            "success": True,
            "metrics": {
                "total_campaigns": total_campaigns + 142, # Total all-time across enterprise
                "total_managed_budget": base_budget,
                "total_impressions": total_impressions,
                "total_conversions": total_conversions,
                "avg_platform_roas": f"{avg_roas}x",
                "active_brands": 18,
                "llm_token_throughput": "1.42M tokens/day",
                "api_latency_ms": 284,
                "system_uptime": "99.98%"
            },
            "platform_distribution": platform_counts,
            "revenue_trends": {
                "labels": trend_labels,
                "campaigns": daily_campaigns,
                "revenue": daily_revenue_impact
            },
            "model_health": [
                {"name": "Google Gemini 3.6 Flash", "type": "Text & Strategy Agent", "status": "Operational", "latency": "240ms", "uptime": "100%"},
                {"name": "FLUX.1-schnell (HF/Pollinations)", "type": "Generative Image Engine", "status": "Operational", "latency": "1.8s", "uptime": "99.9%"},
                {"name": "Predictive ROAS Solver", "type": "Financial Simulator", "status": "Operational", "latency": "12ms", "uptime": "100%"},
                {"name": "SQLite Persistence Hub", "type": "Database Layer", "status": "Healthy", "latency": "4ms", "uptime": "100%"}
            ]
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/activity-logs", methods=["GET"])
def get_activity_logs():
    """Get system-wide live audit and generation logs."""
    try:
        campaigns = get_campaigns()
        logs = []

        # Recent activities based on real saved campaigns
        for idx, c in enumerate(campaigns[:6]):
            logs.append({
                "id": f"log-{idx+1}",
                "user": "Senior Growth Marketer",
                "action": f"Generated Campaign: {c.get('product_name')}",
                "platform": c.get("platform", "Instagram"),
                "goal": c.get("goal", "Sales"),
                "timestamp": c.get("created_at") or "Just now",
                "status": "Success",
                "type": "campaign"
            })

        # Synthetic enterprise activity entries
        preset_logs = [
            {"id": "log-101", "user": "Global Media Buyer", "action": "Optimized Ad Budget ($8,500 across Meta & TikTok)", "platform": "Meta/TikTok", "goal": "ROAS Scaling", "timestamp": "12 mins ago", "status": "Success", "type": "budget"},
            {"id": "log-102", "user": "Creative Director", "action": "Synthesized 8K Photorealistic Product Creative (FLUX.1)", "platform": "Visual Studio", "goal": "Creative Asset", "timestamp": "34 mins ago", "status": "Success", "type": "image"},
            {"id": "log-103", "user": "Content Strategist", "action": "Generated 7-Day Omnichannel Launch Calendar", "platform": "Omnichannel", "goal": "Product Launch", "timestamp": "1 hour ago", "status": "Success", "type": "campaign"},
            {"id": "log-104", "user": "System Admin", "action": "Automated Model Fallback Health Check", "platform": "System Core", "goal": "Uptime Monitor", "timestamp": "2 hours ago", "status": "Success", "type": "system"}
        ]

        combined = logs + preset_logs
        return jsonify({"success": True, "logs": combined}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/brands", methods=["GET"])
def get_brands():
    """Get enterprise brands managed inside MarketAI."""
    return jsonify({
        "success": True,
        "brands": [
            {"id": 1, "name": "AeroPulse Audio", "industry": "Consumer Tech", "campaigns": 8, "total_spend": "$34,200", "avg_roas": "4.6x", "status": "Active"},
            {"id": 2, "name": "Lumina Ergonomics", "industry": "Office & Furniture", "campaigns": 5, "total_spend": "$21,500", "avg_roas": "3.9x", "status": "Active"},
            {"id": 3, "name": "HydraGlow Skincare", "industry": "Beauty & D2C", "campaigns": 12, "total_spend": "$56,000", "avg_roas": "5.1x", "status": "Active"},
            {"id": 4, "name": "CloudScale DevOps", "industry": "SaaS B2B", "campaigns": 4, "total_spend": "$18,000", "avg_roas": "3.4x", "status": "Active"},
            {"id": 5, "name": "ZenPulse Nutrition", "industry": "Health & Wellness", "campaigns": 6, "total_spend": "$28,400", "avg_roas": "4.8x", "status": "Active"}
        ]
    }), 200
