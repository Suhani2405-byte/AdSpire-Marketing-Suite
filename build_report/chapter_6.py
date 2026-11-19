from build_report.docx_helper import (
    add_page_break, add_heading_1, add_heading_2, add_heading_3,
    add_body_p, add_bullet_p, add_styled_table, add_code_block, add_table_caption
)


def build_chapter_6(doc):
    add_heading_1(doc, "CHAPTER 6: IMPLEMENTATION")

    add_heading_2(doc, "6.1 Development Environment and Project Structure")
    add_body_p(doc, "The project was developed on Windows 11 with Python 3.13, Node.js 20 and Visual Studio Code, and is deployed to Render. The repository is organised as follows:")
    add_code_block(doc, (
        "AI-Marketing-Campaign-Generator/\n"
        "├── backend/\n"
        "│   ├── app.py                  # Flask app: blueprints, SPA serving, errors, headers\n"
        "│   ├── routes/                 # auth, campaign, image, budget, brand, admin routes\n"
        "│   ├── services/\n"
        "│   │   ├── gemini_service.py   # prompt, streaming, model fail-over\n"
        "│   │   ├── image_service.py    # prompt analysis, generation, verification\n"
        "│   │   ├── photo_service.py    # licensed real-photo search\n"
        "│   │   ├── database_service.py # SQLAlchemy models + queries + metrics\n"
        "│   │   ├── auth_service.py     # password hashing, tokens, decorators\n"
        "│   │   └── rate_limit.py       # per-user hourly limits\n"
        "│   ├── tests/                  # pytest suite (33 tests)\n"
        "│   ├── create_admin.py         # create / reset an administrator\n"
        "│   ├── seed_demo_data.py       # 10 demo users + 60 brand campaigns\n"
        "│   └── requirements.txt\n"
        "├── frontend/src/\n"
        "│   ├── App.jsx                 # auth gate + navigation shell\n"
        "│   ├── api.js                  # Axios client + SSE stream reader\n"
        "│   ├── state/AppState.jsx      # shared React context\n"
        "│   ├── components/             # 8 screen components\n"
        "│   └── utils/                  # exporters (PDF/MD/JSON), charts\n"
        "├── build_report/               # scripts that generate this report\n"
        "├── render.yaml                 # Render deployment blueprint\n"
        "└── run.bat / start.py          # one-click local start\n"
    ))
    add_body_p(doc, "Running run.bat (or python start.py) builds the frontend, starts Flask on port 5000 and opens the browser. During UI development, npm run dev starts Vite on port 5173 with /api proxied to the backend. Secrets (GEMINI_API_KEY, SECRET_KEY, DATABASE_URL and optional image keys) are read from backend/.env, which is excluded from version control.")

    add_heading_2(doc, "6.2 Frontend Implementation")
    add_body_p(doc, "The frontend consists of eight screen components, a shared context and two utility modules. Notable implementation details:")
    add_bullet_p(doc, "Streaming reader:", "streamCampaign() posts the brief with fetch(), reads the response body with a ReadableStream reader, splits it into Server-Sent Event messages and forwards status, chunk, reset and done events to the context, which updates a live preview and a character counter.")
    add_bullet_p(doc, "Session handling:", "The token is stored in localStorage; on start-up /api/auth/me restores the user, and an Axios interceptor logs the user out when the server answers 401 with auth=false (expired or disabled account).")
    add_bullet_p(doc, "Visual Studio:", "Offers Auto / Real Photo / AI modes and sends a new random seed on every click so Regenerate gives a new variation. Download and Regenerate sit side by side on the image; clicking the image opens a full-screen viewer (rendered into the page body with a React portal, closed with Esc or a click). Real photos show the credit, licence link and a warning for non-commercial licences.")
    add_bullet_p(doc, "Admin Panel:", "Four sections (Overview, Users, Settings & Features, Activity Log) built with Chart.js bar and doughnut charts, inline role and status controls, and a settings form with toggle switches.")
    add_bullet_p(doc, "Responsiveness:", "Navigation and result tabs scroll horizontally on narrow screens and forms collapse to one column; the browser test confirms no screen scrolls sideways at 390 px width.")

    add_heading_2(doc, "6.3 Backend Implementation and API Routes")
    add_body_p(doc, "Table 6.1 lists the main endpoints. All routes except health, login, registration, public settings and the budget simulator require a valid token.")
    add_table_caption(doc, "Table 6.1: Main REST API Endpoints")
    add_styled_table(doc, ["Method", "Endpoint", "Access", "Description"], [
        ["POST", "/api/auth/register", "Public", "Create account (first admin automatic); validates e-mail and password"],
        ["POST", "/api/auth/login", "Public", "Verify hashed password, return signed 7-day token"],
        ["GET", "/api/auth/me", "User", "Return the logged-in user"],
        ["POST", "/api/campaigns/generate-stream", "User", "Stream campaign generation as Server-Sent Events and save it"],
        ["GET", "/api/campaigns", "User", "Own campaigns (administrators: all campaigns)"],
        ["GET / DELETE", "/api/campaigns/<id>", "Owner / Admin", "Read or delete one campaign"],
        ["PUT", "/api/campaigns/<id>/image", "Owner / Admin", "Attach the generated image to a campaign"],
        ["POST", "/api/image/generate", "User", "Create a visual (mode auto / photo / ai) with verification"],
        ["POST", "/api/budget/plan", "Public", "Channel allocation and ROAS simulation"],
        ["GET / POST / PUT / DELETE", "/api/brands[/<id>]", "User", "Manage brand profiles"],
        ["GET", "/api/admin/metrics, /activity-logs", "Admin", "Usage metrics and audit log"],
        ["GET / POST / PATCH / DELETE", "/api/admin/users[/<id>]", "Admin", "Create, change role, enable/disable, delete users"],
        ["POST", "/api/admin/users/<id>/reset-password", "Admin", "Set a new password"],
        ["GET / PUT", "/api/admin/settings", "Admin", "Feature switches, limits, announcement"],
        ["GET", "/api/settings/public, /api/health", "Public", "Enabled features; service status"],
    ], [1.0, 2.1, 1.0, 2.4])

    add_heading_2(doc, "6.4 Security Implementation")
    add_bullet_p(doc, "Passwords:", "Stored only as salted Werkzeug hashes; login returns the same error for an unknown e-mail and a wrong password so account existence is not revealed.")
    add_bullet_p(doc, "Tokens:", "Signed with itsdangerous using SECRET_KEY and valid for seven days; a disabled user's existing tokens stop working immediately.")
    add_bullet_p(doc, "Authorisation:", "Every campaign and brand query is filtered by owner; other users receive 404. Administrators cannot disable, demote or delete themselves, and the last active administrator cannot be removed.")
    add_bullet_p(doc, "Abuse protection:", "Per-user hourly limits for campaigns and images (configurable by the administrator), a limit of ten failed logins per address per 15 minutes (successful logins are never limited), a registration limit per address, a 10 MB request limit, validation that stored images are data or https URLs, and the Werkzeug debugger disabled by default.")

    add_heading_2(doc, "6.5 Database Implementation")
    add_body_p(doc, "database_service.py defines the five models and all queries. The connection string comes from DATABASE_URL (postgres:// URLs are converted for the psycopg 3 driver), falling back to a local SQLite file. Administrator metrics are computed only from stored data — counts of users and campaigns, campaigns per platform and goal, images and failures in the last seven days, average generation times and provider usage from the activity log.")

    add_heading_2(doc, "6.6 Gemini Campaign Engine Implementation")
    add_body_p(doc, "stream_marketing_campaign() is a Python generator that yields progress events; the Flask route converts each event into a Server-Sent Event, and the non-streaming endpoint simply consumes the same generator:")
    add_code_block(doc, (
        "for model_name in _available_models():              # skips models that failed recently\n"
        "    yield {'type': 'status', 'message': f'Writing campaign with {model_name}...'}\n"
        "    try:\n"
        "        for chunk in client.models.generate_content_stream(model=model_name,\n"
        "                                                           contents=prompt, config=config):\n"
        "            yield {'type': 'chunk', 'text': chunk.text}\n"
        "        parsed = json.loads(_clean_json_string(full_text))\n"
        "        if not all(k in parsed for k in REQUIRED_KEYS):\n"
        "            raise ValueError('missing sections')\n"
        "        yield {'type': 'done', 'campaign': parsed, 'meta': {'source': 'gemini', 'model': model_name}}\n"
        "        return\n"
        "    except Exception as e:\n"
        "        _mark_down(model_name, str(e))               # 503 / 429 / 404 -> skip for 2 minutes\n"
        "        yield {'type': 'reset'}\n"
        "yield _template_result(..., warning='All Gemini models were unavailable ...')\n"
    ))

    add_heading_2(doc, "6.7 Visual Engine Implementation")
    add_body_p(doc, "generate_image() in image_service.py coordinates the pipeline of Figure 4.7. Style presets are appended after the analysed prompt (Table 6.2). The core verification loop is:")
    add_table_caption(doc, "Table 6.2: Visual Style Presets")
    add_styled_table(doc, ["Style", "Modifier appended to the prompt"], [
        ["Photorealistic", "photorealistic commercial photography, professional studio lighting, sharp focus, high detail"],
        ["3D Render", "high-end 3D render, octane render, ray-traced soft shadows, clean materials, high detail"],
        ["Cyberpunk", "cyberpunk aesthetic, dark background with neon cyan and magenta glow, glossy reflections"],
        ["Minimalist", "minimalist composition, clean plain backdrop, soft natural light, lots of negative space"],
        ["Luxury", "luxury advertising photography, dark marble, dramatic low-key lighting, gold accents"],
        ["Vibrant Pop", "bold vibrant colors, clean gradient background, high-contrast lighting, pop-art energy"],
    ], [1.4, 5.0])
    add_code_block(doc, (
        "for attempt in range(MAX_ATTEMPTS):                       # up to 3\n"
        "    prompt = [model_prompt, simple_prompt, bare_prompt][attempt]\n"
        "    logo = f'{prompt} The \"{brand}\" brand logo is printed clearly on the product.' if brand and attempt < 2 else prompt\n"
        "    candidate = (_try_gemini(...) or _try_cloudflare(logo, ...) or _try_hf(logo, ...)\n"
        "                 or _try_pollinations(prompt, ...))         # weak engine never gets the brand\n"
        "    if not candidate:\n"
        "        break                                           # no provider available\n"
        "    ok, seen = verify_image(candidate['_raw'], mime, subject, people_requested, brand=brand)\n"
        "    if ok is False:\n"
        "        rejected.append(seen); continue                 # e.g. 'a portrait of a woman'\n"
        "    result = candidate; break\n"
        "if not result and rejected:\n"
        "    return {'success': False, 'error': f'The image engine kept producing the wrong picture ({rejected[-1]}) ...'}\n"
    ))
    add_body_p(doc, "photo_service.find_product_photo() searches each library with query variants (for example \"JBL wireless earbuds\" then \"JBL earbuds\"), downloads a small preview of each candidate for verification, compares up to three approved photos by their advertising score and returns the best one (at most 2,048 px) with its title, creator, licence, licence URL and source page. Unsplash photos are hot-linked from Unsplash's CDN as its API guidelines require; other sources are stored as data URLs.")

    add_heading_2(doc, "6.8 Budget Planner Implementation")
    add_body_p(doc, "budget_routes.py combines industry benchmarks (Table 5.1) with goal-specific channel weights and a duration pacing factor, validates inputs (non-numeric and non-positive budgets are rejected) and maps user-facing labels such as \"Fashion & Apparel\" onto benchmark keys:")

    add_heading_2(doc, "6.9 Testing and Deployment Implementation")
    add_bullet_p(doc, "Unit tests:", "33 pytest tests run against a temporary database with all AI calls replaced by stubs (and every optional service key blanked), covering authentication, failed-login limiting, data isolation, streaming, brands, budget validation, administration, demo data, image verification, logo checks, photo scoring and the Cloudflare and Unsplash integrations.")
    add_bullet_p(doc, "Live tests:", "A 77-check script exercises every endpoint against the running server with real Gemini and image providers, and a 32-step Playwright script drives Microsoft Edge through every screen, including the full-screen image viewer and a 390 px phone layout.")
    add_bullet_p(doc, "Deployment:", "render.yaml defines one Render web service running gunicorn with one process and eight threads (so streaming responses and the shared rate limiter work correctly), a health check on /api/health, a generated SECRET_KEY and a DATABASE_URL pointing to a hosted PostgreSQL database.")

    add_page_break(doc)
