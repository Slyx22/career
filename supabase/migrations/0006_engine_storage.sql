-- Permanent storage for the Python engine's analyses and certificates.
--
-- Run once: Supabase Dashboard -> SQL Editor -> New query -> paste -> Run.
-- Safe to run again.
--
-- These tables match what the engine saves (app/db/supabase_store.py).
-- RLS is on with NO policies: the browser (anon key) can't read or write
-- them at all. Only the engine, using the service role key on the server,
-- can. Certificate verification still works because it goes through the
-- engine, one certificate ID at a time.

create table if not exists engine_analyses (
    id            text primary key,
    first_name    text not null,
    surname       text not null,
    career        text not null,
    score         integer not null check (score between 0 and 100),
    payload       jsonb not null,
    clerk_user_id text,
    created_at    timestamptz not null default now()
);

create table if not exists engine_certificates (
    certificate_id text primary key,
    analysis_id    text not null references engine_analyses(id),
    first_name     text not null,
    surname        text not null,
    career         text not null,
    score          integer not null check (score between 0 and 100),
    clerk_user_id  text,
    issued_at      timestamptz not null default now()
);

create index if not exists idx_engine_certificates_user on engine_certificates (clerk_user_id, issued_at desc);
create index if not exists idx_engine_analyses_created on engine_analyses (created_at desc);

alter table engine_analyses enable row level security;
alter table engine_certificates enable row level security;
