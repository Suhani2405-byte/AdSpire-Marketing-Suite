"""
Render the report's design diagrams (Chapter 4/5) from Mermaid source to PNG.

    python build_report/diagrams.py        (needs: pip install playwright; uses installed Microsoft Edge)

Output: report_assets/fig_4_*.png at 2x resolution.
"""
import os
import sys

from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops


def trim(path, pad=24):
    """Crop the empty white margins Mermaid leaves around a diagram."""
    img = Image.open(path).convert("RGB")
    bg = Image.new("RGB", img.size, (255, 255, 255))
    box = ImageChops.difference(img, bg).getbbox()
    if box:
        l, t, r, b = box
        img.crop((max(l - pad, 0), max(t - pad, 0), min(r + pad, img.width), min(b + pad, img.height))).save(path)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "report_assets")

THEME = """%%{init: {"theme": "base", "themeVariables": {
  "fontFamily": "Segoe UI, Arial, sans-serif", "fontSize": "19px",
  "primaryColor": "#EAF2FB", "primaryBorderColor": "#2874A6", "primaryTextColor": "#1B2631",
  "lineColor": "#34495E", "secondaryColor": "#FEF5E7", "tertiaryColor": "#F4F6F7",
  "clusterBkg": "#FBFCFC", "clusterBorder": "#AAB7B8", "edgeLabelBackground": "#FFFFFF"}}}%%
"""

STYLES = """
classDef ui fill:#EAF2FB,stroke:#2874A6,stroke-width:2px,color:#1B2631
classDef api fill:#FEF5E7,stroke:#D68910,stroke-width:2px,color:#1B2631
classDef svc fill:#FDF2E9,stroke:#CA6F1E,stroke-width:1.5px,color:#1B2631
classDef data fill:#E9F7EF,stroke:#1E8449,stroke-width:2px,color:#1B2631
classDef ext fill:#F4ECF7,stroke:#7D3C98,stroke-width:2px,color:#1B2631
classDef actor fill:#FFFFFF,stroke:#1B4F72,stroke-width:2px,color:#0F294A
classDef bad fill:#FDEDEC,stroke:#C0392B,stroke-width:2px,color:#1B2631
classDef good fill:#E9F7EF,stroke:#1E8449,stroke-width:2px,color:#1B2631
"""

