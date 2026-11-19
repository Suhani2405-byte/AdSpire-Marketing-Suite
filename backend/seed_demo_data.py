"""
Seed realistic demo data: 10 marketer accounts, one campaign for each of 20 well-known products
(JBL, Sony, Apple, Nike ...) over the last 30 days, brand profiles and matching activity history
(so the library + admin dashboard are populated). A product is never added twice.

Usage (from the backend folder):
    venv\\Scripts\\python seed_demo_data.py                 # add the 20 demo campaigns (one per product)
    venv\\Scripts\\python seed_demo_data.py --count 10      # only 10 of them
    venv\\Scripts\\python seed_demo_data.py --owner you@example.com
                                                        # put all campaigns in YOUR library instead
    venv\\Scripts\\python seed_demo_data.py --clear         # remove all demo data again

All demo accounts use emails ending in @demo.adspire.app and the password below.
Works on SQLite locally and on Postgres (DATABASE_URL) on Render.
"""
import argparse
import json
import random
import sys
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

from services import database_service as db  # noqa: E402
from services.database_service import SessionLocal, User, Campaign, Brand, ActivityLog, _utcnow  # noqa: E402
from services.gemini_service import generate_fallback_campaign  # noqa: E402
from services.auth_service import hash_password  # noqa: E402

DEMO_DOMAIN = "@demo.adspire.app"
DEMO_PASSWORD = "DemoPass123"
SEED_SOURCE = "demo-seed"

USERS = [
    ("Aarav Mehta", "aarav"), ("Priya Sharma", "priya"), ("Rohan Gupta", "rohan"),
    ("Ananya Iyer", "ananya"), ("Kabir Singh", "kabir"), ("Sara Khan", "sara"),
    ("Vikram Rao", "vikram"), ("Meera Nair", "meera"), ("Arjun Patel", "arjun"),
    ("Isha Verma", "isha"),
]

