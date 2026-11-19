import json

from conftest import register
from services.image_service import build_prompt, generate_image


# ---------------------------------------------------------------- auth ---

def test_register_login_me(client):
    headers, user = register(client, email="alice@example.com")
    assert user["email"] == "alice@example.com"

    r = client.post("/api/auth/login", json={"email": "ALICE@example.com", "password": "password123"})
    assert r.status_code == 200
    token = r.get_json()["token"]

    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.get_json()["user"]["email"] == "alice@example.com"


def test_login_rejects_wrong_password_and_unknown_user(client):
    register(client, email="bob@example.com")
    r1 = client.post("/api/auth/login", json={"email": "bob@example.com", "password": "wrong-pass"})
    r2 = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "whatever1"})
    assert r1.status_code == r2.status_code == 401
    assert r1.get_json()["error"] == r2.get_json()["error"]  # don't leak which emails exist


def test_register_validation(client):
    assert client.post("/api/auth/register", json={"name": "X Y", "email": "bad", "password": "password123"}).status_code == 400
    assert client.post("/api/auth/register", json={"name": "X Y", "email": "a@b.co", "password": "short"}).status_code == 400
    register(client, email="dup@example.com")
    r = client.post("/api/auth/register", json={"name": "Dup", "email": "dup@example.com", "password": "password123"})
    assert r.status_code == 409


def test_protected_routes_need_token(client):
    assert client.get("/api/campaigns").status_code == 401
    assert client.post("/api/image/generate", json={"prompt": "x"}).status_code == 401
    assert client.get("/api/campaigns", headers={"Authorization": "Bearer forged"}).status_code == 401


def test_admin_role(client):
    admin_headers, admin = register(client, email="boss@example.com")
    assert admin["role"] == "admin"
    user_headers, user = register(client)
    assert user["role"] == "marketer"
    assert client.get("/api/admin/metrics", headers=user_headers).status_code == 403
    r = client.get("/api/admin/metrics", headers=admin_headers)
    assert r.status_code == 200 and "totals" in r.get_json()
    assert client.get("/api/admin/activity-logs", headers=admin_headers).status_code == 200


# ----------------------------------------------------------- campaigns ---

def test_campaign_generate_save_and_isolation(client):
    h1, _ = register(client)
    h2, _ = register(client)

    r = client.post("/api/campaigns/generate", headers=h1, json={"product_name": "Mug", "description": "A mug"})
    body = r.get_json()
    assert r.status_code == 200 and body["source"] == "gemini" and body["campaign_id"]
    cid = body["campaign_id"]

    assert client.get(f"/api/campaigns/{cid}", headers=h1).status_code == 200
    # another user can't read, modify or delete it
    assert client.get(f"/api/campaigns/{cid}", headers=h2).status_code == 404
    assert client.delete(f"/api/campaigns/{cid}", headers=h2).status_code == 404
    assert client.get("/api/campaigns", headers=h2).get_json()["count"] == 0

    r = client.put(f"/api/campaigns/{cid}/image", headers=h1, json={"image_url": "data:image/jpeg;base64,AAAA"})
    assert r.status_code == 200
    assert client.get(f"/api/campaigns/{cid}", headers=h1).get_json()["campaign"]["image_url"].startswith("data:image")
    assert client.put(f"/api/campaigns/{cid}/image", headers=h1, json={"image_url": "javascript:alert(1)"}).status_code == 400

    assert client.delete(f"/api/campaigns/{cid}", headers=h1).status_code == 200
    assert client.get(f"/api/campaigns/{cid}", headers=h1).status_code == 404


def test_campaign_requires_fields(client):
    h, _ = register(client)
    assert client.post("/api/campaigns/generate", headers=h, json={}).status_code == 400
    assert client.post("/api/campaigns/generate", headers=h, json={"product_name": "X"}).status_code == 400


