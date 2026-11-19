import os
import sys
import tempfile

import pytest

# Isolated temp database + no real AI keys, set BEFORE the app is imported
_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(_tmp, "test.db").replace("\\", "/")
os.environ["SECRET_KEY"] = "test-secret"
os.environ["ADMIN_EMAILS"] = "boss@example.com"
os.environ["GEMINI_API_KEY"] = ""
os.environ["HF_TOKEN"] = ""
# tests must never call real external services, whatever keys the developer has in .env
for _k in ("CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN", "POLLINATIONS_API_KEY",
           "PEXELS_API_KEY", "UNSPLASH_ACCESS_KEY", "PIXABAY_API_KEY"):
    os.environ[_k] = ""

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app  # noqa: E402
from services import rate_limit  # noqa: E402

FAKE_CAMPAIGN = {
    "campaign_title": "Test Title", "tagline": "Test tagline", "ad_copies": {},
    "social_posts": {}, "image_prompt": "a red mug on a table",
}


@pytest.fixture()
def client(monkeypatch):
    rate_limit.reset()

    def fake_stream(**kwargs):
        yield {"type": "status", "message": "Writing campaign with fake-model..."}
        yield {"type": "chunk", "text": '{"campaign_title":'}
        yield {"type": "done", "campaign": dict(FAKE_CAMPAIGN, campaign_title=kwargs["product_name"]),
               "meta": {"source": "gemini", "model": "fake-model", "warning": None}}

    import routes.campaign_routes as cr
    monkeypatch.setattr(cr, "stream_marketing_campaign", fake_stream)
    monkeypatch.setattr(cr, "generate_marketing_campaign",
                        lambda **kw: (dict(FAKE_CAMPAIGN, campaign_title=kw["product_name"]),
                                      {"source": "gemini", "model": "fake-model", "warning": None}))

    import routes.image_routes as ir
    monkeypatch.setattr(ir, "generate_image", lambda **kw: {
        "success": True, "image_url": "data:image/jpeg;base64,AAAA", "provider": "Fake Engine",
        "seed": 1, "style": kw["style"], "aspect_ratio": kw["aspect_ratio"], "notes": [],
    })
    return flask_app.test_client()


_counter = {"n": 0}


def register(client, email=None, password="password123", name="Test User"):
    _counter["n"] += 1
    email = email or f"user{_counter['n']}@example.com"
    r = client.post("/api/auth/register", json={"name": name, "email": email, "password": password})
    assert r.status_code == 201, r.get_json()
    data = r.get_json()
    return {"Authorization": f"Bearer {data['token']}"}, data["user"]
