"""
Real product photo search.

For branded products ("JBL earbuds", "Bowers & Wilkins speakers") a real photograph is far
more accurate than anything a free AI image model can draw. This module searches openly
licensed photo libraries, asks Gemini vision to confirm each candidate really shows the
requested product, and returns the first match in HD together with its credit and licence.

Sources (in order, keys are optional and free):
  Pexels      PEXELS_API_KEY        free licence, HD
  Unsplash    UNSPLASH_ACCESS_KEY   free licence, HD
  Pixabay     PIXABAY_API_KEY       free licence, up to 1280 px
  Openverse   no key                Creative Commons (Flickr, Wikimedia, ...)
  Wikimedia   no key                Creative Commons / public domain
"""
import io
import os
import time
import base64

import requests

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

UA = {"User-Agent": "Adspire/3.0 (student marketing project; image search)"}
MAX_SIDE = 2048            # HD, but keeps data URLs a sensible size
MIN_SIDE = 600             # skip tiny images
MAX_CANDIDATES = 8         # how many photos we are willing to check per request
GOOD_ENOUGH = 8            # stop searching once an approved photo scores this well (1-10)
MAX_APPROVED = 3           # otherwise compare up to this many approved photos and keep the best
NON_COMMERCIAL = ("nc",)   # CC licence codes that forbid commercial use


def _env(name):
    v = os.getenv(name)
    return v.strip() if v and v.strip() else None


# ---------------------------------------------------------------- sources ---

def _pexels(query):
    key = _env("PEXELS_API_KEY")
    if not key:
        return []
    r = requests.get("https://api.pexels.com/v1/search", params={"query": query, "per_page": 10},
                     headers={"Authorization": key, **UA}, timeout=15)
    r.raise_for_status()
    return [{
        "url": p["src"].get("large2x") or p["src"]["original"], "check_url": p["src"].get("large") or p["src"]["medium"],
        "width": p["width"], "height": p["height"], "title": p.get("alt") or query,
        "creator": p.get("photographer", "Unknown"), "license": "Pexels License", "license_url": "https://www.pexels.com/license/",
        "page_url": p.get("url"), "source": "Pexels", "commercial_ok": True,
    } for p in r.json().get("photos", [])]


def _pixabay(query):
    key = _env("PIXABAY_API_KEY")
    if not key:
        return []
    r = requests.get("https://pixabay.com/api/", params={
        "key": key, "q": query[:100], "image_type": "photo", "safesearch": "true", "per_page": 20,
    }, headers=UA, timeout=15)
    r.raise_for_status()
    # Pixabay API terms: no permanent hotlinking -> the photo is downloaded (re-hosted) below,
    # which is how this module handles every source except Unsplash.
    return [{
        "url": p.get("largeImageURL") or p["webformatURL"], "check_url": p["webformatURL"],
        "width": p.get("imageWidth", 0), "height": p.get("imageHeight", 0),
        "title": (p.get("tags") or query)[:120], "creator": p.get("user", "Unknown"),
        "license": "Pixabay Content License", "license_url": "https://pixabay.com/service/license-summary/",
        "page_url": p.get("pageURL"), "source": "Pixabay", "commercial_ok": True,
    } for p in r.json().get("hits", [])]


def _unsplash(query):
    key = _env("UNSPLASH_ACCESS_KEY")
    if not key:
        return []
    r = requests.get("https://api.unsplash.com/search/photos", params={"query": query, "per_page": 10},
                     headers={"Authorization": f"Client-ID {key}", **UA}, timeout=15)
    r.raise_for_status()
    utm = "utm_source=adspire&utm_medium=referral"  # Unsplash API guideline for attribution links
    return [{
        "url": p["urls"]["regular"], "check_url": p["urls"]["small"],
        # Unsplash API guideline: hotlink the image from Unsplash's CDN instead of re-hosting a copy
        "hotlink_url": p["urls"]["raw"] + "&w=2048&q=85&fm=jpg&fit=max",
        "width": p["width"], "height": p["height"], "title": p.get("alt_description") or query,
        "creator": p["user"]["name"], "creator_url": f"{p['user']['links']['html']}?{utm}",
        "license": "Unsplash License", "license_url": "https://unsplash.com/license",
        "page_url": f"{p['links']['html']}?{utm}", "source": "Unsplash", "commercial_ok": True,
        "download_ping": p["links"].get("download_location"),
    } for p in r.json().get("results", [])]


