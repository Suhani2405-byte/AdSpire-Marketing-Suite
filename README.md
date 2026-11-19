# Adspire — AI Marketing Campaign Generator

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-brightgreen?style=for-the-badge&logo=render)](https://adspire-marketing-suite-1.onrender.com/)
![React 19](https://img.shields.io/badge/Frontend-React%2019-61DAFB?style=for-the-badge&logo=react)
![Flask](https://img.shields.io/badge/Backend-Flask-3776AB?style=for-the-badge&logo=python)

Generate a complete multi-channel marketing campaign from a product description: buyer persona,
ad copy with A/B variants, social posts, a video script, an email, a 7-day content calendar,
an AI-generated product visual, and a budget/ROAS simulation.

**Live:** https://adspire-marketing-suite-1.onrender.com/

## Features

| Area | What it does |
|---|---|
| **Accounts** | Register / log in (hashed passwords, signed 7-day tokens). Each user's campaigns and brands are private. The first account and any email in `ADMIN_EMAILS` get the admin role. |
| **Campaign Studio** | Google Gemini writes the campaign as structured JSON and **streams it live** to the UI. Uses product, audience, platform, goal, industry and tone. Falls back across several Gemini models; if all are down it uses a template and **tells the user**. |
| **Brand profiles** | Save product/brand presets and load them into the form in one click. |
| **Ad mockups** | Instagram, TikTok, LinkedIn and Google Search previews using the generated copy and image. |
| **Visual Studio** | Text-to-image from **your exact prompt** with style presets and 1:1 / 16:9 / 9:16. Provider chain: Gemini image → Hugging Face FLUX.1 → Pollinations FLUX. Shows which engine made each image. Every click is a new variation. |
| **Budget planner** | Benchmark-based CPC / CTR / conversion simulation across 6 channels, 5 industries and 5 goals, with a spend chart. |
| **Library** | Every campaign is saved with its image; search, reopen, delete. |
| **Export** | PDF (print), Markdown, JSON. |
| **Admin dashboard** | Real usage metrics from the database: users, campaigns, images, success rate, generation times, provider usage, activity log. |

## Tech stack

- **Frontend:** React 19, Vite, Chart.js, lucide-react (`frontend/src`, split into `components/`, `state/`, `utils/`)
- **Backend:** Flask 3, SQLAlchemy 2 (SQLite locally, PostgreSQL in production), gunicorn
- **AI:** Google Gemini (`google-genai`) for text and images, Hugging Face Inference (FLUX.1-schnell), Pollinations
- **Tests:** pytest (`backend/tests`), all AI calls mocked

```
backend/
  app.py                 Flask app, serves frontend/dist in production
  routes/                auth, campaigns (+SSE stream), image, budget, brands, admin
  services/              gemini_service, image_service, database_service, auth_service, rate_limit
  tests/                 pytest suite
frontend/src/
  App.jsx                auth gate + navigation shell
  api.js                 axios client + streaming helper
  state/AppState.jsx     shared state (campaign, visuals, library, brands)
  components/            CampaignStudio, CampaignOutput, AdMockups, VisualStudio, BudgetPlanner, Library, AdminDashboard, LoginPage
  utils/                 exporters (PDF/MD/JSON), chart setup
```

## Run locally (Windows)

```bash
# 1. Backend
cd backend
py -3.11 -m venv venv            # or py -3.13
venv\Scripts\pip install -r requirements.txt
copy .env.example .env           # then put your GEMINI_API_KEY in .env

# 2. Frontend
cd ..\frontend
npm install
npm run build

# 3. Start (serves the built UI + API on http://127.0.0.1:5000)
cd ..
run.bat                          # or: cd backend && venv\Scripts\python app.py
```

For UI development with hot reload: run the backend, then `cd frontend && npm run dev` and open
http://localhost:5173 (Vite proxies `/api` to port 5000).

Open the app and **create an account**: the first account becomes the admin.

### Demo data

```bash
cd backend
venv\Scripts\python seed_demo_data.py                        # 10 demo users + 60 campaigns (60 different products) + activity
venv\Scripts\python seed_demo_data.py --owner you@mail.com   # put the demo campaigns in YOUR library
venv\Scripts\python seed_demo_data.py --clear                # remove all demo data
```

Demo logins: `aarav@demo.adspire.app` (also priya, rohan, ananya, kabir, sara, vikram, meera, arjun, isha)
with password `DemoPass123`. Demo accounts are never admins; the first real person to register is.

### Admin account & panel

```bash
cd backend
venv\Scripts\python create_admin.py --email admin@adspire.app --password "Admin@12345" --name "Adspire Admin"
```

The **Admin Panel** tab lets an admin:
- **Overview** – real usage KPIs, 7-day chart, platform split, AI provider status
- **Users** – create accounts, change role (admin/marketer), disable/enable logins, reset passwords,
  delete a user with all their data (you can't lock out yourself or remove the last admin)
- **Settings & Features** – switch campaign generation, image generation, budget planner and sign-ups
  on/off for everyone, set per-user hourly limits, publish an announcement banner
- **Activity Log** – every generation, login and admin action, filterable

The admin's **All Campaigns** tab shows every user's campaigns with an owner filter, and can open or delete any of them.
Change the admin password after the first login (Admin Panel → Users → key icon).

### Tests

```bash
cd backend
venv\Scripts\pip install -r requirements-dev.txt
venv\Scripts\python -m pytest tests -q
```

## Deploy on Render (frontend + backend in one service)

1. **Database (needed so data survives deploys).** Render's free disk is wiped on every deploy/restart,
   so SQLite data would disappear. Create a free Postgres database at [neon.tech](https://neon.tech)
   (or Supabase) and copy its connection string.
2. **Build the UI** and commit it: `cd frontend && npm run build`, then commit `frontend/dist`.
3. Push to GitHub. In Render: **New → Blueprint** → select the repo (uses `render.yaml`).
   For an existing service, set the same build/start commands as in `render.yaml`.
4. In the service's **Environment** tab set:
   - `GEMINI_API_KEY` – required for real campaigns
   - `DATABASE_URL` – the Neon/Supabase URL
   - `ADMIN_EMAILS` – your email, so you get the admin dashboard
   - `SECRET_KEY` – generated automatically by the blueprint (keep it stable or users get logged out)
   - optional: `HF_TOKEN`, `POLLINATIONS_API_KEY`
5. Deploy. Health check: `/api/health`.

Notes: the free Render instance sleeps after 15 minutes idle (first request takes ~1 minute).

## Image quality

Image quality depends on which provider is available:

| Provider | Needs | Quality |
|---|---|---|
| Gemini image models | `GEMINI_API_KEY` **with billing enabled** (free tier has no image quota) | Best, follows prompts closely |
| Hugging Face FLUX.1-schnell | `HF_TOKEN` with inference credits | Good, 1024px+ |
| Pollinations FLUX (free) | nothing | 768px, watermark, ~1 image / 45 s (requests queue automatically) |
| Pollinations FLUX (keyed) | `POLLINATIONS_API_KEY` | Higher limits, no watermark |

The app never substitutes an unrelated stock photo: if no provider can generate, it shows the reason.

## Known limitations

- Budget figures are simulations from industry benchmark averages, not live ad-platform data.
- Rate limiting is in-memory (per server process).