# (product, description, audience, industry, product type) - real brands, so the demo looks real
PRODUCTS = [
    ("JBL Flip 6 Portable Speaker", "Waterproof IP67 Bluetooth speaker with bold JBL Pro Sound and 12 hours of playtime.", "College students and travellers 18-30", "Consumer Electronics & D2C", "portable bluetooth speaker"),
    ("Sony WH-1000XM5 Headphones", "Industry-leading noise cancelling over-ear headphones with 30-hour battery.", "Commuters and remote workers 22-40", "Consumer Electronics & D2C", "over-ear headphones"),
    ("Apple iPhone 15", "Dynamic Island, 48MP main camera and USB-C in a durable aluminium design.", "Young professionals 20-35", "Consumer Electronics & D2C", "smartphone"),
    ("Samsung Galaxy S24", "Galaxy AI features, 50MP camera and an all-day battery in a compact flagship.", "Tech enthusiasts 20-38", "Consumer Electronics & D2C", "smartphone"),
    ("Nike Pegasus Running Shoes", "Responsive cushioning running shoe for daily training and long runs.", "Runners and gym-goers 18-40", "Fashion & Beauty", "running shoes"),
    ("Adidas Ultraboost Sneakers", "Energy-returning Boost midsole with a Primeknit upper for all-day comfort.", "Streetwear and fitness fans 18-30", "Fashion & Beauty", "sneakers"),
    ("Canon EOS Mirrorless Camera", "24MP mirrorless camera with fast autofocus for vlogging and travel photos.", "Content creators and hobby photographers", "Consumer Electronics & D2C", "camera"),
    ("Apple MacBook Air", "Thin, silent laptop with Apple silicon and up to 18 hours of battery.", "Students and designers 18-30", "Consumer Electronics & D2C", "laptop"),
    ("boAt Airdopes Earbuds", "True wireless earbuds with ENx noise reduction and 40-hour playback.", "Indian college students 17-25", "Consumer Electronics & D2C", "wireless earbuds"),
    ("Casio G-Shock Watch", "Shock-resistant digital watch with 200m water resistance and tough design.", "Outdoor and adventure lovers 18-35", "Fashion & Beauty", "wristwatch"),
    ("Coca-Cola Zero Sugar", "Real Coca-Cola taste with zero sugar, best served ice-cold.", "Young adults 18-35", "E-commerce & D2C", "soda can"),
    ("Red Bull Energy Drink", "Vitalizes body and mind for study, sport and late-night work.", "Students and athletes 18-30", "E-commerce & D2C", "energy drink can"),
    ("Starbucks Coffee", "Handcrafted coffee and seasonal drinks for every part of the day.", "Office workers and students 18-40", "E-commerce & D2C", "coffee cup"),
    ("Nivea Soft Moisturising Cream", "Light, fast-absorbing moisturiser with jojoba oil and vitamin E.", "Skincare beginners 18-35", "Fashion & Beauty", "moisturising cream"),
    ("Ray-Ban Wayfarer Sunglasses", "Iconic acetate frame sunglasses with 100% UV protection.", "Style-conscious adults 20-40", "Fashion & Beauty", "sunglasses"),
    ("Logitech MX Master Mouse", "Ergonomic wireless mouse with MagSpeed scrolling for productivity.", "Developers and designers", "Consumer Electronics & D2C", "computer mouse"),
    ("GoPro HERO Action Camera", "Waterproof 5.3K action camera with HyperSmooth stabilisation.", "Travellers and sports enthusiasts", "Consumer Electronics & D2C", "action camera"),
    ("Amazon Kindle Paperwhite", "Glare-free e-reader with adjustable warm light and weeks of battery.", "Book lovers 20-50", "Consumer Electronics & D2C", "e-reader"),
    ("PlayStation DualSense Controller", "Wireless controller with haptic feedback and adaptive triggers.", "Gamers 15-30", "Consumer Electronics & D2C", "game controller"),
    ("Levi's 501 Original Jeans", "The original straight-fit button-fly jeans, made to last.", "Fashion-conscious adults 18-40", "Fashion & Beauty", "denim jeans"),
    ("Bose QuietComfort Earbuds", "Noise cancelling true wireless earbuds with CustomTune sound.", "Frequent flyers and commuters 22-40", "Consumer Electronics & D2C", "wireless earbuds"),
    ("Dyson V15 Detect Vacuum", "Cordless vacuum with laser dust detection and 60-minute run time.", "Homeowners and families 28-50", "Consumer Electronics & D2C", "cordless vacuum cleaner"),
    ("Nintendo Switch OLED", "Hybrid game console with a vivid 7-inch OLED screen for home and on-the-go play.", "Gamers and families 12-35", "Consumer Electronics & D2C", "handheld game console"),
    ("Xiaomi Redmi Note 13", "Affordable 5G smartphone with a 108MP camera and AMOLED display.", "Budget-conscious students 18-28", "Consumer Electronics & D2C", "smartphone"),
    ("OnePlus 12", "Flagship smartphone with Hasselblad camera and 100W fast charging.", "Tech enthusiasts 20-35", "Consumer Electronics & D2C", "smartphone"),
    ("Fitbit Charge 6", "Fitness tracker with heart-rate, sleep tracking and built-in GPS.", "Health-conscious adults 22-45", "Health & Wellness", "fitness tracker band"),
    ("Garmin Forerunner 265", "GPS running watch with AMOLED display and training readiness insights.", "Runners and triathletes 20-45", "Health & Wellness", "GPS sports watch"),
    ("Philips Air Fryer", "Rapid Air technology for crispy food with up to 90% less fat.", "Busy families and home cooks 25-50", "E-commerce & D2C", "air fryer"),
    ("Nespresso Vertuo Coffee Machine", "One-touch coffee machine for barista-style coffee at home.", "Coffee lovers 25-45", "E-commerce & D2C", "coffee machine"),
    ("Fujifilm Instax Mini 12", "Instant camera that prints credit-card sized photos in seconds.", "Teens and young adults 15-25", "Consumer Electronics & D2C", "instant camera"),
    ("Lenovo ThinkPad X1 Carbon", "Ultralight business laptop with legendary keyboard and security features.", "Business professionals 25-50", "SaaS & B2B Tech", "laptop"),
    ("Dell XPS 13", "Compact premium laptop with an InfinityEdge display.", "Students and creators 18-35", "Consumer Electronics & D2C", "laptop"),
    ("Marshall Emberton Speaker", "Rugged portable speaker with signature Marshall sound and 20+ hours of play.", "Music lovers 20-40", "Consumer Electronics & D2C", "portable speaker"),
    ("Puma Suede Classic Sneakers", "The iconic suede sneaker, a street-style classic since 1968.", "Streetwear fans 16-30", "Fashion & Beauty", "suede sneakers"),
    ("Titan Edge Watch", "One of the world's slimmest analogue watches, crafted in India.", "Professionals 25-45", "Fashion & Beauty", "analogue wristwatch"),
    ("Lakme 9to5 Lipstick", "Long-lasting matte lipstick for a full work day.", "Working women 20-35", "Fashion & Beauty", "lipstick"),
    ("Maybelline Fit Me Foundation", "Lightweight foundation that matches skin tone and texture.", "Makeup users 18-35", "Fashion & Beauty", "foundation bottle"),
    ("L'Oreal Paris Shampoo", "Nourishing shampoo for strong, shiny and healthy-looking hair.", "Adults 18-45", "Fashion & Beauty", "shampoo bottle"),
    ("The Body Shop Tea Tree Face Wash", "Purifying face wash with tea tree oil for blemish-prone skin.", "Young adults with oily skin 16-30", "Health & Wellness", "face wash tube"),
    ("Dove Beauty Bar", "Gentle cleansing bar with 1/4 moisturising cream.", "Families and adults 18-50", "Health & Wellness", "soap bar"),
    ("Colgate MaxFresh Toothpaste", "Cooling crystals toothpaste for long-lasting fresh breath.", "Families 10-50", "Health & Wellness", "toothpaste tube"),
    ("Pepsi Cola", "Bold, refreshing cola for every celebration.", "Teens and young adults 15-30", "E-commerce & D2C", "soda can"),
    ("Lay's Classic Potato Chips", "Thin, crispy potato chips with just the right amount of salt.", "Snack lovers 12-35", "E-commerce & D2C", "bag of potato chips"),
    ("KitKat Chocolate", "Crispy wafer fingers covered in smooth milk chocolate.", "Students and office workers 12-40", "E-commerce & D2C", "chocolate bar"),
    ("Amul Butter", "The taste of India - creamy pasteurised butter.", "Indian households", "E-commerce & D2C", "butter pack"),
    ("Tropicana Orange Juice", "100% orange juice with no added sugar.", "Health-conscious families", "Health & Wellness", "juice carton"),
    ("Milton Thermosteel Flask", "Stainless steel vacuum flask that keeps drinks hot or cold for 24 hours.", "Students and office commuters", "E-commerce & D2C", "steel water flask"),
    ("Tupperware Lunch Box", "Leak-proof, BPA-free lunch box for school and office.", "Parents and office workers", "E-commerce & D2C", "lunch box"),
    ("IKEA Poang Armchair", "Bentwood armchair with a gentle rocking comfort.", "Young homeowners 25-40", "E-commerce & D2C", "armchair"),
    ("Wildcraft Trekking Backpack", "45-litre rucksack with rain cover for treks and travel.", "Trekkers and backpackers 18-35", "E-commerce & D2C", "trekking backpack"),
    ("American Tourister Suitcase", "Lightweight hard-shell trolley suitcase with 360-degree wheels.", "Frequent travellers 22-50", "E-commerce & D2C", "suitcase"),
    ("Decathlon Yoga Mat", "Non-slip 8mm yoga mat for home workouts.", "Fitness beginners 18-40", "Health & Wellness", "yoga mat"),
    ("Yonex Badminton Racket", "Lightweight graphite racket for fast, powerful smashes.", "Badminton players 14-35", "Health & Wellness", "badminton racket"),
    ("SG Cricket Bat", "English willow cricket bat for club and school players.", "Young cricketers 12-25", "Health & Wellness", "cricket bat"),
    ("Hero Sprint Bicycle", "Multi-speed bicycle for city rides and weekend fitness.", "Fitness riders 16-40", "Health & Wellness", "bicycle"),
    ("Royal Enfield Classic 350", "Timeless retro motorcycle with a thumping 350cc engine.", "Riders 21-45", "E-commerce & D2C", "motorcycle"),
    ("Tata Nexon EV", "Electric compact SUV with 450 km range and 5-star safety.", "Urban families 28-50", "E-commerce & D2C", "electric SUV car"),
    ("HP LaserJet Printer", "Fast, reliable office laser printer with wireless printing.", "Small offices and businesses", "SaaS & B2B Tech", "laser printer"),
    ("Parle-G Biscuits", "India's favourite glucose biscuits, perfect with a cup of chai.", "Families and students", "E-commerce & D2C", "biscuit packet"),
    ("Rubik's Cube", "The original 3x3 puzzle cube that has challenged minds since 1980.", "Puzzle lovers and students 8-30", "E-commerce & D2C", "puzzle cube"),
]