def test_campaign_stream(client):
    h, _ = register(client)
    r = client.post("/api/campaigns/generate-stream", headers=h, json={"product_name": "Lamp", "description": "A lamp"})
    assert r.status_code == 200 and r.mimetype == "text/event-stream"
    events = [json.loads(line[6:]) for line in r.get_data(as_text=True).splitlines() if line.startswith("data: ")]
    assert [e["type"] for e in events] == ["status", "chunk", "done"]
    assert events[-1]["campaign_content"]["campaign_title"] == "Lamp"
    assert events[-1]["campaign_id"]


# -------------------------------------------------------------- brands ---

def test_brand_crud(client):
    h, _ = register(client)
    r = client.post("/api/brands", headers=h, json={"name": "Acme", "tone": "Witty & Engaging"})
    assert r.status_code == 201
    bid = r.get_json()["brand"]["id"]
    assert client.put(f"/api/brands/{bid}", headers=h, json={"name": "Acme 2"}).get_json()["brand"]["name"] == "Acme 2"
    other, _ = register(client)
    assert client.delete(f"/api/brands/{bid}", headers=other).status_code == 404
    assert client.delete(f"/api/brands/{bid}", headers=h).status_code == 200
    assert client.post("/api/brands", headers=h, json={}).status_code == 400


# --------------------------------------------------------------- image ---

def test_image_route(client):
    h, _ = register(client)
    assert client.post("/api/image/generate", headers=h, json={"prompt": ""}).status_code == 400
    r = client.post("/api/image/generate", headers=h, json={"prompt": "blue bicycle", "aspect_ratio": "16:9"})
    assert r.status_code == 200 and r.get_json()["aspect_ratio"] == "16:9"


def test_image_prompt_keeps_user_subject():
    p = build_prompt("a blue bicycle leaning on a brick wall", "Cyberpunk")
    assert p.startswith("a blue bicycle leaning on a brick wall")
    assert "no woman" not in p.lower() and "no man" not in p.lower()


def test_image_service_never_returns_stock_photo(monkeypatch):
    import services.image_service as svc
    for name in ("_try_gemini", "_try_hf", "_try_pollinations"):
        monkeypatch.setattr(svc, name, lambda *a, **k: None)
    res = generate_image("a purple giraffe", seed=5)
    assert res["success"] is False and "unsplash" not in json.dumps(res)


# -------------------------------------------------------------- budget ---

def test_budget_plan(client):
    r = client.post("/api/budget/plan", json={"total_budget": 5000, "goal": "Lead Generation",
                                              "industry": "SaaS & B2B Technology", "duration_days": 30})
    body = r.get_json()
    assert r.status_code == 200
    assert sum(c["percentage"] for c in body["channels"]) == 100
    assert "Google" in body["strategic_tips"][1]  # top channel for lead gen
    assert client.post("/api/budget/plan", json={"total_budget": -1}).status_code == 400
    assert client.post("/api/budget/plan", json={"total_budget": "abc"}).status_code == 400


def test_unknown_api_route_is_json_404(client):
    r = client.get("/api/does-not-exist")
    assert r.status_code == 404 and r.get_json()["success"] is False


# ---------------------------------------------------------------- seed ---

def test_demo_seed_and_clear(client):
    import seed_demo_data as seed
    from services import database_service as db

    before = db.get_database_stats()["total_campaigns"]
    n = len(seed.PRODUCTS)
    seed.seed(n + 25)   # more than there are products: capped at one campaign per product
    assert db.get_database_stats()["total_campaigns"] == before + n
    names = [c["product_name"] for c in db.get_campaigns() if c.get("source") == seed.SEED_SOURCE]
    assert len(names) == len(set(names)) == n          # no repeated demo product
    seed.seed(5)    # running again never duplicates a product
    assert db.get_database_stats()["total_campaigns"] == before + n
    demo = db.get_user_by_email("aarav@demo.adspire.app")
    assert demo and demo.role == "marketer"

    r = client.post("/api/auth/login", json={"email": "aarav@demo.adspire.app", "password": seed.DEMO_PASSWORD})
    assert r.status_code == 200

    seed.clear()
    assert db.get_database_stats()["total_campaigns"] == before
    assert db.get_user_by_email("aarav@demo.adspire.app") is None


