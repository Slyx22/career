-- Career Readiness Analyzer - initial schema
-- Mirrors the shape used by python-engine/app/db/local_store.py (SQLite)
-- for local development, so swapping to Supabase is a drop-in change
-- behind the Repository interface (python-engine/app/db/interface.py).
--
-- This migration is NOT applied automatically. Run it against your own
-- Supabase project (via the SQL editor or `supabase db push`) once you
-- are ready to launch.

create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------
-- careers
-- ---------------------------------------------------------------------
create table if not exists careers (
    id          uuid primary key default gen_random_uuid(),
    name        text not null,
    slug        text not null unique,
    description text,
    created_at  timestamptz not null default now()
);

-- ---------------------------------------------------------------------
-- skills (canonical taxonomy - mirrors app/nlp/taxonomy.py)
-- ---------------------------------------------------------------------
create table if not exists skills (
    id         uuid primary key default gen_random_uuid(),
    name       text not null,
    slug       text not null unique,
    category   text not null,
    aliases    text[] not null default '{}',
    created_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------
-- career_skills (career model weights - mirrors app/scoring/career_model.py)
-- ---------------------------------------------------------------------
create table if not exists career_skills (
    career_id         uuid not null references careers(id) on delete cascade,
    skill_id          uuid not null references skills(id) on delete cascade,
    market_frequency  numeric(4,3) not null check (market_frequency between 0 and 1),
    market_importance numeric(4,3) not null check (market_importance between 0 and 1),
    -- Phase 1 values are seeded benchmark estimates, not a verified,
    -- collected job-market dataset. Flag them explicitly so the
    -- application/UI can label them accordingly (see build spec section 15).
    is_benchmark_data boolean not null default true,
    primary key (career_id, skill_id)
);

-- ---------------------------------------------------------------------
-- analyses
-- ---------------------------------------------------------------------
create table if not exists analyses (
    id          uuid primary key default gen_random_uuid(),
    -- Authoritative identity for the analysis/certificate. Deliberately
    -- NOT taken from the CV - always the values the user typed in.
    first_name  text not null,
    surname     text not null,
    career_id   uuid not null references careers(id),
    score       integer not null check (score between 0 and 100),
    -- clerk_user_id is nullable: analysis does not require authentication
    -- (build spec section 24). Identity here is Clerk's user id (a
    -- string like "user_2abc...", not a Supabase Auth uuid) since this
    -- app uses Clerk, not Supabase Auth, for accounts - see the
    -- README's "Integrating Clerk" section.
    clerk_user_id text,
    created_at  timestamptz not null default now()
);

create index if not exists idx_analyses_clerk_user_id on analyses (clerk_user_id);

-- ---------------------------------------------------------------------
-- analysis_skills (per-skill scoring detail, for the skill breakdown UI)
-- ---------------------------------------------------------------------
create table if not exists analysis_skills (
    analysis_id     uuid not null references analyses(id) on delete cascade,
    skill_id        uuid not null references skills(id) on delete cascade,
    present         boolean not null default false,
    evidence_score  numeric(4,3) not null default 0,
    depth_score     numeric(4,3) not null default 0,
    recency_score   numeric(4,3) not null default 0,
    relevance_score numeric(4,3) not null default 0,
    final_score     numeric(4,3) not null default 0,
    primary key (analysis_id, skill_id)
);

-- ---------------------------------------------------------------------
-- certificates
-- ---------------------------------------------------------------------
create table if not exists certificates (
    id             uuid primary key default gen_random_uuid(),
    certificate_id text not null unique,  -- public-facing id, e.g. CR-7F92A1C4
    analysis_id    uuid not null references analyses(id),
    first_name     text not null,
    surname        text not null,
    career         text not null,
    score          integer not null check (score between 0 and 100),
    -- Certificate generation requires a signed-in (free) account once
    -- Clerk is connected - see build spec change: "certificates require
    -- sign-up, free of charge". clerk_user_id is the Clerk user id of
    -- whoever generated this certificate. It's still nullable here so
    -- local development without Clerk configured keeps working (see
    -- frontend/app/api/certificate/route.ts for the enforcement logic).
    clerk_user_id  text,
    issued_at      timestamptz not null default now()
);

create index if not exists idx_certificates_certificate_id on certificates (certificate_id);
create index if not exists idx_certificates_clerk_user_id on certificates (clerk_user_id);
create index if not exists idx_analyses_created_at on analyses (created_at desc);
