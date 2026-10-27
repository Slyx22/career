-- Automatic deletion, matching the Privacy Policy ("How long we keep it"):
--   * analyses with no certificate: deleted 12 months after they were made
--   * certificates: deleted 24 months after they expire (valid 12 months,
--     so 36 months after issue), together with their analysis
--   * feature-interest feedback: deleted after 24 months
-- Runs every night at 03:15 UTC using pg_cron (free on Supabase).

create extension if not exists pg_cron;

create or replace function public.purge_expired_data()
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  delete from engine_certificates where issued_at < now() - interval '36 months';
  delete from engine_analyses a
   where a.created_at < now() - interval '12 months'
     and not exists (select 1 from engine_certificates c where c.analysis_id = a.id);
  delete from feature_interest where created_at < now() - interval '24 months';
end;
$$;

revoke all on function public.purge_expired_data() from public, anon, authenticated;

select cron.unschedule(jobid) from cron.job where jobname = 'purge-expired-data';
select cron.schedule('purge-expired-data', '15 3 * * *', $$select public.purge_expired_data();$$);