# product -> brand name (used for photo search and logo checks)
BRANDS = {
    "JBL Flip 6 Portable Speaker": "JBL", "Sony WH-1000XM5 Headphones": "Sony", "Apple iPhone 15": "Apple",
    "Samsung Galaxy S24": "Samsung", "Nike Pegasus Running Shoes": "Nike", "Adidas Ultraboost Sneakers": "Adidas",
    "Canon EOS Mirrorless Camera": "Canon", "Apple MacBook Air": "Apple", "boAt Airdopes Earbuds": "boAt",
    "Casio G-Shock Watch": "Casio", "Coca-Cola Zero Sugar": "Coca-Cola", "Red Bull Energy Drink": "Red Bull",
    "Starbucks Coffee": "Starbucks", "Nivea Soft Moisturising Cream": "Nivea", "Ray-Ban Wayfarer Sunglasses": "Ray-Ban",
    "Logitech MX Master Mouse": "Logitech", "GoPro HERO Action Camera": "GoPro", "Amazon Kindle Paperwhite": "Kindle",
    "PlayStation DualSense Controller": "PlayStation", "Levi's 501 Original Jeans": "Levi's",
}
# the newer products: brand = the first word(s) of the product name
for _p, *_ in PRODUCTS:
    if _p not in BRANDS:
        _multi = ("The Body Shop", "American Tourister", "Royal Enfield", "L'Oreal Paris")
        BRANDS[_p] = next((m for m in _multi if _p.startswith(m)), _p.split()[0])

