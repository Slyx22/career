-- Row Level Security.
--
-- Phase 1 does not require authentication to run an analysis (build spec
-- section 24), so analyses/certificates are created via the Python engine
-- using the SUPABASE_SERVICE_ROLE_KEY (server-side only, never exposed to
-- the browser - see build spec section 25). These policies lock down
-- what the browser's anon/authenticated key can see directly, while
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

-- Analyses contain the user's name and results. Only the owning user (once
-- they've created an account and the analysis is linked to user_id) can
-- read their own analysis directly from the browser. Anonymous analyses
-- (user_id is null) are only readable via the Python service role, e.g.
-- to render the results page server-side.
create policy "users can read their own analyses"
    on analyses for select
    using (auth.uid() = user_id);

create policy "users can read their own analysis skills"
    on analysis_skills for select
    using (
        exists (
            select 1 from analyses a
            where a.id = analysis_skills.analysis_id
              and a.user_id = auth.uid()
        )
    );

-- Certificates are meant to be PUBLICLY verifiable by anyone with the
-- certificate ID (build spec section 21), and intentionally exclude any
-- CV content or private information, so a public read policy is safe.
create policy "certificates are publicly readable for verification"
    on certificates for select
    using (true);

-- No insert/update/delete policies are defined for anon/authenticated
-- roles: all writes go through the Python engine using the service role
-- key, which bypasses RLS by design.