def _openverse(query):
    r = requests.get("https://api.openverse.org/v1/images/", params={"q": query, "page_size": 12, "mature": "false"},
                     headers=UA, timeout=20)
    r.raise_for_status()
    out = []
    for p in r.json().get("results", []):
        lic = (p.get("license") or "").lower()
        out.append({
            "url": p["url"], "check_url": p.get("thumbnail") or p["url"],
            "width": p.get("width") or 0, "height": p.get("height") or 0, "title": p.get("title") or query,
            "creator": p.get("creator") or "Unknown",
            "license": f"CC {lic.upper()} {p.get('license_version') or ''}".strip() if lic not in ("pdm", "cc0") else lic.upper(),
            "license_url": p.get("license_url"), "page_url": p.get("foreign_landing_url"),
            "source": f"Openverse / {p.get('source', 'web').title()}",
            "commercial_ok": not any(code in lic.split("-") for code in NON_COMMERCIAL),
        })
    return out


def _wikimedia(query):
    r = requests.get("https://commons.wikimedia.org/w/api.php", params={
        "action": "query", "generator": "search", "gsrsearch": f"filetype:bitmap {query}", "gsrnamespace": 6,
        "gsrlimit": 8, "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": MAX_SIDE, "format": "json",
    }, headers=UA, timeout=20)
    r.raise_for_status()
    out = []
    for p in ((r.json().get("query") or {}).get("pages") or {}).values():
        ii = p["imageinfo"][0]
        meta = ii.get("extmetadata") or {}
        lic = (meta.get("LicenseShortName") or {}).get("value", "See source")
        artist = (meta.get("Artist") or {}).get("value", "Unknown")
        artist = __import__("re").sub("<[^>]+>", "", artist)[:80]
        out.append({
            "url": ii.get("thumburl") or ii["url"], "check_url": ii.get("thumburl") or ii["url"],
            "width": ii.get("width", 0), "height": ii.get("height", 0), "title": p["title"].replace("File:", ""),
            "creator": artist, "license": lic, "license_url": ii.get("descriptionurl"), "page_url": ii.get("descriptionurl"),
            "source": "Wikimedia Commons", "commercial_ok": "nc" not in lic.lower(),
        })
    return out


SOURCES = [("Pexels", _pexels), ("Unsplash", _unsplash), ("Pixabay", _pixabay), ("Openverse", _openverse), ("Wikimedia", _wikimedia)]


# -------------------------------------------------------------- utilities ---

def _download(url, max_side=MAX_SIDE):
    r = requests.get(url, headers=UA, timeout=25)
    r.raise_for_status()
    if not r.headers.get("content-type", "").startswith("image/"):
        raise ValueError("not an image")
    if not PIL_AVAILABLE:
        return r.content, r.headers["content-type"].split(";")[0], None
    img = Image.open(io.BytesIO(r.content)).convert("RGB")
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue(), "image/jpeg", img.size


def _nearest_ratio(w, h):
    r = w / h if h else 1
    return min({"1:1": 1.0, "16:9": 16 / 9, "9:16": 9 / 16}.items(), key=lambda kv: abs(kv[1] - r))[0]


def query_variants(search_query: str, brand: str = "", product_type: str = ""):
    """Specific -> broad: libraries match every word, so 'JBL wireless earbuds' can find
    nothing while 'JBL earbuds' finds several photos."""
    out = [search_query]
    if brand and product_type:
        words = product_type.split()
        out += [f"{brand} {product_type}", f"{brand} {words[-1]}"]
        if len(words) > 1:
            out.append(f"{brand} {words[0]} {words[-1]}")
    seen, uniq = set(), []
    for q in out:
        q = " ".join(q.split())
        if q and q.lower() not in seen:
            seen.add(q.lower())
            uniq.append(q)
    return uniq[:4]


