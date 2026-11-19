import os
import sys

# Log output: flush every line, and never crash on characters the console can't show.
# (On Windows the default cp1252 encoding raised UnicodeEncodeError for log lines with
# "·", "→" or emoji in photo titles, which aborted the whole image request.)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except (AttributeError, ValueError):
        pass
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from routes.campaign_routes import campaign_bp
from routes.image_routes import image_bp
from routes.budget_routes import budget_bp
from routes.admin_routes import admin_bp, settings_bp
from routes.auth_routes import auth_bp
from routes.brand_routes import brand_bp
from services.image_service import provider_status

# Determine frontend build directory
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # campaign images are sent as data URLs

# In production the React app is served by Flask from the same origin, so CORS is only
# needed for the Vite dev server (or extra origins listed in CORS_ORIGINS).
_origins = ["http://localhost:5173", "http://127.0.0.1:5173"] + [
    o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()
]
CORS(app, resources={r"/api/*": {"origins": _origins}})

# Register Blueprints
app.register_blueprint(campaign_bp, url_prefix="/api/campaigns")
app.register_blueprint(image_bp, url_prefix="/api/image")
app.register_blueprint(budget_bp, url_prefix="/api/budget")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(brand_bp, url_prefix="/api/brands")
app.register_blueprint(settings_bp, url_prefix="/api/settings")


@app.after_request
def security_headers(resp):
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "DENY")
    resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    return resp


# Health check / status (used by Render's health check)
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Adspire Backend",
        "version": "3.0.0",
        "modules": {
            "campaign_generator": "Gemini" if os.getenv("GEMINI_API_KEY") else "Template only (GEMINI_API_KEY missing)",
            "image_providers": provider_status(),
            "budget_planner": "Online",
            "database": "PostgreSQL" if os.getenv("DATABASE_URL") else "SQLite",
        }
    }), 200


# Serve Frontend SPA in production
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path.startswith("api/"):
        return jsonify({"success": False, "error": "Route not found."}), 404
    if os.path.exists(os.path.join(FRONTEND_DIST, "index.html")):
        target_file = os.path.join(FRONTEND_DIST, path)
        if path != "" and os.path.isfile(target_file):
            return send_from_directory(FRONTEND_DIST, path)
        return send_from_directory(FRONTEND_DIST, "index.html")

    return jsonify({
        "message": "Adspire Backend API is running.",
        "note": "Build the frontend (`cd frontend && npm run build`) or run `npm run dev` for the UI.",
    }), 200


@app.errorhandler(404)
def not_found(error):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Route not found."}), 404
    if os.path.exists(os.path.join(FRONTEND_DIST, "index.html")):
        return send_from_directory(FRONTEND_DIST, "index.html")
    return jsonify({"success": False, "error": "Route not found."}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"success": False, "error": "Method not allowed."}), 405


@app.errorhandler(413)
def too_large(error):
    return jsonify({"success": False, "error": "Request is too large."}), 413


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Internal server error."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Never enable the Werkzeug debugger on 0.0.0.0 by default: it allows remote code execution.
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    print(f"[*] Adspire server running on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1" if debug else "0.0.0.0", port=port, debug=debug, threaded=True)
