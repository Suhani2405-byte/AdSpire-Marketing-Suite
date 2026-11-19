from build_report.docx_helper import (
    add_page_break, add_heading_1, add_heading_2, add_heading_3,
    add_body_p, add_bullet_p, add_figure_image, add_styled_table, add_table_caption
)

def build_chapter_3(doc):
    add_heading_1(doc, "CHAPTER 3: SYSTEM ANALYSIS")

    add_heading_2(doc, "3.1 Existing System Analysis")
    add_body_p(doc, "In the conventional marketing operational paradigm, developing an omni-channel advertising campaign is a highly manual, labor-intensive, and non-deterministic process. A typical workflow across marketing agencies and corporate enterprises involves five disjointed stages:")

    add_bullet_p(doc, "Briefing & Strategy Formulation:", "A brand manager drafts a textual creative brief in a collaborative document (e.g., Google Docs). A senior strategist conducts manual competitive research to outline target demographics and positioning.")
    add_bullet_p(doc, "Copywriting Production:", "A creative copywriter crafts ad headlines, primary text, email newsletters, and social media captions. Producing multi-angle variants for A/B testing typically requires 2 to 4 working days of iterative drafting.")
    add_bullet_p(doc, "Graphic Design & Art Direction:", "Designers create product mockups or search stock image repositories for commercial assets. Custom photo shoots or 3D rendering cycles take 3 to 7 days, with significant billing costs.")
    add_bullet_p(doc, "Media Planning & Spreadsheet Budgeting:", "A media buyer builds a spreadsheet model using static formulas to estimate impressions, clicks, and budget distribution across ad networks, frequently detached from the creative deliverables.")

    add_body_p(doc, "This traditional paradigm suffers from severe latency (averaging 7 to 14 days from brief to launch), high cost (agency retainers routinely exceed $3,000–$10,000 per month), creative fatigue, and a high probability of human error during cross-channel handoffs.")

    add_heading_2(doc, "3.2 Proposed System Architecture and Advantages")
    add_body_p(doc, "Adspire AI fundamentally redesigns the marketing formulation lifecycle into an autonomous, instantaneous, and unified software ecosystem. The user simply specifies the product name, core description, target audience, primary channel, and campaign objective. The system then executes an end-to-end multi-agent pipeline:")

    add_bullet_p(doc, "Instantaneous Turnaround:", "Compresses multi-day briefing and asset production cycles into one to two minutes, with the campaign text visible while it is being written.")
    add_bullet_p(doc, "Full-Spectrum Strategic Briefs:", "Synthesizes comprehensive buyer personas, psychographic pain points, objection-busting frameworks, value propositions, primary ad copy with dual A/B testing variants, Instagram captions with curated hashtags, LinkedIn thought leadership posts, viral TikTok scripts, email newsletters, and 7-day distribution calendars.")
    add_bullet_p(doc, "Photorealistic Commercial Visual Studio:", "Returns licensed real photographs for branded products and AI-generated images otherwise, with every image verified by Gemini vision to really show the requested product.")
    add_bullet_p(doc, "Empirical Predictive ROAS Modeling:", "Employs an algorithmic financial simulator that computes channel-by-channel CPC, CTR, impressions, clicks, conversions, CPA, and projected ROAS with duration-based pacing adjustments.")
    add_bullet_p(doc, "Interactive Live Social Previews:", "Provides pixel-accurate, interactive client-side simulators mimicking authentic user feeds on Instagram, TikTok, LinkedIn, and Google Search.")
    add_bullet_p(doc, "Relational Persistence & History:", "Stores every campaign with its image in a private per-user library (SQLite locally, PostgreSQL in production) with search and PDF, Markdown and JSON export, under an administrator who controls users and features.")

    add_heading_2(doc, "3.3 Functional Requirements Specification")

    add_bullet_p(doc, "FR-1: Campaign Brief Ingestion & Validation:", "The system shall accept product name, description, target audience, platform, and marketing goal, validating that mandatory inputs are populated prior to invoking backend APIs.")
    add_bullet_p(doc, "FR-2: Autonomous Structured Campaign Generation:", "The backend shall construct a specialized JSON generation prompt and interface with Google Gemini (gemini-3.8-flash) using strict MIME type application/json to produce persona profiles, ad copy variants, social deliverables, email newsletters, and 7-day roadmaps.")
    add_bullet_p(doc, "FR-3: Text-to-Image Visual Asset Synthesis:", "The system shall accept a visual prompt, an image source mode (Auto, Real Photo, AI), an aspect ratio (1:1, 16:9, 9:16) and a style preset, and shall return only images that an AI check confirms show the requested product, together with the engine used and, for photos, the credit and licence.")
    add_bullet_p(doc, "FR-4: Financial Simulation & Budget Allocation:", "The system shall compute real-time budget distribution, daily spend pacing, impressions, clicks, conversions, CPA, projected revenue, and ROAS across six channels based on industry benchmarks and duration multipliers.")
    add_bullet_p(doc, "FR-5: Interactive Social Feed Mockup Rendering:", "The frontend shall render authentic client-side mockups for Instagram (with clickable Like and Bookmark states), TikTok (vertical video player with rotating sound tags), LinkedIn (corporate sponsored card), and Google SERP snippets.")
    add_bullet_p(doc, "FR-6: Relational Campaign Storage & Library Management:", "The system shall save every generated campaign and its image for the logged-in user, and allow the user to search, reopen, export (PDF, Markdown, JSON) and delete them. Users shall never see other users' campaigns.")
    add_bullet_p(doc, "FR-7: Accounts & Administration:", "The system shall support registration and login, two roles (marketer and administrator), brand profiles, and an administration panel to create, promote, disable, reset and delete users, switch features on or off, set hourly limits, publish an announcement and view real usage metrics and an activity log.")

    add_heading_2(doc, "3.4 Non-Functional Requirements Specification")

    add_bullet_p(doc, "NFR-1: Performance & Latency:", "Campaign text shall start appearing as soon as Gemini begins responding, and a stalled AI model shall be abandoned after 60 seconds in favour of the next one. Non-AI operations (login, library, budget simulation) shall respond in well under one second.")
    add_bullet_p(doc, "NFR-2: Reliability & Fault Tolerance:", "If an AI service is overloaded, out of quota or offline, the system shall fall back to other models or providers and, when nothing is available, show a clear explanation instead of crashing or presenting wrong content.")
    add_bullet_p(doc, "NFR-3: Usability & User Experience (UX):", "The user interface shall be completely responsive, utilizing Tailwind CSS 4 to support seamless layout adjustments across desktop workstations, tablets, and mobile devices.")
    add_bullet_p(doc, "NFR-4: Data Integrity & Schema Compliance:", "All LLM responses shall be sanitized to strip Markdown code fences and validated to ensure strict JSON schema parsing before delivery to the client.")

    add_heading_2(doc, "3.5 Software Requirements and Toolchain")
    add_body_p(doc, "The comprehensive software development and execution environment is documented in Table 3.2:")

    add_table_caption(doc, "Table 3.2: Software Stack and Versions")
    headers = ["Software Layer", "Technology / Framework", "Version / Details"]
    rows = [
        ["Operating System", "Microsoft Windows / Linux / macOS", "Windows 11 (64-bit) verified"],
        ["Frontend Library", "React.js", "Version 19.2.8"],
        ["Frontend Bundler", "Vite", "Version 8.2.0"],
        ["CSS Framework", "Tailwind CSS", "Version 4.3.3 with @tailwindcss/vite"],
        ["Iconography & Charts", "Lucide React, Chart.js", "lucide-react 1.31, chart.js 4.5 + react-chartjs-2"],
        ["Backend Runtime", "Python", "Version 3.13 (local), 3.11 (Render)"],
        ["Backend Framework", "Flask", "Version 3.1.3 (WSGI Microframework)"],
        ["Cross-Origin Middleware", "Flask-CORS", "Version 6.0.5"],
        ["Object Relational Mapper", "SQLAlchemy", "Version 2.0.51"],
        ["Database Engine", "SQLite / PostgreSQL", "SQLite locally; PostgreSQL via psycopg 3 in production"],
        ["Generative Text LLM", "Google Gemini API", "google-genai v2.20.0 (gemini-3.8-flash)"],
        ["Image Sources", "Cloudflare Workers AI (FLUX.1-schnell), Gemini image, Hugging Face, Pollinations; Unsplash, Pixabay, Pexels, Openverse, Wikimedia", "AI generation with brand logos + licensed real photos, verified by Gemini vision"],
        ["Security", "Werkzeug, itsdangerous", "Salted password hashes, signed 7-day tokens"],
        ["Testing", "pytest, Playwright", "33 unit tests, live API test, browser test (Edge)"],
        ["Deployment", "gunicorn, Render", "render.yaml blueprint, gthread workers"]
    ]
    add_styled_table(doc, headers, rows, [2.0, 2.2, 2.0])

    add_heading_2(doc, "3.6 Feasibility Study")
    add_body_p(doc, "A rigorous feasibility analysis was conducted across technical, economic, and operational dimensions:")

    add_bullet_p(doc, "Technical Feasibility:", "The integration of React 19, Python Flask, and Google Gemini API is highly feasible. Both the frontend and backend utilize modern, mature toolchains with comprehensive documentation, proven asynchronous handling, and robust JSON serialization standards.")
    add_bullet_p(doc, "Economic Feasibility:", "The development cost of Adspire AI is exceptionally low. The software stack relies entirely on open-source libraries (React, Vite, Flask, SQLite, Tailwind CSS). Cloud API calls to Google Gemini offer generous free-tier quotas and cost-effective token pricing, eliminating the need for expensive dedicated on-premise GPU clusters.")
    add_bullet_p(doc, "Operational Feasibility:", "The platform features an intuitive, self-explanatory web interface requiring no prior programming knowledge or prompt engineering experience from end users. Marketers, entrepreneurs, and students can operate the system seamlessly via straightforward form inputs and interactive sliders.")

    add_page_break(doc)