def find_product_photo(query, subject: str, verify, deadline: float, min_score: int = 1):
    """
    query:   search text or list of variants (specific -> broad), e.g. ["JBL wireless earbuds", "JBL earbuds"]
    subject: what must be visible, e.g. "JBL wireless earbuds"
    verify:  function(raw_bytes, mime, subject) -> (ok, description[, ad_score 1-10])
    Returns (result_dict | None, notes: list[str]).
    """
    notes, checked, approved = [], 0, []
    seen = set()
    queries = [query] if isinstance(query, str) else list(query)
    for name, fn in SOURCES:
        if time.time() > deadline - 10:
            break
        candidates = []
        for q in queries:  # first wording that returns anything
            try:
                candidates = fn(q)
            except Exception as e:
                notes.append(f"{name}: search failed ({str(e)[:60]})")
                break
            if candidates:
                break
        if not candidates:
            continue
        # biggest first, skip tiny ones and duplicates
        candidates = [c for c in candidates if min(c["width"], c["height"]) >= MIN_SIDE or not c["width"]]
        candidates.sort(key=lambda c: (c["commercial_ok"], c["width"] * c["height"]), reverse=True)
        for c in candidates:
            if checked >= MAX_CANDIDATES or time.time() > deadline - 10:
                break
            if c["url"] in seen:
                continue
            seen.add(c["url"])
            checked += 1
            try:
                small, mime, _ = _download(c["check_url"], max_side=768)
            except Exception:
                continue
            verdict = verify(small, mime, subject)
            ok, seen_desc = verdict[0], verdict[1]
            score = verdict[2] if len(verdict) > 2 else 5
            if not ok:
                print(f"[PhotoService] rejected {name}: '{c['title'][:50]}' -> {seen_desc}")
                continue
            print(f"[PhotoService] approved {name}: '{c['title'][:50]}' score={score}")
            approved.append((score, c, small, mime))
            if score >= GOOD_ENOUGH or len(approved) >= MAX_APPROVED:
                break
        if approved and (max(a[0] for a in approved) >= GOOD_ENOUGH or len(approved) >= MAX_APPROVED):
            break

    best = max(approved, key=lambda a: (a[0], a[1]["commercial_ok"])) if approved else None
    if best and best[0] < min_score:
        notes.append(f"Best real photo scored only {best[0]}/10 as an advert ('{best[1]['title'][:40]}')")
        best = None
    if best:
        score, c, small, mime = best
        if c.get("download_ping"):  # Unsplash API guideline: register the download
            try:
                requests.get(c["download_ping"], headers={"Authorization": f"Client-ID {_env('UNSPLASH_ACCESS_KEY')}"}, timeout=5)
            except Exception:
                pass
        if c.get("hotlink_url"):
            # Unsplash: serve straight from their CDN (no re-hosted copy); size scaled to <= 2048 px
            image_url = c["hotlink_url"]
            scale = min(1.0, MAX_SIDE / max(c["width"], c["height"], 1))
            w, h = int(c["width"] * scale), int(c["height"] * scale)
        else:
            try:
                raw, mime, size = _download(c["url"])
            except Exception:
                raw, size = small, None
            image_url = f"data:{mime};base64,{base64.b64encode(raw).decode()}"
            w, h = size or (c["width"], c["height"])
        print(f"[PhotoService] using '{c['title'][:50]}' {w}x{h} (score {score})")
        return {
            "image_url": image_url,
            "provider": f"Real photo · {c['source']}",
            "kind": "photo",
            "resolution": f"{w}x{h}",
            "aspect_ratio": _nearest_ratio(w, h),
            "attribution": {
                "title": c["title"][:120], "creator": c["creator"], "creator_url": c.get("creator_url"),
                "license": c["license"],
                "license_url": c["license_url"], "page_url": c["page_url"], "source": c["source"],
                "commercial_ok": c["commercial_ok"],
            },
        }, notes
    if checked:
        notes.append(f"Checked {checked} real photos but none clearly showed \"{subject}\"")
    else:
        notes.append(f"No real photos found for \"{queries[0]}\"")
    return None, notes