# ------------------------------------------------------- admin controls ---

def _admin(client):
    from conftest import _counter
    _counter["n"] += 1
    email = f"admin{_counter['n']}@example.com"
    from services import database_service as db
    h, u = register(client, email=email)
    db.update_user(u["id"], role="admin")
    return h, u


def test_admin_user_management(client):
    ah, admin = _admin(client)
    # create
    r = client.post("/api/admin/users", headers=ah, json={"name": "New Person", "email": "newp@example.com", "password": "password123"})
    assert r.status_code == 201
    uid = r.get_json()["user"]["id"]
    # disable -> cannot log in, old token stops working
    login = client.post("/api/auth/login", json={"email": "newp@example.com", "password": "password123"}).get_json()
    uh = {"Authorization": "Bearer " + login["token"]}
    assert client.patch(f"/api/admin/users/{uid}", headers=ah, json={"is_active": False}).status_code == 200
    assert client.post("/api/auth/login", json={"email": "newp@example.com", "password": "password123"}).status_code == 403
    assert client.get("/api/auth/me", headers=uh).status_code == 401
    # re-enable + reset password
    client.patch(f"/api/admin/users/{uid}", headers=ah, json={"is_active": True})
    assert client.post(f"/api/admin/users/{uid}/reset-password", headers=ah, json={"password": "brandnew123"}).status_code == 200
    assert client.post("/api/auth/login", json={"email": "newp@example.com", "password": "brandnew123"}).status_code == 200
    # promote
    assert client.patch(f"/api/admin/users/{uid}", headers=ah, json={"role": "admin"}).get_json()["user"]["role"] == "admin"
    # delete with data
    client.patch(f"/api/admin/users/{uid}", headers=ah, json={"role": "marketer"})
    assert client.delete(f"/api/admin/users/{uid}", headers=ah).status_code == 200
    assert client.post("/api/auth/login", json={"email": "newp@example.com", "password": "brandnew123"}).status_code == 401
    # self-protection
    assert client.delete(f"/api/admin/users/{admin['id']}", headers=ah).status_code == 400
    assert client.patch(f"/api/admin/users/{admin['id']}", headers=ah, json={"role": "marketer"}).status_code == 400


def test_admin_settings_control_features(client):
    ah, _ = _admin(client)
    mh, _ = register(client)
    r = client.put("/api/admin/settings", headers=ah, json={"image_generation": False, "announcement": "Maintenance tonight", "image_limit_per_hour": 2})
    assert r.status_code == 200 and r.get_json()["settings"]["image_generation"] is False
    pub = client.get("/api/settings/public").get_json()["settings"]
    assert pub["image_generation"] is False and pub["announcement"] == "Maintenance tonight"
    # marketer blocked, admin still allowed
    assert client.post("/api/image/generate", headers=mh, json={"prompt": "x"}).status_code == 403
    assert client.post("/api/image/generate", headers=ah, json={"prompt": "x"}).status_code == 200
    # limit is applied
    client.put("/api/admin/settings", headers=ah, json={"image_generation": True})
    codes = [client.post("/api/image/generate", headers=mh, json={"prompt": "x"}).status_code for _ in range(3)]
    assert codes == [200, 200, 429]
    # registration switch
    client.put("/api/admin/settings", headers=ah, json={"registration_open": False})
    r = client.post("/api/auth/register", json={"name": "Late", "email": "late@example.com", "password": "password123"})
    assert r.status_code == 403
    # marketers can't change settings; reset for other tests
    assert client.put("/api/admin/settings", headers=mh, json={"registration_open": True}).status_code == 403
    client.put("/api/admin/settings", headers=ah, json={"registration_open": True, "image_limit_per_hour": 30, "announcement": ""})


