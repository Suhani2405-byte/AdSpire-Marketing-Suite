import os
from build_report.docx_helper import (
    add_page_break, add_heading_1, add_heading_2, add_heading_3,
    add_body_p, add_bullet_p, add_figure_image, add_styled_table,
    add_code_block, add_table_caption
)


def build_chapter_4(doc):
    add_heading_1(doc, "CHAPTER 4: SYSTEM DESIGN")

    add_heading_2(doc, "4.1 Overall System Architecture")
    add_body_p(doc, "Adspire AI follows a layered client–server architecture. Each layer has one responsibility and talks only to the layer below it, which keeps the code easy to test, replace and deploy. In production a single Flask process serves both the compiled React application and the REST API from the same origin, so no cross-origin configuration is needed for end users. The system is organised into four tiers:")

    add_bullet_p(doc, "1. Presentation Tier (React SPA):", "A React 19 single-page application built with Vite. Screens are separate components (LoginPage, CampaignStudio, CampaignOutput, AdMockups, VisualStudio, BudgetPlanner, Library, AdminDashboard) that share state through a React context (AppState). A small API module attaches the login token to every request and reads streamed campaign text.")
    add_bullet_p(doc, "2. Application Tier (Flask API):", "Seven Flask blueprints (auth, campaigns, image, budget, brands, admin, settings) expose a JSON REST API under /api. Cross-cutting rules are implemented as decorators: login_required, admin_required, feature switches controlled by the administrator, and a per-user hourly rate limiter.")
    add_bullet_p(doc, "3. Service Tier:", "Plain Python modules hold the business logic: gemini_service (prompting, streaming and model fail-over), image_service (prompt analysis, image generation, vision verification and retries), photo_service (licensed real-photo search), database_service (SQLAlchemy models and queries) and auth_service (password hashing and signed tokens).")
    add_bullet_p(doc, "4. Data & External Services Tier:", "SQLite is used locally and PostgreSQL in production through the same SQLAlchemy models (selected by the DATABASE_URL variable). External services are Google Gemini (text, vision and image models), FLUX.1-schnell on Cloudflare Workers AI and Hugging Face, Pollinations, and the Unsplash, Pixabay, Pexels, Openverse and Wikimedia photo libraries.")

    add_figure_image(doc, os.path.abspath("report_assets/fig_4_1_system_architecture.png"),
                     "Figure 4.1: Layered System Architecture of Adspire AI", width_inches=4.2)

    add_heading_2(doc, "4.2 Frontend Architecture")
    add_body_p(doc, "The entry point (main.jsx) renders App.jsx, which acts only as an authentication gate and navigation shell. When no valid token is stored, the LoginPage is shown; otherwise the AppStateProvider wraps the selected screen. This replaced the original single 1,600-line component with small, focused files:")
    add_bullet_p(doc, "AppState context:", "Holds the campaign form, the generated campaign, streaming progress, the current visual and its metadata, the user's library and brand profiles, and exposes actions such as handleGenerateCampaign and handleGenerateVisual to every screen.")
    add_bullet_p(doc, "api.js:", "Creates an Axios instance that adds the bearer token, logs the user out automatically when the server reports an expired token, and implements streamCampaign(), which reads Server-Sent Events from a fetch() response so campaign text appears while it is being written.")
    add_bullet_p(doc, "Feature-aware navigation:", "Tabs are built from the user's role and the administrator's public settings: switched-off features disappear for marketers, and the Admin Panel tab appears only for administrators.")
    add_bullet_p(doc, "Utilities:", "exporters.js converts a campaign to PDF (print view), Markdown and JSON; charts.js registers Chart.js elements used by the budget and admin charts.")

    add_heading_2(doc, "4.3 Backend Architecture")
    add_body_p(doc, "The backend (app.py) registers the blueprints, serves the compiled frontend, returns JSON errors for unknown API routes, limits request size to 10 MB and adds basic security headers. Responsibilities of each blueprint are:")
    add_bullet_p(doc, "auth (/api/auth):", "Registration with validation, login with hashed-password verification, and /me to restore a session. The first account (or any e-mail in ADMIN_EMAILS) becomes administrator.")
    add_bullet_p(doc, "campaigns (/api/campaigns):", "Streaming and non-streaming generation, listing (own campaigns for marketers, all campaigns for administrators), retrieval, deletion and attaching a generated image.")
    add_bullet_p(doc, "image (/api/image):", "Image creation in Auto, Real Photo or AI mode, protected by login, a feature switch and an hourly limit.")
    add_bullet_p(doc, "budget (/api/budget):", "The ROAS and channel-allocation simulation.")
    add_bullet_p(doc, "brands (/api/brands):", "Create, update, list and delete saved brand profiles.")
    add_bullet_p(doc, "admin and settings (/api/admin, /api/settings):", "Usage metrics, activity log, user management, feature switches, limits and the announcement banner; /api/settings/public tells the frontend which features are enabled.")

    add_heading_2(doc, "4.4 Database Design")
    add_body_p(doc, "The schema contains five tables. Campaign content is stored as a JSON document inside a relational row, which keeps querying simple (by owner, platform, goal and date) while allowing the AI output structure to evolve. Table 4.1 lists the main tables:")
    add_table_caption(doc, "Table 4.1: Database Tables and Key Columns")
    add_styled_table(doc, ["Table", "Key Columns", "Purpose"], [
        ["users", "id, name, email (unique), password_hash, role, is_active, created_at", "Accounts, roles (admin / marketer) and enable/disable state"],
        ["campaigns", "id, user_id → users, product_name, platform, goal, campaign_content (JSON), image_url, image_thumb, source, created_at", "Every generated campaign with its full image, a small thumbnail for library cards, and the model that produced it"],
        ["brands", "id, user_id → users, name, industry, tone, audience, description", "Reusable brand profiles that pre-fill the campaign form"],
        ["activity_logs", "id, user_id → users, action, detail, provider, duration_ms, created_at", "Audit trail and the data source for all admin metrics"],
        ["settings", "key, value (JSON)", "Administrator settings: feature switches, limits, announcement"],
    ], [1.2, 3.1, 2.1])

    add_figure_image(doc, os.path.abspath("report_assets/fig_4_5_er_diagram.png"),
                     "Figure 4.2: Entity-Relationship Diagram", width_inches=5.0)

    add_heading_2(doc, "4.5 Data Flow Diagram")
    add_body_p(doc, "Figure 4.3 shows the Level-1 data flow. A marketer authenticates (process 1.0) against the users store and receives a signed token. The product brief flows into campaign generation (2.0), which exchanges a structured prompt and a JSON stream with Gemini and writes the campaign to the campaigns store. Visual creation (3.0) exchanges prompts, images and verification results with the image engines and photo libraries and attaches the chosen image to the campaign. Budget simulation (4.0) is a pure calculation. Administration (5.0) updates users and settings and reads the activity log, which processes 2.0 and 3.0 write to.")
    add_figure_image(doc, os.path.abspath("report_assets/fig_4_2_dfd_level1.png"),
                     "Figure 4.3: Data Flow Diagram (Level 1)", width_inches=6.2)

    add_heading_2(doc, "4.6 Use Case Diagram")
    add_body_p(doc, "There are two human actors and two external system actors. The Marketer performs use cases UC1–UC8 (account, brand profiles, campaign generation, visuals, mock-ups, budget simulation, library and export). The Administrator inherits all marketer use cases and additionally manages users and roles (UC9), feature switches and limits (UC10) and monitors usage and activity (UC11). Gemini supports UC3 and UC4, and the image engines and photo libraries support UC4.")
    add_figure_image(doc, os.path.abspath("report_assets/fig_4_3_use_case.png"),
                     "Figure 4.4: Use Case Diagram", width_inches=5.4)

    add_heading_2(doc, "4.7 Workflow Design")
    add_body_p(doc, "Figure 4.6 shows the campaign generation workflow. After the security checks, the backend builds a structured prompt and calls the first Gemini model in streaming mode. A model that is overloaded (HTTP 503), out of quota (429) or silent for 60 seconds is skipped for two minutes and the next model is tried. Only when every model fails is a clearly labelled template returned.")
    add_figure_image(doc, os.path.abspath("report_assets/fig_4_6_campaign_workflow.png"),
                     "Figure 4.6: Campaign Generation Workflow with Model Fail-Over", width_inches=5.0)
    add_body_p(doc, "Figure 4.7 shows the visual workflow, the most important correctness improvement of the project. Free image models do not know brand names and often draw an unrelated picture (for example a portrait instead of earbuds). The design therefore (a) uses real licensed photographs for plain branded product requests, choosing the best-scoring candidate, (b) sends described scenes to FLUX on Cloudflare Workers AI, which is asked to print the brand name as a logo, while the weak free fallback only receives a brand-free description, and (c) checks every candidate with Gemini vision — product type, unwanted people and logo spelling — before it can be shown.")
    add_figure_image(doc, os.path.abspath("report_assets/fig_4_7_image_workflow.png"),
                     "Figure 4.7: Visual Creation Workflow with AI Verification", width_inches=4.4)

    add_page_break(doc)
