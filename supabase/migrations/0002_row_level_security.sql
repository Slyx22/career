-- Row Level Security.
--
-- This app uses Clerk for authentication, not Supabase Auth, so there is
-- no Supabase `auth.uid()` to key off - Clerk's user id is stored as a
-- plain text column (clerk_user_id) instead. All reads/writes for
-- signed-in users therefore go through the Next.js server (which knows
-- the caller's Clerk identity) or the Python engine using
-- SUPABASE_SERVICE_ROLE_KEY (server-side only, never exposed to the
-- browser - see build spec section 25) - never directly from the
-- browser with a user-scoped Supabase policy. These policies exist to
-- lock down what a stray anon-key browser request could see, while
-- keeping public certificate verification working.

alter table careers enable row level security;
alter table skills enable row level security;
alter table career_skills enable row level security;
alter table analyses enable row level security;
alter table analysis_skills enable row level security;
alter table certificates enable row level security;

-- Reference data (careers/skills/career_skills) is safe to read publicly -
-- it contains no personal information.
create policy "careers are publicly readable"
    on careers for select
    using (true);

create policy "skills are publicly readable"
    on skills for select
    using (true);

create policy "career_skills are publicly readable"
    on career_skills for select
    using (true);

-- Analyses contain the user's name and results. No anon/authenticated
-- Supabase-key policy grants read access here on purpose - since
-- identity is Clerk's, not Supabase Auth's, per-user filtering has to
-- happen in the Next.js server (which verifies the Clerk session, then
-- reads with the service role key). Direct anon-key reads are denied by
-- default once RLS is enabled with no matching policy.

-- Certificates are meant to be PUBLICLY verifiable by anyone with the
-- certificate ID (build spec section 21), and intentionally exclude any
-- CV content or private information, so a public read policy is safe.
create policy "certificates are publicly readable for verification"
    on certificates for select
    using (true);

-- No insert/update/delete policies are defined for anon/authenticated
-- roles: all writes go through the Python engine using the service role
-- key, which bypasses RLS by design.