PLATFORMS = ["Instagram", "TikTok / Reels", "LinkedIn", "Google Search Ads", "Facebook Ads", "Twitter / X", "Omnichannel Suite"]
B2B_PLATFORMS = ["LinkedIn", "Google Search Ads", "Twitter / X", "Omnichannel Suite"]
GOALS = ["Sales & Conversions", "Lead Generation", "Brand Awareness", "Product Launch", "Viral Engagement"]
TONES = ["Bold & Premium", "Professional & Authoritative", "High Energy & Dynamic", "Minimalist & Luxury", "Witty & Engaging", "Warm & Friendly"]
SEASONS = ["Diwali Sale", "Summer Launch", "Back to College", "New Year Push", "Monsoon Offer", "Festive Edit", "Weekend Flash Sale", "Spring Refresh"]
IMAGE_PROVIDERS = ["Pollinations FLUX (free tier)"] * 6 + ["Google Gemini (gemini-3.1-flash-image)"] * 2 + ["FLUX.1-schnell (Hugging Face)"]
MODELS = ["gemini-3-flash-preview"] * 5 + ["gemini-3.8-flash"] * 2 + ["gemini-3.1-flash-lite"] * 2 + ["gemini-3.5-flash"]


def build_campaign(rng, product, desc, audience, platform, goal, tone, image_subject):
    c = generate_fallback_campaign(product, desc, audience, platform, goal)
    season = rng.choice(SEASONS)
    c["campaign_title"] = f"{product}: {season}"
    c["tagline"] = rng.choice([
        f"{product} — made for the way you live.",
        f"Upgrade your everyday with {product}.",
        f"Less hassle, more {rng.choice(['flow', 'joy', 'results', 'style', 'energy'])}.",
        f"The {season.lower()} favourite everyone is talking about.",
    ])
    c["executive_summary"] = (
        f"A {tone.lower()} {goal.lower()} campaign for {product} on {platform}, built around the "
        f"{season.lower()} moment and aimed at {audience.lower()}."
    )
    c["image_prompt"] = (
        f"{image_subject}, hero product shot, {rng.choice(['soft studio lighting', 'golden-hour sunlight', 'dramatic rim lighting', 'bright clean daylight'])}, "
        f"{rng.choice(['marble surface', 'wooden table', 'pastel backdrop', 'dark slate background'])}, shallow depth of field"
    )
    c["budget_recommendations"]["expected_ctr"] = f"{rng.uniform(1.8, 3.0):.1f}% - {rng.uniform(3.1, 4.8):.1f}%"
    c["budget_recommendations"]["expected_cpc"] = f"${rng.uniform(0.4, 0.9):.2f} - ${rng.uniform(1.0, 2.5):.2f}"
    return c


