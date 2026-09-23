import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from routes.campaign_routes import campaign_bp
from routes.image_routes import image_bp
from routes.budget_routes import budget_bp
from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp

# Determine frontend build directory
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path="")
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register Blueprints
app.register_blueprint(campaign_bp, url_prefix="/api/campaigns")
app.register_blueprint(image_bp, url_prefix="/api/image")
app.register_blueprint(budget_bp, url_prefix="/api/budget")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(auth_bp, url_prefix="/api/auth")


# Health check / status
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "MarketAI Backend Engine",
        "version": "2.0.0",
        "modules": {
            "campaign_generator": "Online (Gemini 2.5/3.7)",
            "image_studio": "Online (FLUX.1 + Pollinations)",
            "budget_planner": "Online (Financial Simulation Engine)",
            "analytics_db": "Online (SQLite)"
        }
    }), 200


# Serve Frontend SPA in production
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if FRONTEND_DIST and os.path.exists(FRONTEND_DIST):
        target_file = os.path.join(FRONTEND_DIST, path)
        if path != "" and os.path.exists(target_file):
            return send_from_directory(FRONTEND_DIST, path)
        return send_from_directory(FRONTEND_DIST, "index.html")

    return jsonify({
        "message": "MarketAI Backend API is running successfully!",
        "endpoints": [
            "/api/campaigns/generate",
            "/api/campaigns",
            "/api/image/generate",
            "/api/budget/plan",
            "/api/health"
        ],
        "note": "To view the React UI, run Vite frontend (`npm run dev`) or build frontend (`npm run build`)."
    }), 200


@app.errorhandler(404)
def not_found(error):
    # In SPA mode, redirect to index.html if dist exists
    if FRONTEND_DIST and os.path.exists(os.path.join(FRONTEND_DIST, "index.html")):
        return send_from_directory(FRONTEND_DIST, "index.html")
    return jsonify({"success": False, "error": "Route not found."}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Internal server error."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] MarketAI Server running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)