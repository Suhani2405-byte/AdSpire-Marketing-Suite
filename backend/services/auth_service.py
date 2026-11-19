"""
Authentication: salted password hashes (Werkzeug PBKDF2/scrypt) + signed, expiring
bearer tokens (itsdangerous). Admin role is granted to emails listed in ADMIN_EMAILS,
or to the very first account created.
"""
import os
import re
import secrets
from functools import wraps

from flask import request, jsonify, g
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash

from services import database_service as db

TOKEN_MAX_AGE = 7 * 24 * 3600  # 7 days
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

_secret = os.getenv("SECRET_KEY")
if not _secret:
    _secret = secrets.token_hex(32)
    print("[Auth] WARNING: SECRET_KEY not set; using a random key. Logins reset when the server restarts.")
_serializer = URLSafeTimedSerializer(_secret, salt="adspire-auth")


def admin_emails():
    return {e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()}


def hash_password(pw):
    return generate_password_hash(pw)


def verify_password(pw_hash, pw):
    return check_password_hash(pw_hash, pw)


def issue_token(user):
    return _serializer.dumps({"uid": user.id})


def user_from_token(token):
    try:
        data = _serializer.loads(token, max_age=TOKEN_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
    user = db.get_user_by_id(data.get("uid"))
    if user and user.is_active is False:  # disabled by an admin -> existing tokens stop working
        return None
    return user


def _current_user():
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return user_from_token(header[7:].strip())
    return None


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = _current_user()
        if not user:
            return jsonify({"success": False, "error": "Please log in to continue.", "auth": False}), 401
        g.user = user
        return fn(*args, **kwargs)
    return wrapper


def attach_optional_user(fn):
    """For public routes: set g.user when a valid token is sent, but don't require one."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        g.user = _current_user()
        return fn(*args, **kwargs)
    return wrapper


def feature_required(feature):
    """Block a route when an admin has switched the feature off (admins can still use it)."""
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = getattr(g, "user", None)
            if not db.get_settings().get(feature, True) and not (user and user.role == "admin"):
                return jsonify({"success": False, "error": "This feature has been turned off by the administrator."}), 403
            return fn(*args, **kwargs)
        return wrapper
    return deco


def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if g.user.role != "admin":
            return jsonify({"success": False, "error": "Admin access required."}), 403
        return fn(*args, **kwargs)
    return wrapper
