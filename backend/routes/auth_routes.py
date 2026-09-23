from flask import Blueprint, request, jsonify
import hashlib
import time

auth_bp = Blueprint("auth", __name__)

# In-memory / Pre-seeded Enterprise User Accounts
USERS = {
    "admin@marketai.com": {
        "id": "usr_adm_01",
        "name": "Sarah Jenkins",
        "email": "admin@marketai.com",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "title": "Chief Marketing Officer / Admin",
        "avatar": "SJ",
        "brand": "MarketAI Global",
        "created_at": "2026-01-15"
    },
    "creator@marketai.com": {
        "id": "usr_mkt_01",
        "name": "Alex Rivera",
        "email": "creator@marketai.com",
        "password_hash": hashlib.sha256("creator123".encode()).hexdigest(),
        "role": "marketer",
        "title": "Lead Growth Strategist",
        "avatar": "AR",
        "brand": "AeroPulse Tech",
        "created_at": "2026-02-01"
    },
    "demo@marketai.com": {
        "id": "usr_mkt_02",
        "name": "Jordan Lee",
        "email": "demo@marketai.com",
        "password_hash": hashlib.sha256("demo123".encode()).hexdigest(),
        "role": "marketer",
        "title": "Content & Campaign Specialist",
        "avatar": "JL",
        "brand": "Lumina Brands",
        "created_at": "2026-02-10"
    }
}


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user with role-based credentials."""
    try:
        data = request.get_json() or {}
        email = data.get("email", "").strip().lower()
        password = data.get("password", "").strip()

        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required."}), 400

        user = USERS.get(email)
        if not user:
            return jsonify({"success": False, "error": "User account not found."}), 401

        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        if user["password_hash"] != pwd_hash:
            return jsonify({"success": False, "error": "Invalid password."}), 401

        # Generate session token
        token = hashlib.sha256(f"{email}-{time.time()}".encode()).hexdigest()

        return jsonify({
            "success": True,
            "message": f"Welcome back, {user['name']}!",
            "token": token,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
                "title": user["title"],
                "avatar": user["avatar"],
                "brand": user["brand"]
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@auth_bp.route("/users", methods=["GET"])
def get_users_list():
    """Get all team members for Admin User Management."""
    user_list = [
        {
            "id": u["id"],
            "name": u["name"],
            "email": u["email"],
            "role": u["role"],
            "title": u["title"],
            "avatar": u["avatar"],
            "brand": u["brand"],
            "created_at": u["created_at"],
            "status": "Active"
        }
        for u in USERS.values()
    ]
    return jsonify({"success": True, "users": user_list}), 200
