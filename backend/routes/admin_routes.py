"""
Admin panel API: metrics, activity, user management and app settings.
Every number here is computed from real stored data.
"""
import os

from flask import Blueprint, jsonify, request, g

from services import database_service as db
from services.auth_service import admin_required, hash_password, EMAIL_RE
from services.image_service import provider_status

admin_bp = Blueprint("admin", __name__)
settings_bp = Blueprint("settings", __name__)


# ------------------------------------------------------------ dashboard ---

@admin_bp.route("/metrics", methods=["GET"])
@admin_required
def get_admin_metrics():
    metrics = db.admin_metrics()
    metrics["system"] = {
        "database": "PostgreSQL" if not db.IS_SQLITE else "SQLite (local file)",
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "image_providers": provider_status(),
    }
    return jsonify({"success": True, **metrics}), 200


@admin_bp.route("/activity-logs", methods=["GET"])
@admin_required
def get_activity_logs():
    limit = max(1, min(request.args.get("limit", 50, type=int), 500))
    return jsonify({"success": True, "logs": db.recent_activity(limit=limit)}), 200


# --------------------------------------------------------- user management ---

@admin_bp.route("/users", methods=["GET"])
@admin_required
def get_users():
    return jsonify({"success": True, "users": db.list_users()}), 200


@admin_bp.route("/users", methods=["POST"])
@admin_required
def create_user():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    role = data.get("role", "marketer")

    if len(name) < 2:
        return jsonify({"success": False, "error": "Name is required."}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"success": False, "error": "Enter a valid email address."}), 400
    if len(password) < 8:
        return jsonify({"success": False, "error": "Password must be at least 8 characters."}), 400
    if role not in ("admin", "marketer"):
        return jsonify({"success": False, "error": "Role must be admin or marketer."}), 400
    if db.get_user_by_email(email):
        return jsonify({"success": False, "error": "An account with this email already exists."}), 409

    user = db.create_user(name=name[:120], email=email, password_hash=hash_password(password), role=role)
    db.log_activity("admin", user_id=g.user.id, detail=f"Created {role} account {email}")
    return jsonify({"success": True, "user": db.user_to_dict(user)}), 201


def _guard_self_and_last_admin(target, new_role=None, new_active=None, deleting=False):
    """Stop the admin from locking everyone out."""
    if target.id == g.user.id and (deleting or new_active is False or new_role == "marketer"):
        return "You can't disable, demote or delete your own account."
    removes_admin = target.role == "admin" and (deleting or new_active is False or new_role == "marketer")
    if removes_admin and db.count_active_admins(exclude_id=target.id) == 0:
        return "At least one active admin must remain."
    return None


@admin_bp.route("/users/<int:user_id>", methods=["PATCH"])
@admin_required
def update_user(user_id):
    target = db.get_user_by_id(user_id)
    if not target:
        return jsonify({"success": False, "error": "User not found."}), 404
    data = request.get_json(silent=True) or {}
    changes = {}

    if "name" in data:
        name = str(data["name"]).strip()
        if len(name) < 2:
            return jsonify({"success": False, "error": "Name is too short."}), 400
        changes["name"] = name[:120]
    if "role" in data:
        if data["role"] not in ("admin", "marketer"):
            return jsonify({"success": False, "error": "Role must be admin or marketer."}), 400
        changes["role"] = data["role"]
    if "is_active" in data:
        changes["is_active"] = bool(data["is_active"])

    err = _guard_self_and_last_admin(target, new_role=changes.get("role"), new_active=changes.get("is_active"))
    if err:
        return jsonify({"success": False, "error": err}), 400

    user = db.update_user(user_id, **changes)
    db.log_activity("admin", user_id=g.user.id, detail=f"Updated {target.email}: {changes}")
    return jsonify({"success": True, "user": db.user_to_dict(user)}), 200


@admin_bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@admin_required
def reset_password(user_id):
    target = db.get_user_by_id(user_id)
    if not target:
        return jsonify({"success": False, "error": "User not found."}), 404
    password = str((request.get_json(silent=True) or {}).get("password", ""))
    if len(password) < 8:
        return jsonify({"success": False, "error": "Password must be at least 8 characters."}), 400
    db.update_user(user_id, password_hash=hash_password(password))
    db.log_activity("admin", user_id=g.user.id, detail=f"Reset password for {target.email}")
    return jsonify({"success": True}), 200


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    target = db.get_user_by_id(user_id)
    if not target:
        return jsonify({"success": False, "error": "User not found."}), 404
    err = _guard_self_and_last_admin(target, deleting=True)
    if err:
        return jsonify({"success": False, "error": err}), 400
    counts = db.delete_user_cascade(user_id)
    db.log_activity("admin", user_id=g.user.id,
                    detail=f"Deleted {target.email} ({counts['campaigns']} campaigns, {counts['brands']} brands)")
    return jsonify({"success": True, "deleted": counts}), 200


# --------------------------------------------------------------- settings ---

@admin_bp.route("/settings", methods=["GET"])
@admin_required
def get_settings():
    return jsonify({"success": True, "settings": db.get_settings()}), 200


@admin_bp.route("/settings", methods=["PUT"])
@admin_required
def update_settings():
    try:
        settings = db.update_settings(request.get_json(silent=True) or {})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    db.log_activity("admin", user_id=g.user.id, detail="Updated app settings")
    return jsonify({"success": True, "settings": settings}), 200


@settings_bp.route("/public", methods=["GET"])
def public_settings():
    """What the UI needs to know before/after login (feature switches + announcement)."""
    s = db.get_settings()
    return jsonify({"success": True, "settings": {
        "registration_open": s["registration_open"] or db.count_admins() == 0,
        "campaign_generation": s["campaign_generation"],
        "image_generation": s["image_generation"],
        "budget_planner": s["budget_planner"],
        "announcement": s["announcement"],
    }}), 200
