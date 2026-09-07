# Career Readiness Analyzer — Phase 1

Upload a CV, pick a target career, and get an explainable Career Readiness
Score, a skill-gap breakdown, recommendations, and a shareable, publicly
verifiable Career Readiness Certificate.

This is a **complete, working, launch-ready Phase 1 codebase**. Nothing has
been deployed, and no production accounts (Netlify, Supabase, AI API) are
required to run it locally.

---

## 1. Architecture

```
                         USER
                           |
                           v
                  +----------------+
                  |    NEXT.JS     |   frontend/  (TypeScript, Tailwind)
                  |   FRONTEND     |
                  +-------+--------+
                          |  Next.js Route Handlers proxy requests to the
                          |  Python engine. PYTHON_API_URL never reaches
                          |  the browser.
                          v
                  +----------------+
                  |  API / SERVER  |   frontend/app/api/*
                  |     LAYER      |
                  +-------+--------+
                          |
                          v
                  +----------------+
                  | PYTHON /       |   python-engine/  (FastAPI)
                  | FASTAPI ENGINE |
                  +-------+--------+
                          |
             +------------+------------+
             |            |            |
             v            v            v
          CV Parser   Skill Engine   Scoring
        (extractors/)   (nlp/)     (scoring/)
                                      |
                                      v
                              Career Assessment
                                      |
                                      v
                             Certificate (services/)
```

- **Frontend (`frontend/`)** — Next.js 14 (App Router) + TypeScript +
  Tailwind. Renders the landing page, analysis form, results, certificate,
  and public verification page. Talks to the Python engine only through
  its own server-side Route Handlers (`frontend/app/api/*`), so
  `PYTHON_API_URL` and any future secrets never reach client JavaScript.
- **Python engine (`python-engine/`)** — FastAPI service that does all of
  the real analysis work: CV text extraction, evidence-aware skill
  extraction, explainable scoring, recommendations, and certificate
  (PDF) generation. **The Python scoring engine is the sole authority on
  the numeric score** — no LLM is involved in deciding it.
- **Storage** — a `Repository` interface
  (`python-engine/app/db/interface.py`) is implemented today by a
  zero-config SQLite store (`local_store.py`) so the whole app runs
  locally with no external services. `supabase/migrations/` contains
  Postgres-ready SQL that mirrors the same shape, so a
  `SupabaseStore` implementing the same interface is a drop-in swap
  later — no other code changes needed.

---

## 2. What's built (Phase 1 + Phase 2 accounts scaffold)

- Landing page with the required headline/CTA, no fake testimonials/stats.
- Analysis form: first name, surname, target career, CV upload (PDF or DOCX).
- **Four careers today** - ML Engineer, Data Scientist, Software Engineer,
  and English Teacher - each mapped to a real O*NET-SOC occupation code
  (see "Careers & O*NET sourcing" below). Adding another career is a
  matter of dropping a new JSON file into
  `python-engine/app/data/career_models/` - no code changes required.