def test_admin_sees_all_campaigns(client):
    ah, _ = _admin(client)
    mh, _ = register(client)
    cid = client.post("/api/campaigns/generate", headers=mh, json={"product_name": "Hat", "description": "A hat"}).get_json()["campaign_id"]
    all_ids = [c["id"] for c in client.get("/api/campaigns", headers=ah).get_json()["campaigns"]]
    assert cid in all_ids
    assert client.delete(f"/api/campaigns/{cid}", headers=ah).status_code == 200


# ------------------------------------------------- image verification ---

def _fake_candidate(*a, **k):
    return {"image_url": "data:image/jpeg;base64,AAAA", "provider": "Fake", "_raw": b"x", "_mime": "image/jpeg"}


def test_wrong_image_is_never_shown(monkeypatch):
    import services.image_service as svc
    monkeypatch.setattr(svc, "_try_gemini", lambda *a, **k: None)
    monkeypatch.setattr(svc, "_try_hf", lambda *a, **k: None)
    monkeypatch.setattr(svc, "_try_pollinations", _fake_candidate)
    monkeypatch.setattr(svc, "refine_prompt", lambda p, s: ("wireless earbuds product shot", "wireless earbuds", False, "wireless earbuds, product packshot"))
    calls = []
    def fake_verify(raw, mime, subject, people, **kw):
        calls.append(subject)
        return False, "a portrait of a woman"
    monkeypatch.setattr(svc, "verify_image", fake_verify)
    res = svc.generate_image("JBL earbuds", seed=99)
    assert res["success"] is False and "woman" in res["error"] and "image_url" not in res
    assert len(calls) == svc.MAX_ATTEMPTS


def test_retry_after_wrong_image_succeeds(monkeypatch):
    import services.image_service as svc
    monkeypatch.setattr(svc, "_try_gemini", lambda *a, **k: None)
    monkeypatch.setattr(svc, "_try_hf", lambda *a, **k: None)
    monkeypatch.setattr(svc, "_try_pollinations", _fake_candidate)
    monkeypatch.setattr(svc, "refine_prompt", lambda p, s: ("wireless earbuds product shot", "wireless earbuds", False, "wireless earbuds, product packshot"))
    answers = iter([(False, "a woman"), (True, "black earbuds in a case")])
    monkeypatch.setattr(svc, "verify_image", lambda *a: next(answers))
    res = svc.generate_image("JBL earbuds", seed=123)
    assert res["success"] and res["attempts"] == 2 and res["verified"] is True and "_raw" not in res


# ------------------------------------------------------ real product photos ---

def test_branded_prompt_uses_verified_real_photo(monkeypatch):
    import services.image_service as svc
    import services.photo_service as ps
    monkeypatch.setattr(svc, "refine_prompt", lambda p, s: ("x", "speakers", False, "x"))
    svc._brand_info["Bowers & Wilkins speakers"] = {"brand": "Bowers & Wilkins", "search_query": "Bowers Wilkins speaker",
                                                   "branded_subject": "Bowers & Wilkins speakers"}
    seen = {}
    def fake_find(query, subject, verify, deadline, **kw):
        seen["query"], seen["subject"] = query, subject
        return {"image_url": "data:image/jpeg;base64,AAAA", "provider": "Real photo · Openverse / Flickr", "kind": "photo",
                "aspect_ratio": "16:9", "attribution": {"creator": "A", "license": "CC BY 2.0"}}, []
    monkeypatch.setattr(ps, "find_product_photo", fake_find)
    res = svc.generate_image("Bowers & Wilkins speakers", seed=5)
    assert res["success"] and res["kind"] == "photo" and seen["query"][0] == "Bowers Wilkins speaker"
    assert res["attribution"]["license"] == "CC BY 2.0"