def clear():
    with SessionLocal() as s:
        demo_ids = [u.id for u in s.query(User).filter(User.email.like(f"%{DEMO_DOMAIN}")).all()]
        n_c = s.query(Campaign).filter(Campaign.source == SEED_SOURCE).delete(synchronize_session=False)
        n_l = s.query(ActivityLog).filter(ActivityLog.detail.like("[demo]%")).delete(synchronize_session=False)
        if demo_ids:
            s.query(Brand).filter(Brand.user_id.in_(demo_ids)).delete(synchronize_session=False)
            s.query(ActivityLog).filter(ActivityLog.user_id.in_(demo_ids)).delete(synchronize_session=False)
            s.query(User).filter(User.id.in_(demo_ids)).delete(synchronize_session=False)
        s.commit()
    print(f"Removed {n_c} demo campaigns, {len(demo_ids)} demo users, {n_l}+ demo activity rows.")


def seed(count, owner_email=None, rng_seed=42):
    rng = random.Random(rng_seed)
    now = _utcnow()
    pw_hash = hash_password(DEMO_PASSWORD)

    with SessionLocal() as s:
        owner = None
        if owner_email:
            owner = s.query(User).filter(User.email == owner_email.strip().lower()).first()
            if not owner:
                sys.exit(f"No account with email {owner_email}. Register it in the app first.")

        users = []
        for name, handle in USERS:
            email = f"{handle}{DEMO_DOMAIN}"
            u = s.query(User).filter(User.email == email).first()
            if not u:
                u = User(name=name, email=email, password_hash=pw_hash, role="marketer",
                         created_at=now - timedelta(days=rng.randint(31, 60)))
                s.add(u)
                s.flush()
                s.add(ActivityLog(user_id=u.id, action="register", detail="[demo] New marketer account", created_at=u.created_at))
            users.append(u)

        # each demo user "owns" 2 brands
        for i, u in enumerate(users):
            if s.query(Brand).filter(Brand.user_id == u.id).count() == 0:
                for product, desc, audience, industry, _ in (PRODUCTS[(2 * i) % len(PRODUCTS)], PRODUCTS[(2 * i + 1) % len(PRODUCTS)]):
                    s.add(Brand(user_id=u.id, name=product, description=desc, audience=audience,
                                industry=industry, tone=rng.choice(TONES), created_at=u.created_at))

        # one campaign per product, never a product that is already in the demo data
        existing = {(n or "").strip().lower() for (n,) in s.query(Campaign.product_name)}
        todo = [p for p in PRODUCTS if p[0].lower() not in existing]
        rng.shuffle(todo)
        todo = todo[:count]
        count = len(todo)
        for product, desc, audience, industry, subject in todo:
            platform = rng.choice(B2B_PLATFORMS if industry == "SaaS & B2B Tech" else PLATFORMS)
            goal = rng.choice(GOALS)
            tone = rng.choice(TONES)
            # more recent activity is more common -> nicer 7-day trend
            days_ago = min(int(rng.expovariate(1 / 8)), 29)
            created = now - timedelta(days=days_ago, hours=rng.randint(0, 20), minutes=rng.randint(0, 59))
            author = owner or rng.choice(users)
            model = rng.choice(MODELS)

            content = build_campaign(rng, product, desc, audience, platform, goal, tone, subject)
            s.add(Campaign(user_id=author.id, product_name=product, target_audience=audience, platform=platform,
                           goal=goal, campaign_content=json.dumps(content), source=SEED_SOURCE, created_at=created))
            s.add(ActivityLog(user_id=author.id, action="campaign", detail=f"[demo] {product}", provider=model,
                              duration_ms=rng.uniform(14000, 45000), created_at=created))
            # most campaigns also had an image generated (rarely failed)
            if rng.random() < 0.8:
                failed = rng.random() < 0.08
                s.add(ActivityLog(user_id=author.id, action="image_failed" if failed else "image",
                                  detail=f"[demo] {content['image_prompt'][:100]}",
                                  provider=None if failed else rng.choice(IMAGE_PROVIDERS),
                                  duration_ms=rng.uniform(8000, 60000),
                                  created_at=created + timedelta(seconds=rng.randint(40, 120))))
            if rng.random() < 0.3:
                s.add(ActivityLog(user_id=author.id, action="login", detail="[demo]",
                                  created_at=created - timedelta(minutes=rng.randint(1, 30))))
        s.commit()

    where = f"the library of {owner_email}" if owner_email else "10 demo marketer accounts"
    print(f"Added {count} demo campaigns to {where}.")
    print(f"Demo logins: e.g. aarav{DEMO_DOMAIN} / {DEMO_PASSWORD}  (all 10: {', '.join(h for _, h in USERS)})")
    print(f"Totals now: {db.count_users()} users, {db.get_database_stats()['total_campaigns']} campaigns.")



