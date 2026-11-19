import os
from build_report.docx_helper import (
    add_page_break, add_heading_1, add_heading_2, add_heading_3,
    add_body_p, add_bullet_p, add_figure_image, add_styled_table, add_table_caption
)

def build_chapter_5(doc):
    add_heading_1(doc, "CHAPTER 5: METHODOLOGY")

    add_heading_2(doc, "5.1 Development Methodology")
    add_body_p(doc, "The development of Adspire AI was conducted following an Agile Software Development Lifecycle (SDLC) combined with rapid iterative prototyping. Given the non-deterministic nature of generative artificial intelligence and the need for responsive user interfaces, the development lifecycle was divided into six two-week engineering sprints:")

    add_bullet_p(doc, "Sprint 1 – Architectural Scaffolding & API Proof-of-Concept:", "Established the project workspace, installed the Node.js and Python virtual environments, verified Vite and Flask hot-reloading, configured SQLite database bindings via SQLAlchemy, and executed initial curl tests against the Google Gemini API.")
    add_bullet_p(doc, "Sprint 2 – Backend Microservices & Prompt Engineering:", "Engineered campaign_routes.py, image_routes.py, budget_routes.py, and admin_routes.py. Developed rigorous structured JSON prompt templates and implemented regex-based JSON cleaning filters.")
    add_bullet_p(doc, "Sprint 3 – Frontend Componentization & State Management:", "Constructed the React 19 single-page application using Tailwind CSS 4. Built modular form controls, reactive sliders, non-blocking loading states, and output sub-tabs.")
    add_bullet_p(doc, "Sprint 4 – Visual Studio & Interactive Social Mockups:", "Integrated the Gemini, Hugging Face FLUX.1 and Pollinations image providers. Engineered interactive client-side mockups (Instagram, TikTok, LinkedIn, Google SERP) with local state toggles.")
    add_bullet_p(doc, "Sprint 5 – Accounts, Administration & Refactoring:", "Added registration and login with hashed passwords and signed tokens, per-user data isolation, brand profiles, the activity log, the Admin Panel (user management, feature switches, limits, announcement) and split the frontend into components with a shared React context.")
    add_bullet_p(doc, "Sprint 6 – Reliability, Image Verification, Testing & Deployment:", "Introduced streaming generation with model fail-over, prompt analysis, real-photo search and Gemini vision verification for images, wrote automated unit, API and browser tests, and prepared the Render deployment (render.yaml, gunicorn, PostgreSQL support).")

    add_heading_2(doc, "5.2 Database Integration and ORM Lifecycle")
    add_body_p(doc, "Database operations use SQLAlchemy 2. The same models run on SQLite locally and on PostgreSQL in production; the engine is chosen from the DATABASE_URL environment variable:")

    add_bullet_p(doc, "Declarative Model Mapping:", "Five declarative models (User, Campaign, Brand, ActivityLog, Setting) map Python classes to tables. A small migration routine adds columns introduced after the first release (user_id, source, is_active) to existing databases, so older data is preserved.")
    add_bullet_p(doc, "Session Management & Thread Safety:", "Each operation opens its own session in a with-block, so sessions are always closed, and SQLite is opened with check_same_thread disabled because gunicorn serves requests from several threads.")
    add_bullet_p(doc, "Hybrid Relational-JSON Storage:", "While top-level metadata (product title, channel, objective, creation timestamp) is stored in structured relational columns for rapid filtering and sorting, complex marketing deliverables (personas, A/B variants, social posts, calendars) are serialized as clean JSON text, offering schema flexibility without relational overhead.")

    add_heading_2(doc, "5.3 AI Integration and Prompt Engineering Methodology")
    add_body_p(doc, "A critical innovation in Adspire AI lies in its structured prompt engineering methodology for Google Gemini:")

    add_bullet_p(doc, "Role-Based System Prompting:", "The prompt explicitly instructs the LLM to adopt the persona of an elite Autonomous Marketing Director and Chief Marketing Officer, establishing a tone of commercial authority, persuasive copywriting, and rigorous strategic reasoning.")
    add_bullet_p(doc, "Strict JSON Schema Enforcement:", "Rather than requesting freeform text, the prompt supplies a comprehensive JSON skeleton specifying exact object keys (campaign_title, tagline, executive_summary, target_persona, value_propositions, ad_copies, social_posts, email_newsletter, content_calendar_7day, image_prompt, budget_recommendations). The Gemini API is invoked with response_mime_type='application/json' and temperature=0.7 to maximize creativity while ensuring syntactic compliance.")
    add_bullet_p(doc, "Heuristic JSON Sanitization:", "To guard against edge cases where the model wraps JSON in Markdown code fences (e.g., ```json ... ```), the service passes raw output through a sanitization function (_clean_json_string) that strips code blocks and normalizes whitespace prior to json.loads() parsing.")
    add_bullet_p(doc, "Autonomous Model Failover Cascade:", "The service tries six Gemini models in order (gemini-3.8-flash, gemini-3.5-flash, gemini-3-flash-preview, gemini-flash-latest, gemini-3.1-flash-lite, gemini-flash-lite-latest). A model that returns 503, 429 or 404, or stalls for 60 seconds, is skipped for two minutes. If all models fail, a template campaign is returned and the user is explicitly warned instead of being shown generic text as if it were AI output.")

    add_heading_2(doc, "5.4 Campaign Generation Workflow Pipeline")
    add_body_p(doc, "The campaign generation workflow executes through five sequential computational stages as illustrated in Figure 4.6 (Chapter 4):")
    
    add_bullet_p(doc, "Stage 1 – Ingestion:", "The user enters product, description, audience, platform, goal, industry and tone, or loads a saved brand profile.")
    add_bullet_p(doc, "Stage 2 – Payload Dispatch:", "The frontend validates the fields and opens a streaming POST request to /api/campaigns/generate-stream with the login token.")
    add_bullet_p(doc, "Stage 3 – Gemini LLM Processing:", "The backend checks login, feature switch and hourly limit, builds the structured prompt and streams Gemini output back to the browser as Server-Sent Events.")
    add_bullet_p(doc, "Stage 4 – Sanitization & Relational Save:", "The complete text is parsed, checked for all required sections, saved with its owner and model name, and recorded in the activity log.")
    add_bullet_p(doc, "Stage 5 – Interactive Rendering:", "The browser renders the six result tabs and automatically requests a matching product visual, which is attached to the saved campaign.")

    add_heading_2(doc, "5.5 Creative Visual Synthesis Workflow Pipeline")
    add_body_p(doc, "The visual methodology (Figure 4.7) was redesigned after testing showed that free image models frequently return unrelated pictures for branded prompts — for example a woman's portrait for \"JBL earbuds\". The final pipeline has five steps:")

    add_bullet_p(doc, "1. Prompt Analysis:", "A fast Gemini model returns the generic product type, the brand (for any company), a photo-search query, whether the user described a custom scene, and a brand-free visual prompt that describes the product's shape, colours and materials, avoids portrait-photography wording and never shows wearables being worn.")
    add_bullet_p(doc, "2. Real Product Photos:", "In Real Photo mode, or in Auto mode for a plain branded request (no described scene), licensed photo libraries are searched (Pexels, Unsplash, Pixabay, Openverse, Wikimedia) using query variants from specific to broad. Gemini scores each matching photo from 1 to 10 as an advertising image and the best one is used; in Auto mode a photo scoring below 5 is skipped in favour of AI generation.")
    add_bullet_p(doc, "3. AI Generation:", "Otherwise the providers are tried in order of quality: Gemini image models, FLUX.1-schnell on Cloudflare Workers AI, FLUX.1-schnell on Hugging Face, then Pollinations. FLUX is asked to print the brand name clearly on the product; Pollinations only receives the brand-free prompt and its 768 px output is upscaled two times with Lanczos resampling.")
    add_bullet_p(doc, "4. Vision Verification:", "Every candidate is shown to Gemini vision, which reports whether the requested product type (and brand, for photos) is the main subject, whether an unwanted person is present, and — for branded AI images — whether the logo is spelled exactly right.")
    add_bullet_p(doc, "5. Retry or Refuse:", "A rejected AI image is regenerated with a new seed and progressively simpler prompts (up to three attempts, the last one without the logo requirement); a rejected photo is replaced by the next candidate. If nothing passes, the user receives a clear message — an unrelated image is never displayed.")

    add_heading_2(doc, "5.6 Financial Simulation and Analytics Workflow")
    add_body_p(doc, "The budget simulation methodology translates abstract financial budgets into actionable channel allocations using empirical industry benchmarks:")

    add_bullet_p(doc, "Empirical Industry Benchmarks:", "The system incorporates verified benchmark matrices for major commercial verticals (Consumer Electronics & D2C, SaaS & B2B Tech, Fashion & Beauty, Health & Wellness) detailing standard CPC, CTR, conversion rates, and Average Order Value (AOV) across six channels as documented in Table 5.1:")

    add_table_caption(doc, "Table 5.1: Industry Benchmark Matrix Used by the Budget Simulator")
    headers = ["Industry Vertical", "Meta CPC / CTR", "Google CPC / CTR", "LinkedIn CPC / CTR", "TikTok CPC / CTR", "Conv Rate / AOV"]
    rows = [
        ["Consumer Electronics & D2C", "$0.85 / 2.1%", "$1.20 / 3.8%", "$4.50 / 1.1%", "$0.65 / 2.9%", "3.2% / $75.00"],
        ["SaaS & B2B Tech", "$1.80 / 1.4%", "$3.50 / 2.9%", "$6.80 / 1.8%", "$1.20 / 1.5%", "2.1% / $250.00"],
        ["Fashion & Beauty", "$0.70 / 2.8%", "$1.10 / 3.4%", "$3.90 / 0.9%", "$0.50 / 3.5%", "3.8% / $55.00"],
        ["Health & Wellness", "$0.95 / 2.3%", "$1.60 / 3.2%", "$4.20 / 1.2%", "$0.75 / 2.7%", "3.0% / $75.00"]
    ]
    add_styled_table(doc, headers, rows, [1.6, 1.2, 1.2, 1.2, 1.2, 1.2])

    add_bullet_p(doc, "Algorithmic Pacing Multiplier:", "Unlike static spreadsheets, Adspire AI models algorithmic pacing. Sustained campaigns allow advertising algorithms (pixel tracking, lookalike modeling) to optimize bids. The system computes a duration pacing factor:")
    
    add_body_p(doc, "duration_factor = 0.85 + (min(duration_days, 90) / 90.0) * 0.35")

    add_body_p(doc, "Short 7-day bursts experience slight conversion penalties (~0.88x) due to initial bid volatility, while sustained 30-to-90-day campaigns achieve compounding conversion efficiency (~1.22x). Projected revenue, ROAS, CPA, and net profit are computed directly from these mathematically adjusted figures.")

    add_page_break(doc)
