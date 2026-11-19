"""
Database layer (SQLAlchemy).

- Locally: SQLite file backend/marketing_campaign.db
- Production (Render): set DATABASE_URL to a Postgres URL (Neon / Supabase / Render Postgres)
  so data survives redeploys. Render's free disk is wiped on every deploy/restart.
"""
import os
import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean,
    inspect, text, func,
)
from sqlalchemy.orm import declarative_base, sessionmaker

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "marketing_campaign.db"))


def _database_url():
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        return f"sqlite:///{DB_PATH}"
    # Heroku/Render style URLs -> SQLAlchemy psycopg3 driver
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    elif not url.startswith(("sqlite", "postgresql+psycopg://")):
        # Unrecognised format (e.g. Render internal ref) — fall back to SQLite
        print(f"[WARNING] DATABASE_URL format not recognised, falling back to SQLite")
        return f"sqlite:///{DB_PATH}"
    return url


DATABASE_URL = _database_url()
IS_SQLITE = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if IS_SQLITE else {},
    pool_pre_ping=True,
)

Base = declarative_base()


def _utcnow():
    """Naive UTC timestamp (works the same on SQLite and Postgres)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(300), nullable=False)
    role = Column(String(20), nullable=False, default="marketer")  # marketer | admin
    is_active = Column(Boolean, nullable=False, default=True)  # admins can disable accounts
    created_at = Column(DateTime, default=_utcnow)


class Setting(Base):
    """Admin-controlled app settings (feature switches, limits, announcement)."""
    __tablename__ = "settings"

    key = Column(String(60), primary_key=True)
    value = Column(Text, nullable=False)  # JSON-encoded


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    product_name = Column(String(200), nullable=False)
    target_audience = Column(String(300))
    platform = Column(String(100))
    goal = Column(String(100), default="Brand Awareness")
    campaign_content = Column(Text)  # JSON string
    image_url = Column(Text, nullable=True)
    image_thumb = Column(Text, nullable=True)  # small JPEG data URL for library cards
    source = Column(String(40), nullable=True)  # gemini model name or "template"
    created_at = Column(DateTime, default=_utcnow)


def make_thumb(image_url, size=420):
    """Small JPEG (data URL) for library cards, so listing campaigns doesn't ship full-size images.
    https URLs (e.g. Unsplash hotlinks) are returned unchanged."""
    if not image_url:
        return None
    if not image_url.startswith("data:image/"):
        return image_url
    try:
        import base64
        import io
        from PIL import Image
        raw = base64.b64decode(image_url.split(",", 1)[1])
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        img.thumbnail((size, size))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=78, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print(f"[DB] thumbnail failed: {e}")
        return None


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    industry = Column(String(100))
    tone = Column(String(100))
    audience = Column(String(300))
    description = Column(Text)
    created_at = Column(DateTime, default=_utcnow)


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(40), nullable=False)  # campaign | image | image_failed | login | register
    detail = Column(String(300))
    provider = Column(String(80))
    duration_ms = Column(Float)
    created_at = Column(DateTime, default=_utcnow, index=True)


def _migrate():
    """Add columns introduced after the first version to an existing database."""
    insp = inspect(engine)
    if "campaigns" in insp.get_table_names():
        cols = {c["name"] for c in insp.get_columns("campaigns")}
        with engine.begin() as conn:
            if "user_id" not in cols:
                conn.execute(text("ALTER TABLE campaigns ADD COLUMN user_id INTEGER"))
            if "source" not in cols:
                conn.execute(text("ALTER TABLE campaigns ADD COLUMN source VARCHAR(40)"))
            if "image_thumb" not in cols:
                conn.execute(text("ALTER TABLE campaigns ADD COLUMN image_thumb TEXT"))
    if "users" in insp.get_table_names():
        cols = {c["name"] for c in insp.get_columns("users")}
        if "is_active" not in cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE"))


Base.metadata.create_all(engine)
_migrate()


def _backfill_thumbs():
    with SessionLocal() as s:
        rows = s.query(Campaign).filter(Campaign.image_url.isnot(None), Campaign.image_thumb.is_(None)).all()
        for c in rows:
            c.image_thumb = make_thumb(c.image_url)
        if rows:
            s.commit()
            print(f"[DB] created thumbnails for {len(rows)} campaigns")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
_backfill_thumbs()


def _fmt(dt):
    return dt.strftime("%Y-%m-%d %H:%M") if dt else None


# ------------------------------------------------------------------ users ---

def user_to_dict(u):
    return {
        "id": u.id, "name": u.name, "email": u.email, "role": u.role,
        "is_active": bool(u.is_active) if u.is_active is not None else True,
        "avatar": "".join(p[0] for p in u.name.split()[:2]).upper() or "U",
        "created_at": _fmt(u.created_at),
    }


def create_user(name, email, password_hash, role="marketer"):
    with SessionLocal() as s:
        u = User(name=name, email=email, password_hash=password_hash, role=role)
        s.add(u)
        s.commit()
        return u


def claim_orphan_campaigns(user_id):
    """Give campaigns created before accounts existed to this user (used for the first admin)."""
    with SessionLocal() as s:
        n = s.query(Campaign).filter(Campaign.user_id.is_(None)).update({Campaign.user_id: user_id})
        s.commit()
        return n


def get_user_by_email(email):
    with SessionLocal() as s:
        return s.query(User).filter(User.email == email).first()


def get_user_by_id(user_id):
    with SessionLocal() as s:
        return s.get(User, user_id)


def list_users():
    with SessionLocal() as s:
        rows = (
            s.query(User, func.count(Campaign.id))
            .outerjoin(Campaign, Campaign.user_id == User.id)
            .group_by(User.id)
            .order_by(User.created_at.desc())
            .all()
        )
        return [dict(user_to_dict(u), campaigns=n) for u, n in rows]


def count_users():
    with SessionLocal() as s:
        return s.query(User).count()


def count_admins():
    with SessionLocal() as s:
        return s.query(User).filter(User.role == "admin").count()


# -------------------------------------------------------------- campaigns ---

def _campaign_to_dict(c, include_image=True):
    try:
        parsed = json.loads(c.campaign_content)
    except Exception:
        parsed = c.campaign_content
    return {
        "id": c.id,
        "user_id": c.user_id,
        "product_name": c.product_name,
        "target_audience": c.target_audience,
        "platform": c.platform,
        "goal": c.goal or "Brand Awareness",
        "campaign_content": parsed,
        "image_url": c.image_url if include_image else None,
        "image_thumb": c.image_thumb or (c.image_url if c.image_url and not c.image_url.startswith("data:") else None),
        "has_image": bool(c.image_url),
        "source": c.source,
        "created_at": _fmt(c.created_at),
    }


def save_campaign(product_name, target_audience, platform, goal, campaign_content,
                  image_url=None, user_id=None, source=None):
    content_str = json.dumps(campaign_content) if isinstance(campaign_content, (dict, list)) else str(campaign_content)
    with SessionLocal() as s:
        c = Campaign(
            user_id=user_id, product_name=product_name, target_audience=target_audience,
            platform=platform, goal=goal, campaign_content=content_str,
            image_url=image_url, image_thumb=make_thumb(image_url), source=source,
        )
        s.add(c)
        s.commit()
        return c.id


def get_campaigns(user_id=None):
    """user_id=None returns every campaign (admin / internal use)."""
    with SessionLocal() as s:
        q = s.query(Campaign, User.name).outerjoin(User, User.id == Campaign.user_id)
        if user_id is not None:
            q = q.filter(Campaign.user_id == user_id)
        return [
            dict(_campaign_to_dict(c, include_image=False), owner_name=owner or "Unassigned")
            for c, owner in q.order_by(Campaign.created_at.desc()).all()
        ]


def get_campaign_by_id(campaign_id, user_id=None):
    with SessionLocal() as s:
        c = s.get(Campaign, campaign_id)
        if not c or (user_id is not None and c.user_id != user_id):
            return None
        return _campaign_to_dict(c)


def update_campaign_image(campaign_id, image_url, user_id=None):
    with SessionLocal() as s:
        c = s.get(Campaign, campaign_id)
        if not c or (user_id is not None and c.user_id != user_id):
            return False
        c.image_url = image_url
        c.image_thumb = make_thumb(image_url)
        s.commit()
        return True


def delete_campaign(campaign_id, user_id=None):
    with SessionLocal() as s:
        c = s.get(Campaign, campaign_id)
        if not c or (user_id is not None and c.user_id != user_id):
            return False
        s.delete(c)
        s.commit()
        return True


def get_database_stats(user_id=None):
    with SessionLocal() as s:
        q = s.query(Campaign)
        if user_id is not None:
            q = q.filter(Campaign.user_id == user_id)
        return {"total_campaigns": q.count()}


# ----------------------------------------------------------------- brands ---

def _brand_to_dict(b):
    return {
        "id": b.id, "name": b.name, "industry": b.industry, "tone": b.tone,
        "audience": b.audience, "description": b.description, "created_at": _fmt(b.created_at),
    }


def list_brands(user_id):
    with SessionLocal() as s:
        rows = s.query(Brand).filter(Brand.user_id == user_id).order_by(Brand.name).all()
        return [_brand_to_dict(b) for b in rows]


def create_brand(user_id, **fields):
    with SessionLocal() as s:
        b = Brand(user_id=user_id, **fields)
        s.add(b)
        s.commit()
        return _brand_to_dict(b)


def update_brand(brand_id, user_id, **fields):
    with SessionLocal() as s:
        b = s.get(Brand, brand_id)
        if not b or b.user_id != user_id:
            return None
        for k, v in fields.items():
            setattr(b, k, v)
        s.commit()
        return _brand_to_dict(b)


def delete_brand(brand_id, user_id):
    with SessionLocal() as s:
        b = s.get(Brand, brand_id)
        if not b or b.user_id != user_id:
            return False
        s.delete(b)
        s.commit()
        return True


# --------------------------------------------------------------- activity ---

def log_activity(action, user_id=None, detail=None, provider=None, duration_ms=None):
    try:
        with SessionLocal() as s:
            s.add(ActivityLog(action=action, user_id=user_id, detail=(detail or "")[:300],
                              provider=provider, duration_ms=duration_ms))
            s.commit()
    except Exception as e:  # logging must never break a request
        print(f"[DB] activity log failed: {e}")


def recent_activity(limit=25):
    with SessionLocal() as s:
        rows = (
            s.query(ActivityLog, User.name)
            .outerjoin(User, User.id == ActivityLog.user_id)
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
            .all()
        )
        return [{
            "id": a.id, "user": name or "Unknown", "action": a.action, "detail": a.detail,
            "provider": a.provider, "duration_ms": round(a.duration_ms) if a.duration_ms else None,
            "timestamp": _fmt(a.created_at),
        } for a, name in rows]


def admin_metrics():
    """Aggregates computed from real stored data only."""
    now = _utcnow()
    start = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
    with SessionLocal() as s:
        total_users = s.query(User).count()
        total_campaigns = s.query(Campaign).count()
        with_images = s.query(Campaign).filter(Campaign.image_url.isnot(None)).count()
        template_campaigns = s.query(Campaign).filter(Campaign.source == "template").count()

        platforms = dict(
            s.query(Campaign.platform, func.count(Campaign.id)).group_by(Campaign.platform).all()
        )
        goals = dict(s.query(Campaign.goal, func.count(Campaign.id)).group_by(Campaign.goal).all())

        recent_campaigns = s.query(Campaign.created_at).filter(Campaign.created_at >= start).all()
        recent_logs = s.query(ActivityLog.action, ActivityLog.created_at, ActivityLog.provider,
                              ActivityLog.duration_ms).filter(ActivityLog.created_at >= start).all()

    labels, by_day_campaigns, by_day_images = [], [], []
    for i in range(7):
        day = (start + timedelta(days=i)).date()
        labels.append(day.strftime("%a %d"))
        by_day_campaigns.append(sum(1 for (d,) in recent_campaigns if d and d.date() == day))
        by_day_images.append(sum(1 for a, d, _, _ in recent_logs if a == "image" and d.date() == day))

    providers, durations = {}, {"campaign": [], "image": []}
    image_failures = 0
    for a, _, p, ms in recent_logs:
        if a == "image" and p:
            providers[p] = providers.get(p, 0) + 1
        if a == "image_failed":
            image_failures += 1
        if a in durations and ms:
            durations[a].append(ms)

    avg = lambda xs: round(sum(xs) / len(xs) / 1000, 1) if xs else None
    images_7d = sum(by_day_images)
    return {
        "totals": {
            "users": total_users,
            "campaigns": total_campaigns,
            "campaigns_with_images": with_images,
            "template_fallback_campaigns": template_campaigns,
            "images_7d": images_7d,
            "image_failures_7d": image_failures,
            "image_success_rate_7d": (
                round(100 * images_7d / (images_7d + image_failures)) if images_7d + image_failures else None
            ),
            "avg_campaign_seconds_7d": avg(durations["campaign"]),
            "avg_image_seconds_7d": avg(durations["image"]),
        },
        "platform_distribution": {k or "Unknown": v for k, v in platforms.items()},
        "goal_distribution": {k or "Unknown": v for k, v in goals.items()},
        "image_providers_7d": providers,
        "trend": {"labels": labels, "campaigns": by_day_campaigns, "images": by_day_images},
    }


# ------------------------------------------------------- admin: user mgmt ---

def update_user(user_id, **fields):
    allowed = {"name", "role", "is_active", "password_hash"}
    with SessionLocal() as s:
        u = s.get(User, user_id)
        if not u:
            return None
        for k, v in fields.items():
            if k in allowed:
                setattr(u, k, v)
        s.commit()
        return u


def delete_user_cascade(user_id):
    """Delete a user together with their campaigns, brands and activity."""
    with SessionLocal() as s:
        u = s.get(User, user_id)
        if not u:
            return None
        counts = {
            "campaigns": s.query(Campaign).filter(Campaign.user_id == user_id).delete(synchronize_session=False),
            "brands": s.query(Brand).filter(Brand.user_id == user_id).delete(synchronize_session=False),
        }
        s.query(ActivityLog).filter(ActivityLog.user_id == user_id).delete(synchronize_session=False)
        s.delete(u)
        s.commit()
        return counts


def count_active_admins(exclude_id=None):
    with SessionLocal() as s:
        q = s.query(User).filter(User.role == "admin", User.is_active.is_(True))
        if exclude_id is not None:
            q = q.filter(User.id != exclude_id)
        return q.count()


# ------------------------------------------------------- admin: settings ---

DEFAULT_SETTINGS = {
    "registration_open": True,
    "campaign_generation": True,
    "image_generation": True,
    "budget_planner": True,
    "campaign_limit_per_hour": 20,
    "image_limit_per_hour": 30,
    "announcement": "",
}


def get_settings():
    settings = dict(DEFAULT_SETTINGS)
    with SessionLocal() as s:
        for row in s.query(Setting).all():
            if row.key in settings:
                try:
                    settings[row.key] = json.loads(row.value)
                except ValueError:
                    pass
    return settings


def update_settings(changes):
    """Validate and store setting changes. Returns the full settings dict."""
    clean = {}
    for k, v in changes.items():
        if k not in DEFAULT_SETTINGS:
            continue
        default = DEFAULT_SETTINGS[k]
        if isinstance(default, bool):
            clean[k] = bool(v)
        elif isinstance(default, int):
            try:
                clean[k] = max(1, min(int(v), 1000))
            except (TypeError, ValueError):
                raise ValueError(f"{k} must be a whole number")
        else:
            clean[k] = str(v or "")[:300]
    with SessionLocal() as s:
        for k, v in clean.items():
            row = s.get(Setting, k)
            if row:
                row.value = json.dumps(v)
            else:
                s.add(Setting(key=k, value=json.dumps(v)))
        s.commit()
    return get_settings()
