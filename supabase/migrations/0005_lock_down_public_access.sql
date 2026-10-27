-- Lock down public (anon key) access.
--
-- Before this migration, the "certificates are publicly readable" policy
-- let anyone holding the project's anon key run `select * from
-- certificates` and download every holder's name and score at once.
-- Verification only ever needs ONE certificate looked up by its ID, and
-- that lookup goes through the server (Python engine / Next.js) with the
-- service role key, which bypasses RLS. So no anon policy is needed.
--
-- feature_interest had an INSERT policy open to everyone, which let
-- anyone spam the table straight from the browser. The Next.js route
-- already writes with the service role key, so that policy can go too.
--
-- Run this once in the Supabase SQL editor (Dashboard -> SQL Editor ->
-- paste -> Run). It is safe to run more than once.

drop policy if exists "certificates are publicly readable for verification" on certificates;

drop policy if exists "Users can express interest in features" on feature_interest;
drop policy if exists "Users can view their own interests" on feature_interest;

-- RLS stays enabled on every table; with no anon/authenticated policies,
-- the browser-side anon key can read and write nothing in them.
alter table if exists certificates enable row level security;
alter table if exists analyses enable row level security;
alter table if exists analysis_skills enable row level security;
alter table if exists feature_interest enable row level security;
