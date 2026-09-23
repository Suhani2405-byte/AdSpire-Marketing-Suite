from flask import Blueprint, request, jsonify

budget_bp = Blueprint("budget", __name__)

# Industry benchmark multipliers
INDUSTRY_BENCHMARKS = {
    "E-commerce & D2C": {
        "cpc": {"Meta": 0.85, "Google": 1.20, "LinkedIn": 4.50, "TikTok": 0.65, "Email": 0.15, "Influencer": 2.10},
        "ctr": {"Meta": 2.1, "Google": 3.8, "LinkedIn": 1.1, "TikTok": 2.9, "Email": 5.2, "Influencer": 4.0},
        "conv_rate": 3.2,
        "avg_order_value": 65.0
    },
    "SaaS & B2B Tech": {
        "cpc": {"Meta": 1.80, "Google": 3.50, "LinkedIn": 6.80, "TikTok": 1.20, "Email": 0.20, "Influencer": 4.00},
        "ctr": {"Meta": 1.4, "Google": 2.9, "LinkedIn": 1.8, "TikTok": 1.5, "Email": 4.5, "Influencer": 2.5},
        "conv_rate": 2.1,
        "avg_order_value": 250.0
    },
    "Fashion & Beauty": {
        "cpc": {"Meta": 0.70, "Google": 1.10, "LinkedIn": 3.90, "TikTok": 0.50, "Email": 0.12, "Influencer": 1.80},
        "ctr": {"Meta": 2.8, "Google": 3.4, "LinkedIn": 0.9, "TikTok": 3.5, "Email": 6.0, "Influencer": 5.2},
        "conv_rate": 3.8,
        "avg_order_value": 55.0
    },
    "Health & Wellness": {
        "cpc": {"Meta": 0.95, "Google": 1.60, "LinkedIn": 4.20, "TikTok": 0.75, "Email": 0.14, "Influencer": 2.30},
        "ctr": {"Meta": 2.3, "Google": 3.2, "LinkedIn": 1.2, "TikTok": 2.7, "Email": 5.0, "Influencer": 4.5},
        "conv_rate": 3.0,
        "avg_order_value": 75.0
    },
    "Education & EdTech": {
        "cpc": {"Meta": 1.10, "Google": 2.20, "LinkedIn": 5.10, "TikTok": 0.80, "Email": 0.18, "Influencer": 2.50},
        "ctr": {"Meta": 1.9, "Google": 3.1, "LinkedIn": 1.6, "TikTok": 2.4, "Email": 4.8, "Influencer": 3.2},
        "conv_rate": 2.5,
        "avg_order_value": 180.0
    },
    "Default": {
        "cpc": {"Meta": 0.90, "Google": 1.50, "LinkedIn": 4.80, "TikTok": 0.70, "Email": 0.15, "Influencer": 2.00},
        "ctr": {"Meta": 2.0, "Google": 3.2, "LinkedIn": 1.3, "TikTok": 2.6, "Email": 5.0, "Influencer": 3.8},
        "conv_rate": 2.8,
        "avg_order_value": 80.0
    }
}

# Goal based budget distribution
GOAL_WEIGHTS = {
    "Brand Awareness": {"Meta": 35, "TikTok": 30, "Influencer": 20, "Google": 10, "LinkedIn": 5, "Email": 0},
    "Lead Generation": {"Google": 35, "LinkedIn": 30, "Meta": 20, "Email": 10, "TikTok": 5, "Influencer": 0},
    "Sales": {"Meta": 35, "Google": 35, "Email": 15, "TikTok": 10, "Influencer": 5, "LinkedIn": 0},
    "Product Promotion": {"Meta": 35, "TikTok": 25, "Google": 20, "Influencer": 15, "Email": 5, "LinkedIn": 0},
    "Engagement": {"TikTok": 40, "Meta": 35, "Influencer": 15, "Google": 5, "LinkedIn": 5, "Email": 0}
}


@budget_bp.route("/plan", methods=["POST"])
def calculate_budget_plan():
    """Calculate dynamic ROI & budget allocation model."""
    try:
        data = request.get_json() or {}
        total_budget = float(data.get("total_budget", 1500) or 1500)
        goal = data.get("goal", "Sales")
        industry = data.get("industry", "E-commerce & D2C")
        duration_days = int(data.get("duration_days", 30) or 30)

        # Get benchmark metrics
        benchmarks = INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["Default"])
        weights = GOAL_WEIGHTS.get(goal, GOAL_WEIGHTS["Sales"])

        channels = []
        total_reach = 0
        total_clicks = 0
        total_conversions = 0

        for channel, pct in weights.items():
            if pct <= 0:
                continue

            allocated_amount = (total_budget * pct) / 100.0
            cpc = benchmarks["cpc"].get(channel, 1.0)
            ctr = benchmarks["ctr"].get(channel, 2.0)
            conv_rate = benchmarks["conv_rate"]

            clicks = int(allocated_amount / cpc) if cpc > 0 else 0
            # Impressions = Clicks / (CTR / 100)
            impressions = int(clicks / (ctr / 100.0)) if ctr > 0 else 0
            conversions = int(clicks * (conv_rate / 100.0))

            total_reach += impressions
            total_clicks += clicks
            total_conversions += conversions

            channels.append({
                "name": channel,
                "percentage": pct,
                "budget": round(allocated_amount, 2),
                "cpc": round(cpc, 2),
                "ctr": f"{ctr}%",
                "estimated_impressions": impressions,
                "estimated_clicks": clicks,
                "estimated_conversions": conversions
            })

        # Financial projections
        aov = benchmarks["avg_order_value"]
        projected_revenue = round(total_conversions * aov, 2)
        roas = round(projected_revenue / total_budget, 2) if total_budget > 0 else 1.0
        cpa = round(total_budget / total_conversions, 2) if total_conversions > 0 else 0
        net_profit = round(projected_revenue - total_budget, 2)

        return jsonify({
            "success": True,
            "inputs": {
                "total_budget": total_budget,
                "goal": goal,
                "industry": industry,
                "duration_days": duration_days
            },
            "summary": {
                "total_budget": total_budget,
                "total_reach": total_reach,
                "total_clicks": total_clicks,
                "total_conversions": total_conversions,
                "avg_cpa": cpa,
                "projected_revenue": projected_revenue,
                "projected_roas": f"{roas}x",
                "net_profit": net_profit,
                "daily_spend": round(total_budget / duration_days, 2)
            },
            "channels": channels,
            "strategic_tips": [
                f"Allocate highest budget ({weights.get('Meta', 35)}%) to high-intent retargeting and lookalike audiences.",
                f"Test at least 3 creative variants in week 1 to establish baseline CTR above {benchmarks['ctr']['Meta']}%.",
                f"Implement automated conversion pixel tracking before scaling to minimize CPA."
            ]
        }), 200

    except Exception as e:
        print(f"[BudgetRoutes] Error calculating plan: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