- Python engine:
  - CV text extraction (PyMuPDF for PDF, python-docx for DOCX) with
    light section detection (experience / education / projects / skills).
  - A canonical, alias-aware skill taxonomy (`app/nlp/taxonomy.py`) - the
    frontend never hard-codes skill names. Covers both tech skills
    (Python, Docker, Kubernetes, ...) and education skills (lesson
    planning, classroom management, differentiated instruction, ...) to
    support non-tech careers like English Teacher.
  - Evidence-aware skill extraction (`app/nlp/skill_extractor.py`):
    presence, evidence strength, depth (mentioned vs. actually
    demonstrated - scoped to the sentence containing the mention, not a
    fixed character window, so evidence from one sentence can't leak
    into an unrelated neighbouring mention), and recency. Sentence
    splitting correctly handles bullet-list CVs (lines separated by a
    single newline, no punctuation - very common in real resumes), and
    explicit self-rated proficiency ("Python - Moderate", "SQL:
    Beginner") is detected and takes priority over a vaguer mention
    elsewhere in the same CV.
  - An explainable scoring engine (`app/scoring/scorer.py`) combining
    coverage × evidence × depth × recency × career importance/frequency
    into a 0–100 score, with a per-skill breakdown.
  - A deterministic recommendation engine (no AI API required).
  - Certificate creation with a secure random ID, SQL-ready storage, and
    a downloadable PDF (via ReportLab).
  - Public certificate verification endpoint that never exposes CV
    content.
- Next.js frontend wired to all of the above: results page with strengths
  / gaps / skill bars / recommendations, certificate page with
  print/download, and a `/verify/[certificateId]` page. The career
  dropdown is populated live from `/api/careers`, so it reflects
  whatever careers exist in the data directory.
- **Clerk authentication, wired in but optional** (see "Integrating
  Clerk" below) - a `/dashboard` route is protected and ready for
  Phase 2 "save your results" features, while the core CV → score →
  certificate flow works with zero setup and no account required.
- Supabase-ready SQL migrations (`supabase/migrations/`) with RLS
  policies, mirroring the local SQLite schema.
- Netlify-ready frontend config (`frontend/netlify.toml`) and a
  Python `Dockerfile` for independent deployment later — neither is
  used to deploy anything now.
- Automated tests: 29 passing tests covering scoring across a strong /
  beginner / transitioning / career-changer CV, messy real-world CV
  formatting, the sentence-scoping evidence fix, the O*NET data loader,
  and a full English Teacher CV run end-to-end.
- `.github/workflows/ci.yml` - GitHub Actions CI that runs the backend
  test suite and the frontend type-check/build on every push and PR.

### Explicitly out of scope for Phase 1

Per the build spec: job board, LinkedIn/GitHub integration, payments,
chatbot/AI career coach, social features, mobile app, additional careers
beyond ML Engineer, real-time market monitoring, resume builder,
community features, and a large analytics dashboard. These are future
phases.

---

## 3. Local setup

### Requirements

- Node.js 18.18+ (Next.js 14 requirement)
- Python 3.11+
- No Netlify, Supabase, or AI API account needed to run locally.

### 3.1 Start the Python engine

```bash
cd python-engine
python3 -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt
cp .env.example .env        # defaults already work locally
uvicorn app.main:app --reload --port 8000
```

Check it's up: `curl http://localhost:8000/health` → `{"status":"ok"}`.

The engine stores data in a local SQLite file
(`python-engine/local_dev.db`) by default — nothing external required.

### 3.2 Start the frontend

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env.local   # PYTHON_API_URL defaults to http://localhost:8000
npm run dev
```

Open http://localhost:3000.

### 3.3 How the frontend talks to Python

The browser never calls the Python API directly. Next.js Route Handlers
under `frontend/app/api/*` read `PYTHON_API_URL` (server-side only) and
proxy the request, so the Python engine's location is never exposed to
client JavaScript and can be changed freely (e.g. to a deployed URL)
without touching frontend code.

### 3.4 Run tests

```bash
cd python-engine
pytest
```

13 tests cover skill scoring across CV strength levels, validation
errors, extraction failures, and the full analyze → certificate → verify
API flow.

Frontend type-checking: `cd frontend && npx tsc --noEmit`.

### 3.5 Build for production

```bash
cd frontend && npm run build
```

---

## 4. Environment variables

See `frontend/.env.example` and `python-engine/.env.example` for the
authoritative, commented list. Summary:

**Frontend (`frontend/.env.local`)**
| Variable | Required locally? | Notes |
|---|---|---|
| `PYTHON_API_URL` | Yes | Points at your running Python engine. |
| `NEXT_PUBLIC_APP_URL` | No | Used to build certificate verify links. |
| `NEXT_PUBLIC_SUPABASE_URL` | No | Fill in when you connect Supabase. |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | No | Safe to expose to the browser. |
| `SUPABASE_SERVICE_ROLE_KEY` | No | **Server-side only. Never expose to the browser.** |
| `AI_API_KEY` | No | Optional; only used to rephrase recommendations. |

**Python engine (`python-engine/.env`)**
| Variable | Required locally? | Notes |
|---|---|---|
| `ALLOWED_ORIGINS` | No (has default) | CORS allow-list. |
| `STORAGE_BACKEND` | No (defaults to `local`) | `local` (SQLite) or `supabase` (implement first). |
| `LOCAL_DB_PATH` | No | SQLite file path for local dev. |
| `PUBLIC_VERIFY_URL_BASE` | No | Used on certificate PDFs; leave blank locally. |
| `AI_API_KEY` | No | Optional, never required to run the core product. |

No secrets are hard-coded anywhere in the codebase.

---

## 5. Careers & O*NET sourcing

Each career lives in its own file: `python-engine/app/data/career_models/<slug>.json`.

| Career | Slug | O*NET-SOC code | Match quality |
|---|---|---|---|
| ML Engineer | `ml-engineer` | 15-1221.00 (Computer and Information Research Scientists) | Closest available - O*NET has no distinct "ML Engineer" title yet |
| Data Scientist | `data-scientist` | 15-2051.00 (Data Scientists) | Exact match |
| Software Engineer | `software-engineer` | 15-1252.00 (Software Developers) | Exact match |
| English Teacher | `english-teacher` | 25-2031.00 (Secondary School Teachers) | "English Teacher" is O*NET's own listed sample job title for this broader occupation |

Every skill weight in these files carries a `source` tag so nothing is
silently presented as more verified than it is:

- `"onet_hot_technologies"` - a **real** percentage of employer job
  postings mentioning that skill for this occupation, pulled from
  O*NET's public Hot Technologies report (Lightcast job-postings data).
  This is genuine market data, not an estimate.
- `"onet_api"` - a real numeric Importance score (0-100) from the
  authenticated O*NET Web Services API, via `scripts/onet_sync.py`.
- `"onet_technology_list_only"` - the skill is confirmed relevant by
  O*NET's technology list, but no numeric score is available yet.
- `"benchmark_estimate"` - **not yet sourced from anywhere verified.**
  An initial estimate seeded by the product team. The API response
  labels these clearly (`onet_source` / `weight_source` fields) so the
  frontend never presents them as verified statistics.

### Adding another career

1. Find its O*NET-SOC code at https://www.onetonline.org (search by job title).
2. Either:
   - **Manual (quick, less precise):** copy an existing file in
     `app/data/career_models/`, update `slug`/`name`/`description`/`onet`,
     and hand-write skill weights (mark them `"benchmark_estimate"`
     honestly if you're guessing).
   - **Bulk database (recommended, real numbers, no signup):** download
     O*NET's free full database zip - no API credentials needed at all:
     1. Go to https://www.onetcenter.org/database.html#individual-files
     2. Under "Text Format", download the latest zip (e.g. `db_29_1_text.zip`).
     3. Unzip it somewhere, e.g. `~/Downloads/db_29_1_text/`.
     4. Run:
        ```bash
        cd python-engine
        python3 -m scripts.onet_bulk_import --db-dir ~/Downloads/db_29_1_text --list-occupations
        python3 -m scripts.onet_bulk_import \
          --db-dir ~/Downloads/db_29_1_text \
          --soc-code <code> --career-slug <slug> --career-name "..."
        ```
     This writes real, numeric Importance scores straight from the
     official database - no rate limits, no credentials, and you can run
     it once per career for as many careers as you want.
   - **Scripted API (slower, one career at a time, needs free signup):**
     get free O*NET Web Services credentials
     (https://services.onetcenter.org/developer/signup) and run:
     ```bash
     cd python-engine
     export ONET_USERNAME=... ONET_PASSWORD=...
     python3 -m scripts.onet_sync --soc-code <code> --career-slug <slug> --career-name "..."
     ```
3. Add any missing skills to `app/nlp/taxonomy.py` first if the career
   needs vocabulary that isn't covered yet (see the `Education` category
   added for English Teacher as an example of extending into a
   non-tech domain).
4. Restart the Python engine - `list_careers()` picks up new files
   automatically, and the frontend's career dropdown (`/api/careers`) reflects
   it immediately, no frontend code changes needed.

## 6. Integrating Clerk

Clerk (`@clerk/nextjs`) is already installed and wired into the code -
turning it on is two environment variables, not a code change.

1. Create a free account at https://dashboard.clerk.com and create an application.
2. Copy your **Publishable key** and **Secret key** from the Clerk dashboard.
3. Add them to `frontend/.env.local`:
   ```
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
   CLERK_SECRET_KEY=sk_test_...
   ```
4. Restart `npm run dev`. That's it:
   - `components/AuthProvider.tsx` now wraps the app in `ClerkProvider`.
   - The header shows a real Sign in button (`components/AuthSection.tsx`).
   - `middleware.ts` starts protecting `/dashboard` - visiting it while
     signed out redirects to Clerk's sign-in flow automatically.
   - `/dashboard` (`app/dashboard/page.tsx`) lists every certificate the
     signed-in user has generated, via `GET /api/certificates`
     (`app/api/certificates/route.ts`, which uses the caller's own
     verified Clerk session - never a client-supplied user id).
   - **Certificate generation requires a free account.** Analysis stays
     completely open with no sign-in; only clicking "Generate My
     Certificate" checks your Clerk session
     (`app/api/certificate/route.ts`) and prompts you to sign up/sign in
     first if needed (`components/GenerateCertificateButton.tsx`). Set
     `REQUIRE_ACCOUNT_FOR_CERTIFICATE=true` in the Python engine's `.env`
     too for a defense-in-depth check on that side as well.

Until you set the two env vars above, none of this activates: the app
builds, runs, and serves the full CV → score → certificate flow exactly
as if Clerk weren't installed at all (see `lib/clerk.ts`), with no
sign-up required anywhere.

**A note on secrets:** never paste your `CLERK_SECRET_KEY` (or any
secret key) into a chat tool, ticket, or anywhere outside your own
`.env.local` file (which is already git-ignored). If a secret key is
ever exposed somewhere it shouldn't be, roll it from the Clerk dashboard
- generating a new one immediately invalidates the old one.

## 7. Terms of Service & Privacy Policy

`app/terms/page.tsx` and `app/privacy/page.tsx` contain a drafted Terms
of Service and Privacy Policy, written to reflect what this specific
application actually collects and does (CV upload, free certificate
generation requiring a Clerk account, public certificate verification,
no ads, no data sale). **These are templates, not legal advice** - they
say so directly on the page. Before launching for real:

1. Replace every `[bracketed placeholder]` (company name, contact email, retention policy, age threshold, etc.).
2. Have a lawyer review both pages - particularly for South Africa's
   POPIA if your users are there, and any other jurisdiction (e.g. GDPR)
   your users are in.
3. Update Section 5 of the Privacy Policy once you've picked and connected
   a real database provider (Supabase or otherwise).

Both pages are linked from the site footer.

## 8. Pushing this repository to GitHub

This project is already a git repository with an initial commit. To push
it to your own GitHub account:

```bash
# 1. Create a new, empty repository on github.com (don't initialize it
#    with a README/license - this repo already has one).

# 2. From the project root:
git remote add origin https://github.com/<your-username>/<your-repo>.git
git branch -M main
git push -u origin main
```

Once pushed, `.github/workflows/ci.yml` runs automatically on every push
and pull request: it installs the Python engine's dependencies and runs
the full test suite, and separately type-checks and builds the frontend
(with no Clerk/Supabase/AI keys configured, proving the app builds
cleanly without them). No secrets or deployment credentials are needed
for CI to pass - it only tests and builds, it doesn't deploy anything.

Connecting this GitHub repo to Netlify (step 10 below) is what actually
deploys the frontend - pushing to GitHub by itself does not deploy or
launch anything.

## 9. Configuring Supabase later

1. Create a Supabase project.
2. Run the SQL in `supabase/migrations/` in order (via the SQL editor or
   `supabase db push`) — this creates the schema, RLS policies, and seeds
   the ML Engineer taxonomy/career model.
3. Implement `python-engine/app/db/supabase_store.py` against the
   `Repository` interface in `app/db/interface.py` (same method shapes as
   `local_store.py`), then set `STORAGE_BACKEND=supabase` and provide
   `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` to the Python engine.
4. Set `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_ANON_KEY` on the
   frontend only once you build the optional "create an account to save
   your results" feature — the core flow doesn't require it.

## 10. Configuring Netlify later

1. Connect this repository to a new Netlify site.
2. Netlify will read `frontend/netlify.toml` (base directory, build
   command, and the `@netlify/plugin-nextjs` plugin) automatically.
3. Set `PYTHON_API_URL` in the Netlify site's environment variables to
   point at wherever you deploy the Python engine (step 11).
4. Trigger a deploy from Netlify. Nothing in this repo deploys itself.

## 11. Deploying the Python engine later

`python-engine/Dockerfile` builds a container exposing port 8000. Deploy
it to any container host you like (Fly.io, Render, Cloud Run, ECS, etc.).
Set `ALLOWED_ORIGINS` to your deployed frontend's URL and
`PUBLIC_VERIFY_URL_BASE` to your public domain once you have one.

## 12. Optional AI API

Phase 1 works fully without any AI API key. If you later want more
natural-language recommendations, wire an AI API call into
`app/recommendations/engine.py` that takes the deterministic
recommendations as input and rephrases them — the ranked list of gaps and
the score must keep coming from the Python engine, never the LLM.

---

## 13. Repository layout

```
career-readiness-analyzer/
  frontend/                Next.js app (TypeScript, Tailwind)
    app/                   Pages + Route Handlers (proxy to Python engine)
    components/            Reusable UI components
    lib/                   Config + typed API helpers (server-only)
    netlify.toml           Netlify build config (not deployed by default)
  python-engine/           FastAPI service - the real analysis engine
    app/
      api/                 FastAPI routes
      extractors/          PDF/DOCX text extraction
      nlp/                 Skill taxonomy + evidence-aware extraction
      scoring/              Career model + explainable scoring
      recommendations/     Deterministic recommendation engine
      services/            Orchestration (analysis, certificates)
      db/                  Repository interface + local SQLite store
      models/              Pydantic schemas
    tests/                 Pytest suite
    Dockerfile             Deployment-readiness only, not built/deployed
  supabase/
    migrations/            Postgres schema, RLS policies, seed data
  README.md                You are here
```

---

## 14. Launch checklist (when you're ready)

- [ ] Create Supabase project, run `supabase/migrations/*.sql`.
- [ ] Implement `app/db/supabase_store.py`, set `STORAGE_BACKEND=supabase`.
- [ ] Deploy `python-engine` (Docker) somewhere with a stable URL.
- [ ] Set `PUBLIC_VERIFY_URL_BASE` / `ALLOWED_ORIGINS` on the deployed engine.
- [ ] Push this repo to GitHub (see section 8), connect it to Netlify; set `PYTHON_API_URL` there.
- [ ] Point your domain at Netlify.
- [ ] Set your Clerk env vars (see section 6) - certificates require an account, so this is not optional once you're live.
- [ ] Set `REQUIRE_ACCOUNT_FOR_CERTIFICATE=true` on the deployed Python engine.
- [ ] Fill in the `[bracketed placeholders]` in `app/terms/page.tsx` and `app/privacy/page.tsx`, and have a lawyer review both (see section 7).
- [ ] (Optional) Configure an AI API key for nicer recommendation phrasing.
- [ ] (Optional) Get free O*NET Web Services credentials and run `scripts/onet_sync.py`, or download the bulk database and run `scripts/onet_bulk_import.py` (see section 5), for each career to replace remaining benchmark estimates with real numeric scores.

This project does not perform any of the above automatically — every step
here is something you trigger yourself when ready.