DIAGRAMS = {
    "fig_4_1_system_architecture": """
flowchart TB
  subgraph P["PRESENTATION — React 19 SPA"]
    direction LR
    P1["LoginPage · CampaignStudio<br/>Output · AdMockups"]:::ui
    P2["VisualStudio · BudgetPlanner<br/>Library · AdminDashboard"]:::ui
    P3["AppState context · api.js<br/>Axios · SSE reader · token"]:::ui
  end
  subgraph F["APPLICATION — Flask 3 (gunicorn)"]
    direction LR
    F1["Blueprints<br/>auth · campaigns · image · budget<br/>brands · admin · settings"]:::api
    F2["Middleware<br/>login / admin required<br/>feature switches · rate limits"]:::api
  end
  subgraph S["SERVICES"]
    direction LR
    S1["gemini_service<br/>streaming · fail-over"]:::svc
    S2["image_service + photo_service<br/>analyse · generate · verify"]:::svc
    S3["database_service<br/>auth_service"]:::svc
  end
  subgraph X["DATA & EXTERNAL SERVICES"]
    direction LR
    X1[("SQLite / PostgreSQL")]:::data
    X2["Google Gemini<br/>text · vision · image"]:::ext
    X3["Cloudflare FLUX · HF FLUX<br/>Pollinations<br/>Unsplash · Pixabay · Pexels<br/>Openverse · Wikimedia"]:::ext
  end
  P -- "HTTPS JSON /api · Server-Sent Events" --> F
  F --> S
  S1 --> X2
  S2 --> X2
  S2 --> X3
  S3 --> X1
""",
    "fig_4_2_dfd_level1": """
flowchart LR
  U(["Marketer"]):::actor
  A(["Administrator"]):::actor
  P1(("1.0<br/>Authenticate")):::api
  P2(("2.0<br/>Generate<br/>Campaign")):::api
  P3(("3.0<br/>Create<br/>Visual")):::api
  P4(("4.0<br/>Simulate<br/>Budget")):::api
  P5(("5.0<br/>Administer<br/>Platform")):::api
  D1[("D1 users")]:::data
  D2[("D2 campaigns")]:::data
  D3[("D3 brands")]:::data
  D4[("D4 activity_logs")]:::data
  D5[("D5 settings")]:::data
  G["Gemini API"]:::ext
  I["Image engines /<br/>photo libraries"]:::ext
  U -- "credentials" --> P1
  P1 -- "verify hash" --> D1
  P1 -- "signed token" --> U
  U -- "product brief" --> P2
  P2 -- "structured prompt" --> G
  G -- "JSON stream" --> P2
  P2 -- "campaign" --> D2
  P2 -- "live text + result" --> U
  U -- "brand profile" --> D3
  U -- "prompt, style, mode" --> P3
  P3 <-- "image / photo + QA" --> I
  P3 -- "image_url" --> D2
  U -- "budget, goal, days" --> P4
  P4 -- "ROAS projection" --> U
  A -- "user + feature changes" --> P5
  P5 --> D1
  P5 --> D5
  P2 & P3 -- "events" --> D4
  D4 -- "metrics" --> P5
""",
    "fig_4_3_use_case": """
flowchart LR
  M(["👤 Marketer"]):::actor
  A(["👤 Administrator"]):::actor
  GE(["⚙ Gemini AI"]):::ext
  IE(["⚙ Image engines &<br/>photo libraries"]):::ext
  subgraph SYS["Adspire AI System"]
    direction TB
    UC1(["UC1 Register / Log in"]):::ui
    UC2(["UC2 Manage brand profiles"]):::ui
    UC3(["UC3 Generate campaign (live stream)"]):::ui
    UC4(["UC4 Create product visual"]):::ui
    UC5(["UC5 Preview ad mockups"]):::ui
    UC6(["UC6 Simulate budget & ROAS"]):::ui
    UC7(["UC7 Library: search · open · delete"]):::ui
    UC8(["UC8 Export PDF / Markdown / JSON"]):::ui
    UC9(["UC9 Manage users & roles"]):::api
    UC10(["UC10 Feature switches & limits"]):::api
    UC11(["UC11 View usage & activity"]):::api
  end
  M --- UC1 & UC2 & UC3 & UC4 & UC5 & UC6 & UC7 & UC8
  A --- UC9 & UC10 & UC11
  A -. "inherits all marketer use cases" .-> M
  UC3 --- GE
  UC4 --- IE
  UC4 --- GE
""",
    "fig_4_4_activity_diagram": """
flowchart LR
  subgraph G1["Campaign"]
    direction TB
    S((Start)):::actor --> L{"Logged in?"}:::api
    L -- No --> LG["Log in / register"]:::ui --> F
    L -- Yes --> F["Fill brief or<br/>load brand profile"]:::ui
    F --> V{"Required fields,<br/>feature on, under limit?"}:::api
    V -- No --> E1["Show message"]:::bad
    V -- Yes --> GEN["Stream campaign<br/>from Gemini"]:::svc
    GEN --> J{"Valid JSON?"}:::api
    J -- No --> NX["Next model /<br/>template + warning"]:::svc
    J -- Yes --> SAVE["Save campaign"]:::data
    NX --> SAVE
  end
  subgraph G2["Visual & review"]
    direction TB
    IMG["Real photo or<br/>AI image"]:::svc --> Q{"Gemini vision:<br/>right product?"}:::api
    Q -- No --> R["Retry / next photo"]:::svc --> IMG
    Q -- Yes --> ATT["Attach to campaign"]:::data
    ATT --> OUT["Tabs · mock-ups · export"]:::ui --> E((End)):::actor
  end
  G1 -- "campaign saved" --> G2
""",
    "fig_4_5_er_diagram": """
erDiagram
  USERS ||--o{ CAMPAIGNS : creates
  USERS ||--o{ BRANDS : saves
  USERS ||--o{ ACTIVITY_LOGS : generates
  USERS {
    int id PK
    string name
    string email UK
    string password_hash
    string role "admin or marketer"
    bool is_active
    datetime created_at
  }
  CAMPAIGNS {
    int id PK
    int user_id FK
    string product_name
    string target_audience
    string platform
    string goal
    text campaign_content "JSON"
    text image_url "data URL or https"
    text image_thumb "small JPEG for cards"
    string source "model or template"
    datetime created_at
  }
  BRANDS {
    int id PK
    int user_id FK
    string name
    string industry
    string tone
    string audience
    text description
  }
  ACTIVITY_LOGS {
    int id PK
    int user_id FK
    string action
    string detail
    string provider
    float duration_ms
    datetime created_at
  }
  SETTINGS {
    string key PK
    text value "JSON"
  }
""",
    "fig_4_6_campaign_workflow": """
flowchart TB
  A["POST /api/campaigns/generate-stream"]:::api --> B["Checks: login · feature switch · hourly limit"]:::api
  B --> C["Build structured prompt<br/>product · audience · platform · goal · tone · industry"]:::svc
  C --> D["Next available Gemini model<br/>3.8-flash → 3.5-flash → 3-flash-preview<br/>→ flash-latest → 3.1-flash-lite → flash-lite"]:::ext
  D -- "503 / 429 / 404 / 60 s timeout:<br/>skip model for 2 min" --> D
  D -- "SSE chunks to browser" --> E["Parse JSON · check 11 sections"]:::svc
  E -- "invalid" --> D
  D -- "all models unavailable" --> T["Template campaign + visible warning"]:::bad
  E -- "valid" --> F["Save campaign + activity log"]:::data
  T --> F
  F --> G["'done' event → React renders tabs<br/>→ automatic product visual"]:::ui
""",
    "fig_4_7_image_workflow": """
flowchart TB
  A["Prompt + style + aspect + mode"]:::ui --> B["Gemini analyses prompt:<br/>product type · brand · search query ·<br/>brand-free visual prompt"]:::svc
  B --> M{"Mode"}:::api
  M -- "Real Photo, or Auto with a brand<br/>and no described scene" --> P["Search Pexels → Unsplash → Pixabay<br/>→ Openverse → Wikimedia"]:::ext
  P --> PV{"Gemini vision:<br/>right product & brand?<br/>ad score 1-10"}:::api
  PV -- "No: next candidate" --> P
  PV -- Yes --> PH["HD photo (≤2048 px)<br/>+ credit & licence"]:::good
  PV -- "none match (Auto)" --> AI
  M -- "AI, or a described scene" --> AI["Gemini image → Cloudflare FLUX<br/>→ HF FLUX → Pollinations<br/>(FLUX also asked for the brand logo)"]:::ext
  AI --> V{"Gemini vision:<br/>right product, no unwanted<br/>person, logo spelled right?"}:::api
  V -- "No (≤3 tries: new seed, simpler<br/>prompt; last try without logo)" --> AI
  V -- Yes --> OK["Verified AI image"]:::good
  V -- "still wrong" --> ER["Clear error —<br/>wrong image never shown"]:::bad
""",
}