def test_photo_mode_without_match_returns_error_not_wrong_image(monkeypatch):
    import services.image_service as svc
    import services.photo_service as ps
    monkeypatch.setattr(svc, "refine_prompt", lambda p, s: ("x", "gadget", False, "x"))
    monkeypatch.setattr(ps, "find_product_photo", lambda *a, **k: (None, ["No real photos found"]))
    res = svc.generate_image("Some Unknown Brand gadget", seed=6, mode="photo")
    assert res["success"] is False and "image_url" not in res


def test_photo_service_picks_first_verified_candidate(monkeypatch):
    import services.photo_service as ps
    cands = [{"url": f"u{i}", "check_url": f"c{i}", "width": 2000, "height": 1500, "title": f"t{i}", "creator": "c",
              "license": "CC BY", "license_url": "", "page_url": "", "source": "Openverse / Flickr", "commercial_ok": True}
             for i in range(3)]
    monkeypatch.setattr(ps, "SOURCES", [("Fake", lambda q: cands)])
    monkeypatch.setattr(ps, "_download", lambda url, max_side=2048: (b"img-" + url.encode(), "image/jpeg", (2000, 1500)))
    verdicts = {b"img-c0": (False, "a cat"), b"img-c1": (True, "speaker"), b"img-c2": (True, "speaker")}
    res, notes = ps.find_product_photo("q", "speaker", lambda raw, mime, subj: verdicts[raw], deadline=10**12)
    assert res and res["attribution"]["title"] == "t1" and res["aspect_ratio"] == "1:1"


def test_photo_search_tries_broader_wording(monkeypatch):
    import services.photo_service as ps
    asked = []
    def fake_source(q):
        asked.append(q)
        if q != "JBL earbuds":
            return []
        return [{"url": "u", "check_url": "c", "width": 1024, "height": 683, "title": "JBL Earbuds", "creator": "x",
                 "license": "CC BY 2.0", "license_url": "", "page_url": "", "source": "Openverse / Flickr", "commercial_ok": True}]
    monkeypatch.setattr(ps, "SOURCES", [("Fake", fake_source)])
    monkeypatch.setattr(ps, "_download", lambda url, max_side=2048: (b"img", "image/jpeg", (1024, 683)))
    q = ps.query_variants("JBL wireless earbuds", "JBL", "wireless earbuds")
    res, _ = ps.find_product_photo(q, "JBL earbuds", lambda *a: (True, "earbuds"), deadline=10**12)
    assert res and asked[0] == "JBL wireless earbuds" and "JBL earbuds" in asked


def test_successful_logins_are_not_rate_limited_but_failures_are(client):
    register(client, email="many@example.com")
    for _ in range(30):
        assert client.post("/api/auth/login", json={"email": "many@example.com", "password": "password123"}).status_code == 200
    codes = [client.post("/api/auth/login", json={"email": "many@example.com", "password": "wrong-pass"}).status_code for _ in range(11)]
    assert codes[:10] == [401] * 10 and codes[10] == 429


def test_photo_service_prefers_best_scored_photo_and_skips_weak_ones(monkeypatch):
    import services.photo_service as ps
    cands = [{"url": f"u{i}", "check_url": f"c{i}", "width": 3000 - i, "height": 2000, "title": t, "creator": "c",
              "license": "CC BY", "license_url": "", "page_url": "", "source": "Openverse", "commercial_ok": True}
             for i, t in enumerate(["speaker in a car door", "speaker on a stand", "speaker in a crowd"])]
    monkeypatch.setattr(ps, "SOURCES", [("Fake", lambda q: cands)])
    monkeypatch.setattr(ps, "_download", lambda url, max_side=2048: (url.encode(), "image/jpeg", (2000, 1500)))
    scores = {b"c0": 3, b"c1": 9, b"c2": 4}
    verify = lambda raw, mime, subj: (True, "speaker", scores[raw])
    res, _ = ps.find_product_photo("q", "speaker", verify, deadline=10**12, min_score=5)
    assert res["attribution"]["title"] == "speaker on a stand"
    weak = {b"c0": 3, b"c1": 2, b"c2": 4}
    res, notes = ps.find_product_photo("q", "speaker", lambda r, m, s: (True, "x", weak[r]), deadline=10**12, min_score=5)
    assert res is None and "scored only" in notes[-2]