def attach_images(replace=False):
    """Find one verified picture per demo product and attach it to every demo campaign of that product.
    Real licensed photo first (with brand check), otherwise a verified *branded* AI image from a
    strong engine (Gemini / Cloudflare FLUX / Hugging Face). Generic free-tier images (Pollinations)
    are not good enough for the demo, so such products are left for a later run.
    replace=True redoes products that already have a picture."""
    import time as _t
    from services.photo_service import find_product_photo, query_variants
    from services.image_service import verify_photo, generate_image, provider_status, _try_cloudflare, _try_gemini, _try_hf

    # probe the strong engines once: a quota/credit error puts them on cooldown, so we don't wait for
    # the slow free engine only to throw its picture away
    probe = []
    _try_gemini("a red apple", "1:1", probe)
    _try_cloudflare("a red apple", 0, probe)
    _try_hf("a red apple", 512, 512, 1, probe)

    from google.genai import types as _gt
    from services.image_service import _qa_json

    def exact_model_check(product, ptype):
        """Demo pictures must show this exact product, not just the same kind of product."""
        def check(raw, mime, subject):
            ok, desc, score = verify_photo(raw, mime, subject)
            if not ok:
                return ok, desc, score
            data = _qa_json([
                _gt.Part.from_bytes(data=raw, mime_type=mime or "image/jpeg"),
                f'Does this photo show the product "{product}" ({ptype})? Reply JSON: {{"exact": bool (true only '
                'if it is this brand AND this model or model family, or so similar that a shopper would accept it; '
                'false for an older generation, a different model or product line of the same brand, a toy, a '
                'part or only packaging), "description": "max 12 words"}}',
            ])
            if data is None:
                return None, desc, score
            return bool(data.get("exact")), str(data.get("description", desc))[:150], score
        return check

    done, missing = 0, []
    for product, desc, audience, industry, ptype in PRODUCTS:
        with SessionLocal() as s:
            camps = s.query(Campaign).filter(Campaign.product_name == product).all()
            if not camps or (not replace and all(c.image_url for c in camps)):
                continue
        brand = BRANDS.get(product, "")
        t0 = _t.time()
        model_words = product.replace(brand, "", 1).strip()
        queries = [product] + query_variants(f"{brand} {ptype}", brand, ptype)
        if model_words:
            queries.insert(1, f"{brand} {model_words.split()[0]}")
        photo, _ = find_product_photo(list(dict.fromkeys(queries)), product,
                                      exact_model_check(product, ptype), deadline=_t.time() + 150, min_score=5)
        image_url, how = (photo["image_url"], photo["provider"]) if photo else (None, None)
        strong_ai = ((provider_status().get("cloudflare") or provider_status().get("gemini_image")
                      or provider_status().get("huggingface")))
        if not image_url and strong_ai:
            res = generate_image(f"{brand} {ptype}, studio product photography", mode="ai", style="Photorealistic")
            if res.get("success") and "Pollinations" not in res.get("provider", ""):
                image_url, how = res["image_url"], res["provider"]
        if not image_url:
            missing.append(product)
            print(f"  [no image]  {product}  ({_t.time() - t0:.0f}s) - run again later (e.g. after the Cloudflare daily reset)")
            continue
        thumb = db.make_thumb(image_url)
        with SessionLocal() as s:
            for c in s.query(Campaign).filter(Campaign.product_name == product):
                c.image_url, c.image_thumb = image_url, thumb
            s.commit()
        done += 1
        print(f"  [image] {product:36} <- {how}  ({_t.time() - t0:.0f}s)", flush=True)
    print(f"Images attached for {done} products" + (f"; missing: {', '.join(missing)}" if missing else ""))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Seed or remove Adspire demo data.")
    ap.add_argument("--count", type=int, default=len(PRODUCTS),
                    help=f"number of demo campaigns, one per product (default and maximum {len(PRODUCTS)})")
    ap.add_argument("--owner", help="put all demo campaigns into this existing account's library")
    ap.add_argument("--clear", action="store_true", help="remove all demo data")
    ap.add_argument("--images", action="store_true", help="attach a verified product picture to the demo campaigns")
    ap.add_argument("--images-only", action="store_true", help="only attach pictures to existing demo campaigns")
    ap.add_argument("--replace", action="store_true", help="with --images/--images-only: redo pictures that already exist")
    args = ap.parse_args()
    if args.clear:
        clear()
    else:
        if not args.images_only:
            seed(max(1, min(args.count, 5000)), args.owner)
        if args.images or args.images_only:
            attach_images(replace=args.replace)