HTML = """<!doctype html><html><head><meta charset="utf-8">
<style>body{margin:0;background:#fff;font-family:'Segoe UI',Arial,sans-serif} #d{display:inline-block;padding:24px} .mermaid, .mermaid *{font-family:'Segoe UI',Arial,sans-serif !important}</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script></head>
<body><div id="d"><div class="mermaid">__SRC__</div></div>
<script>mermaid.initialize({startOnLoad:false, securityLevel:"loose", flowchart:{htmlLabels:true, curve:"basis", padding:12, useMaxWidth:false}, er:{useMaxWidth:false}});
mermaid.run().then(()=>document.body.setAttribute("data-done","1")).catch(e=>{document.body.setAttribute("data-done","err:"+e)});</script>
</body></html>"""


def render(names=None):
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(device_scale_factor=2, viewport={"width": 1600, "height": 1200})
        for name, src in DIAGRAMS.items():
            if names and name not in names:
                continue
            body = THEME + src.strip() + ("\n" + STYLES if not src.strip().startswith("erDiagram") else "")
            page.set_content(HTML.replace("__SRC__", body))
            page.wait_for_function("document.body.getAttribute('data-done')", timeout=30000)
            status = page.evaluate("document.body.getAttribute('data-done')")
            if status != "1":
                raise RuntimeError(f"{name}: {status}")
            path = os.path.join(OUT, name + ".png")
            page.locator("#d").screenshot(path=path)
            trim(path)
            print("rendered", path, Image.open(path).size)
        browser.close()


if __name__ == "__main__":
    render(sys.argv[1:] or None)