def test_logging_unicode_never_breaks_requests(capsys):
    # app.py reconfigures stdout to UTF-8 with errors="replace"; printing these must not raise
    print("[PhotoService] using 'Real photo · Openverse → JBL ✓ 🎧'")
    assert "Openverse" in capsys.readouterr().out


def test_auto_mode_skips_photo_search_for_described_scenes(monkeypatch):
    import services.image_service as svc
    import services.photo_service as ps
    monkeypatch.setattr(svc, "refine_prompt", lambda p, s: ("speaker product shot", "bluetooth speaker", False, "x"))
    svc._brand_info["JBL speaker on dark surface with orange lighting and smoke"] = {
        "brand": "JBL", "search_query": "JBL speaker", "branded_subject": "JBL speaker", "custom_scene": True}
    called = []
    monkeypatch.setattr(ps, "find_product_photo", lambda *a, **k: called.append(1) or (None, []))
    monkeypatch.setattr(svc, "_try_gemini", lambda *a, **k: None)
    monkeypatch.setattr(svc, "_try_hf", lambda *a, **k: None)
    monkeypatch.setattr(svc, "_try_pollinations", lambda *a, **k: {"image_url": "data:image/jpeg;base64,AA", "provider": "Fake", "_raw": b"x", "_mime": "image/jpeg"})
    monkeypatch.setattr(svc, "verify_image", lambda *a, **k: (True, "speaker"))
    res = svc.generate_image("JBL speaker on dark surface with orange lighting and smoke", seed=9)
    assert res["success"] and not called


def test_unsplash_photos_are_hotlinked_not_rehosted(monkeypatch):
    import services.photo_service as ps
    cand = {"url": "https://images.unsplash.com/regular", "check_url": "https://images.unsplash.com/small",
            "hotlink_url": "https://images.unsplash.com/raw?x=1&w=2048&q=85&fm=jpg&fit=max", "width": 4000, "height": 3000,
            "title": "JBL speaker", "creator": "Jane", "creator_url": "https://unsplash.com/@jane?utm_source=adspire&utm_medium=referral",
            "license": "Unsplash License", "license_url": "https://unsplash.com/license", "page_url": "https://unsplash.com/photos/x",
            "source": "Unsplash", "commercial_ok": True, "download_ping": None}
    monkeypatch.setattr(ps, "SOURCES", [("Unsplash", lambda q: [cand])])
    downloads = []
    monkeypatch.setattr(ps, "_download", lambda url, max_side=2048: downloads.append(url) or (b"x", "image/jpeg", (768, 576)))
    res, _ = ps.find_product_photo("q", "JBL speaker", lambda *a: (True, "speaker", 9), deadline=10**12)
    assert res["image_url"] == cand["hotlink_url"]                     # served from Unsplash's CDN
    assert downloads == [cand["check_url"]]                            # only the small preview was fetched (for the AI check)
    assert res["resolution"] == "2048x1536" and res["attribution"]["creator_url"].endswith("utm_medium=referral")


