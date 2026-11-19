from flask import Blueprint, request, jsonify, g

from services import database_service as db
from services.auth_service import (
    hash_password, verify_password, issue_token, login_required, admin_required,
    admin_emails, EMAIL_RE,
)
from services.rate_limit import rate_limited, failures_exceeded, record_failure

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
@rate_limited("register", limit=10, window=3600, per="ip")
def register():
    if not db.get_settings()["registration_open"] and db.count_admins() > 0:
        return jsonify({"success": False, "error": "New sign-ups are currently closed by the administrator."}), 403
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if len(name) < 2:
        return jsonify({"success": False, "error": "Please enter your name."}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"success": False, "error": "Please enter a valid email address."}), 400
    if len(password) < 8:
        return jsonify({"success": False, "error": "Password must be at least 8 characters."}), 400
    if db.get_user_by_email(email):
        return jsonify({"success": False, "error": "An account with this email already exists."}), 409

    # The first person to register while no admin exists becomes admin (demo seed accounts
    # are never admins), plus anyone listed in ADMIN_EMAILS.
    first_admin = db.count_admins() == 0
    role = "admin" if (email in admin_emails() or first_admin) else "marketer"
    user = db.create_user(name=name[:120], email=email, password_hash=hash_password(password), role=role)
    if first_admin:
        db.claim_orphan_campaigns(user.id)  # campaigns saved before login existed
    db.log_activity("register", user_id=user.id, detail=f"New {role} account")
    return jsonify({"success": True, "token": issue_token(user), "user": db.user_to_dict(user)}), 201


LOGIN_MAX_FAILURES, LOGIN_WINDOW = 10, 900  # 10 wrong passwords per IP per 15 minutes


@auth_bp.route("/login", methods=["POST"])
def login():
    if failures_exceeded("login_fail", LOGIN_MAX_FAILURES, LOGIN_WINDOW):
        return jsonify({"success": False, "error": "Too many failed login attempts. Please wait 15 minutes."}), 429
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required."}), 400

    user = db.get_user_by_email(email)
    # Same message for unknown email and wrong password (don't reveal which accounts exist)
    if not user or not verify_password(user.password_hash, password):
        record_failure("login_fail")
        return jsonify({"success": False, "error": "Incorrect email or password."}), 401
    if user.is_active is False:
        return jsonify({"success": False, "error": "This account has been disabled by the administrator."}), 403

    db.log_activity("login", user_id=user.id)
    return jsonify({"success": True, "token": issue_token(user), "user": db.user_to_dict(user)}), 200


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify({"success": True, "user": db.user_to_dict(g.user)}), 200


@auth_bp.route("/users", methods=["GET"])
@admin_required
def get_users_list():
    return jsonify({"success": True, "users": db.list_users()}), 200
