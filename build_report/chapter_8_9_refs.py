import docx
from docx.shared import Inches, Pt, RGBColor
from build_report.docx_helper import (
    add_page_break, add_heading_1, add_heading_2, add_heading_3,
    add_body_p, add_bullet_p, add_figure_image, add_styled_table
)

def build_chapter_8_9_refs(doc):
    # =============================================================
    # CHAPTER 8: CHALLENGES AND LIMITATIONS
    # =============================================================
    add_heading_1(doc, "CHAPTER 8: CHALLENGES AND LIMITATIONS")

    add_heading_2(doc, "8.1 Technical Challenges")
    add_body_p(doc, "During the design, implementation, and optimization of Adspire AI, several complex technical engineering challenges were encountered and methodically resolved:")

    add_bullet_p(doc, "1. Enforcing Deterministic JSON Structure in LLMs:", "Large Language Models inherently produce conversational, non-deterministic text. During initial development, the model occasionally included conversational preambles (e.g., 'Sure, here is your marketing campaign:') or enclosed JSON within Markdown code fences (```json ... ```). This caused standard json.loads() parsers in Python to raise JSONDecodeError exceptions. To resolve this, the system integrated response_mime_type='application/json' via the google-genai SDK, coupled with a robust regex-based sanitization filter (_clean_json_string) to ensure flawless parsing.")
    add_bullet_p(doc, "2. Wrong Images from Free Image Models:", "The free Pollinations tier silently ignores the requested FLUX model and uses a weaker model (reported in its x-model-used header as \"sana\"). It does not know brand names and, for prompts such as \"JBL earbuds\" with portrait-style wording (editorial, rim lighting), it drew a woman's portrait in every test. An earlier version of the project hid this by returning keyword-matched stock photos, which showed unrelated products. The final design analyses the prompt with Gemini, uses licensed real photos for branded products, rewrites prompts into brand-free visual descriptions, and verifies every image with Gemini vision, retrying or refusing instead of showing a wrong image.")
    add_bullet_p(doc, "3. Cross-Origin Resource Sharing (CORS) & Path Resolution:", "In development the React app runs on port 5173 and Flask on 5000. Instead of allowing every origin, the Vite server proxies /api to Flask, CORS is restricted to the development origins, and in production Flask serves the built app from the same origin.")

    add_bullet_p(doc, "4. Defects Found by Testing:", "Automated and manual testing exposed several defects that were fixed: log lines containing characters such as \"·\" crashed image requests on Windows because the console used the cp1252 encoding (logs are now written as UTF-8 and can never break a request); Cloudflare's FLUX endpoint rejected a seed parameter, so every request silently fell back to the weak engine; Chart.js charts collapsed inside CSS grid cells until they were given fixed-height containers; a full-screen image viewer was trapped inside a panel by its backdrop-filter until it was rendered through a React portal; and a login rate limit that counted successful logins locked out legitimate users during testing, so only failed attempts are now counted.")

    add_heading_2(doc, "8.2 Integration Challenges")
    add_body_p(doc, "Integrating disparate cloud APIs, database drivers, and frontend dependencies presented key integration hurdles:")

    add_bullet_p(doc, "API Quotas and Rate Limiting:", "During testing the preferred Gemini models frequently answered 503 (high demand), some older model names returned 404, every Gemini image model returned 429 with a free-tier limit of zero, Hugging Face returned 402 (no credits) and Pollinations allows one image per 45 seconds. The system therefore streams from six models with automatic skipping of failing ones, queues Pollinations requests instead of failing them, and always tells the user which engine produced a result.")
    add_bullet_p(doc, "Multi-Threading SQLite Database Locking:", "Under simultaneous browser requests, SQLite can trigger database locked errors if multiple threads attempt concurrent writes. This was resolved by configuring SQLAlchemy with connect_args={'check_same_thread': False} and scoping all database sessions to isolated try-finally blocks.")

    add_heading_2(doc, "8.3 Current Limitations")
    add_body_p(doc, "While Adspire AI achieves its core objectives effectively, certain operational boundaries define its current state:")

    add_bullet_p(doc, "Lack of Direct Programmatic Ad Spend Execution:", "The current implementation simulates budget allocations and generates ad creative, but does not execute direct programmatic bidding via Meta Marketing API or Google Ads API. Marketers must manually copy generated copy into ad managers.")
    add_bullet_p(doc, "Single Database Node Architecture:", "The best free AI engine, FLUX on Cloudflare Workers AI, has a daily allowance of 10,000 neurons (roughly a few dozen images) that resets at 00:00 UTC; after that the system falls back to the weaker Pollinations tier (768 px, watermark). AI images print the brand name as text but do not reproduce official logo artwork, and may contain small invented words elsewhere. Real-photo coverage depends on openly licensed libraries, and some Creative Commons photos are non-commercial: the interface labels them, but they must not be used in paid advertisements.")
    add_bullet_p(doc, "Static Industry Benchmarks:", "The predictive ROAS simulator relies on curated benchmark matrices rather than live auction API data streams, meaning seasonal bidding spikes (e.g., Black Friday) are not automatically ingested in real time.")

    add_page_break(doc)

    # =============================================================
    # CHAPTER 9: CONCLUSION AND FUTURE SCOPE
    # =============================================================
    add_heading_1(doc, "CHAPTER 9: CONCLUSION AND FUTURE SCOPE")

    add_heading_2(doc, "9.1 Conclusion")
    add_body_p(doc, "The major project entitled \"Adspire AI – AI Marketing Campaign Generator\" has successfully designed, implemented, and validated an autonomous, full-stack marketing intelligence platform. Developed as a final-year B.Tech Computer Science Engineering initiative at Sangam University, Bhilwara, the system addresses the fragmentation, excessive cost, and creative fatigue inherent in traditional digital marketing workflows.")

    add_body_p(doc, "By combining Google Gemini for copywriting and image verification with licensed real photographs and AI image generation, Adspire AI compresses complex marketing formulation workflows from days into one to two minutes. The platform produces complete, cohesive marketing deliverables—from target buyer psychographics and objection-busting frameworks to multi-angle A/B ad copy, platform-specific social captions, viral short-form video scripts, email newsletters, and 7-day distribution calendars.")

    add_body_p(doc, "Furthermore, the inclusion of an empirical predictive ROAS budgeting engine, authentic interactive social media mockups (Instagram, TikTok, LinkedIn, Google SERP), and an embedded relational persistence tier establishes Adspire AI as a comprehensive, production-ready solution. The system is verified by automated unit, live API and real-browser tests, all of which pass, and it supports multiple users with an administrator who controls features and monitors real usage.")

    add_heading_2(doc, "9.2 Future Enhancements")
    add_body_p(doc, "The modular architecture of Adspire AI establishes a strong foundation for future technological enhancements:")

    add_bullet_p(doc, "1. Direct Programmatic Ad API Publishing:", "Integrate direct OAuth2 connections to the Meta Marketing API, Google Ads API, and TikTok for Business API, enabling marketers to publish approved campaigns directly to live ad auctions with a single click.")
    add_bullet_p(doc, "2. Closed-Loop Machine Learning Attribution:", "Implement webhook listeners that ingest real-time conversion pixel data from live campaigns, allowing the system to train custom reinforcement learning models that optimize future ad copy based on actual conversion performance.")
    add_bullet_p(doc, "3. Autonomous Video Ad Generation:", "Expand the short-form video script generator into a full video synthesis pipeline by integrating text-to-speech (TTS) voiceover engines (e.g., ElevenLabs) and generative video diffusion models (e.g., Runway, Pika) to output fully assembled MP4 video ads.")
    add_bullet_p(doc, "4. Multi-Tenant Distributed Architecture:", "Building on the existing accounts, roles and PostgreSQL support, add shared team workspaces, approval workflows for campaigns, Redis-backed rate limiting for multiple server instances and single sign-on.")

    add_heading_2(doc, "9.3 Scope for Long-Term Improvement")
    add_body_p(doc, "In the long term, Adspire AI can evolve into an entirely autonomous Marketing AI Agent capable of conducting continuous market intelligence surveillance. By crawling competitor social feeds, monitoring trending hashtags, and analyzing real-time consumer sentiment, the system could autonomously suggest proactive campaign pivots and dynamically reallocate media budgets to maximize commercial growth.")

    add_page_break(doc)

    # =============================================================
    # REFERENCES
    # =============================================================
    add_heading_1(doc, "REFERENCES")

    refs = [
        "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). Attention is all you need. Advances in Neural Information Processing Systems (NeurIPS), 30, 5998–6008.",
        "Rombach, R., Blattmann, A., Lorenz, D., Esser, P., & Ommer, B. (2022). High-resolution image synthesis with latent diffusion models. Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 10684–10695.",
        "Brown, T., Mann, B., Ryder, N., Subbiah, M., Kaplan, J. D., Dhariwal, P., ... & Amodei, D. (2020). Language models are few-shot learners. Advances in Neural Information Processing Systems (NeurIPS), 33, 1877–1901.",
        "Google DeepMind. (2024). Gemini: A family of highly capable multimodal models. Google Research Technical Report.",
        "Black Forest Labs. (2024). FLUX.1: Open-source rectified flow transformers for high-resolution image synthesis. Technical Report.",
        "Chaffey, D., & Ellis-Chadwick, F. (2019). Digital Marketing: Strategy, Implementation and Practice (7th ed.). Pearson Education.",
        "Kotler, P., Kartajaya, H., & Setiawan, I. (2021). Marketing 5.0: Technology for Humanity. John Wiley & Sons.",
        "Davenport, T., Guha, A., Grewal, D., & Bressgott, T. (2020). How artificial intelligence will change the future of marketing. Journal of the Academy of Marketing Science, 48(1), 24–42.",
        "Huang, M. H., & Rust, R. T. (2021). A strategic framework for artificial intelligence in marketing. Journal of the Academy of Marketing Science, 49(1), 30–50.",
        "Flask Documentation. (2024). Flask: A lightweight WSGI web application framework. Pallets Projects. https://flask.palletsprojects.com/",
        "React Documentation. (2024). React: A JavaScript library for building user interfaces. Meta Platforms. https://react.dev/",
        "SQLAlchemy Authors. (2024). SQLAlchemy: The Database Toolkit for Python. https://www.sqlalchemy.org/",
        "Vite Documentation. (2024). Next Generation Frontend Tooling. https://vitejs.dev/",
        "Tailwind Labs. (2024). Tailwind CSS: Rapidly build modern websites without ever leaving your HTML. https://tailwindcss.com/",
        "Google. (2026). Gemini API documentation: text generation, streaming, image understanding and image generation. https://ai.google.dev/gemini-api/docs",
        "WHATWG. (2026). HTML Living Standard – Server-sent events. https://html.spec.whatwg.org/multipage/server-sent-events.html",
        "Microsoft. (2026). Playwright: Reliable end-to-end testing for modern web apps. https://playwright.dev/",
        "Openverse. (2026). Openverse API: openly licensed images. https://api.openverse.org/",
        "Creative Commons. (2026). About CC Licenses. https://creativecommons.org/about/cclicenses/",
        "OWASP Foundation. (2026). Authentication Cheat Sheet and Password Storage Cheat Sheet. https://cheatsheetseries.owasp.org/"
    ]

    for i, ref in enumerate(refs, 1):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.3
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4)
        r = p.add_run(f"[{i}] {ref}")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.font.color.rgb = docx.shared.RGBColor(0x21, 0x25, 0x29)