def test_cloudflare_provider_used_before_huggingface_and_pollinations(monkeypatch):
    import base64 as b64, services.image_service as svc
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "acc"); monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    svc._cooldown.pop("cloudflare", None)

    class R:
        ok, status_code, headers = True, 200, {"content-type": "application/json"}
        def json(self):
            return {"success": True, "result": {"image": b64.b64encode(b"jpegbytes").decode()}}
    calls, sent = [], []
    monkeypatch.setattr(svc.requests, "post", lambda url, **k: calls.append(url) or sent.append(k["json"]) or R())
    monkeypatch.setattr(svc, "_try_gemini", lambda *a, **k: None)
    monkeypatch.setattr(svc, "_try_hf", lambda *a, **k: (_ for _ in ()).throw(AssertionError("HF should not be called")))
    monkeypatch.setattr(svc, "refine_prompt", lambda p, s: ("earbuds product shot", "earbuds", False, "earbuds"))
    monkeypatch.setattr(svc, "verify_image", lambda *a: (True, "earbuds"))
    res = svc.generate_image("plain earbuds", seed=77, mode="ai")
    assert res["success"] and "Cloudflare" in res["provider"] and "flux-1-schnell" in calls[0]
    assert set(sent[0]) == {"prompt", "steps"}   # Cloudflare's flux-1-schnell rejects any other field (e.g. seed)


def test_pixabay_source_parses_results(monkeypatch):
    import services.photo_service as ps
    monkeypatch.setenv("PIXABAY_API_KEY", "k")

    class R:
        def raise_for_status(self): pass
        def json(self):
            return {"hits": [{"largeImageURL": "https://pixabay.com/l.jpg", "webformatURL": "https://pixabay.com/w.jpg",
                              "imageWidth": 4000, "imageHeight": 3000, "tags": "speaker, music", "user": "bob",
                              "pageURL": "https://pixabay.com/p/1"}]}
    monkeypatch.setattr(ps.requests, "get", lambda *a, **k: R())
    c = ps._pixabay("bluetooth speaker")[0]
    assert c["source"] == "Pixabay" and c["commercial_ok"] and c["check_url"].endswith("w.jpg")


def _cf_setup(monkeypatch, svc, prompt, verdicts):
    svc._brand_info[prompt] = {"brand": "JBL", "search_query": "JBL earbuds", "branded_subject": "JBL earbuds",
                               "custom_scene": True}
    monkeypatch.setattr(svc, "refine_prompt", lambda p, s: ("matte black earbuds on marble", "wireless earbuds", False, "earbuds packshot"))
    monkeypatch.setattr(svc, "_try_gemini", lambda *a, **k: None)
    sent = []
    monkeypatch.setattr(svc, "_try_cloudflare", lambda p, seed, errors: sent.append(p) or
                        {"image_url": "data:image/jpeg;base64,AA", "provider": "FLUX.1-schnell (Cloudflare Workers AI)", "_raw": b"x", "_mime": "image/jpeg"})
    checks = []
    def verify(raw, mime, subject, people, brand=""):
        checks.append(brand)
        return verdicts[len(checks) - 1]
    monkeypatch.setattr(svc, "verify_image", verify)
    return sent, checks


def test_brand_logo_requested_and_verified_for_flux(monkeypatch):
    import services.image_service as svc
    sent, checks = _cf_setup(monkeypatch, svc, "JBL earbuds over black marble", [(True, "earbuds with JBL logo")])
    res = svc.generate_image("JBL earbuds over black marble", seed=11, mode="ai")
    assert res["success"] and res["logo"] == "JBL"
    assert '"JBL" brand logo' in sent[0] and checks == ["JBL"]


def test_misspelled_logo_is_retried_then_falls_back_without_logo(monkeypatch):
    import services.image_service as svc
    sent, checks = _cf_setup(monkeypatch, svc, "JBL earbuds with neon light",
                             [(False, "JBL logo missing or misspelled (reads 'JLB')"),
                              (False, "JBL logo missing or misspelled"), (True, "earbuds")])
    res = svc.generate_image("JBL earbuds with neon light", seed=12, mode="ai")
    assert res["success"] and res["logo"] is None and res["attempts"] == 3
    assert "JBL" in sent[0] and "JBL" in sent[1] and "JBL" not in sent[2]   # last try drops the logo
    assert checks == ["JBL", "JBL", ""]
