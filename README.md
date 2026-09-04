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

## 2. What's built (Phase 1 scope)

- Landing page with the required headline/CTA, no fake testimonials/stats.
- Analysis form: first name, surname, target career (ML Engineer),
  CV upload (PDF or DOCX).
- Python engine:
  - CV text extraction (PyMuPDF for PDF, python-docx for DOCX) with
    light section detection (experience / education / projects / skills).
  - A canonical, alias-aware skill taxonomy (`app/nlp/taxonomy.py`) — the
    frontend never hard-codes skill names.
  - Evidence-aware skill extraction (`app/nlp/skill_extractor.py`):
    presence, evidence strength, depth (mentioned vs. demonstrated), and
    recency (from years found near each mention), not just keyword
    matching.
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
  print/download, and a `/verify/[certificateId]` page.
- Supabase-ready SQL migrations (`supabase/migrations/`) with RLS
  policies, mirroring the local SQLite schema.
- Netlify-ready frontend config (`frontend/netlify.toml`) and a
  Python `Dockerfile` for independent deployment later — neither is
  used to deploy anything now.
- Automated tests for the Python engine (scoring across a strong /
  beginner / transitioning CV, extraction failures, validation errors,
  certificate creation/verification, and the full API flow).

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

## 5. Configuring Supabase later

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

## 6. Configuring Netlify later

1. Connect this repository to a new Netlify site.
2. Netlify will read `frontend/netlify.toml` (base directory, build
   command, and the `@netlify/plugin-nextjs` plugin) automatically.
3. Set `PYTHON_API_URL` in the Netlify site's environment variables to
   point at wherever you deploy the Python engine (step 7).
4. Trigger a deploy from Netlify. Nothing in this repo deploys itself.

## 7. Deploying the Python engine later

`python-engine/Dockerfile` builds a container exposing port 8000. Deploy
it to any container host you like (Fly.io, Render, Cloud Run, ECS, etc.).
Set `ALLOWED_ORIGINS` to your deployed frontend's URL and
`PUBLIC_VERIFY_URL_BASE` to your public domain once you have one.

## 8. Optional AI API

Phase 1 works fully without any AI API key. If you later want more
natural-language recommendations, wire an AI API call into
`app/recommendations/engine.py` that takes the deterministic
recommendations as input and rephrases them — the ranked list of gaps and
the score must keep coming from the Python engine, never the LLM.

---

## 9. Repository layout

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

## 10. Launch checklist (when you're ready)

- [ ] Create Supabase project, run `supabase/migrations/*.sql`.
- [ ] Implement `app/db/supabase_store.py`, set `STORAGE_BACKEND=supabase`.
- [ ] Deploy `python-engine` (Docker) somewhere with a stable URL.
- [ ] Set `PUBLIC_VERIFY_URL_BASE` / `ALLOWED_ORIGINS` on the deployed engine.
- [ ] Connect this repo to Netlify; set `PYTHON_API_URL` there.
- [ ] Point your domain at Netlify.
- [ ] (Optional) Configure an AI API key for nicer recommendation phrasing.

This project does not perform any of the above automatically — every step
here is something you trigger yourself when ready.
