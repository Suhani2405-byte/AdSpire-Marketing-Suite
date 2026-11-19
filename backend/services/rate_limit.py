"""
Small in-memory rate limiter (per process). Protects the paid/limited AI quotas
and the login endpoint from abuse. Good enough for a single Render instance.
"""
import time
import threading
from collections import defaultdict, deque
from functools import wraps

from flask import request, jsonify, g

_hits = defaultdict(deque)
_lock = threading.Lock()


def rate_limited(name, limit, window, per="user"):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if per == "user" and getattr(g, "user", None):
                who = f"u{g.user.id}"
            else:
                who = request.headers.get("X-Forwarded-For", request.remote_addr or "?").split(",")[0].strip()
            key = (name, who)
            now = time.time()
            max_hits = limit() if callable(limit) else limit  # callable -> admin-configurable
            with _lock:
                q = _hits[key]
                while q and q[0] <= now - window:
                    q.popleft()
                if len(q) >= max_hits:
                    retry = int(q[0] + window - now) + 1
                    return jsonify({"success": False,
                                    "error": f"Too many requests. Please try again in {retry}s."}), 429
                q.append(now)
            return fn(*args, **kwargs)
        return wrapper
    return deco


def reset():
    with _lock:
        _hits.clear()


# ---- failed-attempt limiting (used for login: only wrong passwords count) ----

def _client_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr or "?").split(",")[0].strip()


def failures_exceeded(name, limit, window):
    """True if this IP already has `limit` failures in the last `window` seconds."""
    key, now = (name, _client_ip()), time.time()
    with _lock:
        q = _hits[key]
        while q and q[0] <= now - window:
            q.popleft()
        return len(q) >= limit


def record_failure(name):
    with _lock:
        _hits[(name, _client_ip())].append(time.time())
