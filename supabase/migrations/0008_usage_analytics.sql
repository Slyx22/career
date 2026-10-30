-- Anonymous usage analytics for the founder's /admin dashboard.
--
-- What we record: which step someone reached (opened the check page,
-- picked a career, chose a file, finished a check, clicked "Get my
-- certificate", shared it) plus the career involved. No names, no email,
-- no CV text, no Clerk user ID - only a random browser ID (so we can
-- count unique people) and whether the person was signed in.
--
-- Like the other tables, RLS is on with NO policies: the browser's anon
-- key can't read or write it. Only the server, using the service role
-- key, can insert events or call admin_usage_stats().
--
-- Run once: Supabase Dashboard -> SQL Editor -> paste -> Run. Safe to run again.

create table if not exists usage_events (
    id            bigint generated always as identity primary key,
    event         text not null check (event in (
                    'analyze_view',
                    'career_selected',
                    'file_chosen',
                    'check_submitted',
                    'check_completed',
                    'check_failed',
                    'results_view',
                    'certificate_clicked',
                    'certificate_view',
                    'share_clicked'
                  )),
    career        text check (char_length(career) <= 120),
    career_label  text check (char_length(career_label) <= 160),
    detail        text check (char_length(detail) <= 120),
    visitor_id    uuid,
    signed_in     boolean not null default false,
    created_at    timestamptz not null default now()
);

create index if not exists idx_usage_events_created on usage_events (created_at desc);
create index if not exists idx_usage_events_event_created on usage_events (event, created_at desc);

alter table usage_events enable row level security;
revoke all on usage_events from anon, authenticated;

comment on table usage_events is 'Anonymous funnel/click events for the founder analytics dashboard. No personal details.';

-- One call returns everything the dashboard shows, already aggregated, so
-- individual rows never leave the database.
create or replace function public.admin_usage_stats(p_days integer default null)
returns jsonb
language sql
stable
security definer
set search_path = public
as $$
with
  bounds as (
    select case when p_days is null then '-infinity'::timestamptz
                else now() - make_interval(days => p_days) end as since
  ),
  ev as (
    select e.* from usage_events e, bounds b where e.created_at >= b.since
  ),
  steps as (
    select event,
           count(*)                    as clicks,
           count(distinct visitor_id)  as people
      from ev group by event
  ),
  per_career as (
    select coalesce(nullif(career_label, ''), career)                              as career,
           count(*) filter (where event = 'career_selected')                         as selections,
           count(distinct visitor_id) filter (where event = 'career_selected')       as selected_by,
           count(*) filter (where event = 'check_submitted')                         as submitted,
           count(*) filter (where event = 'check_completed')                         as completed,
           count(*) filter (where event = 'check_failed')                            as failed,
           count(*) filter (where event = 'certificate_clicked')                     as certificate_clicks,
           count(*) filter (where event = 'share_clicked')                           as shares
      from ev
     where coalesce(nullif(career_label, ''), career) is not null
     group by 1
  ),
  scores as (
    select a.career, count(*) as checks, round(avg(a.score))::int as avg_score,
           count(*) filter (where a.score >= 70) as scored_70_plus
      from engine_analyses a, bounds b
     where a.created_at >= b.since
     group by a.career
  ),
  days as (
    select d::date as day
      from generate_series(
             (now() - make_interval(days => least(coalesce(p_days, 30), 90) - 1))::date,
             now()::date, interval '1 day') d
  ),
  daily as (
    select days.day,
           count(distinct e.visitor_id) filter (where e.event = 'analyze_view')     as visitors,
           count(*)                     filter (where e.event = 'career_selected')  as selections,
           count(*)                     filter (where e.event = 'check_completed')  as checks
      from days
      left join usage_events e on e.created_at::date = days.day
     group by days.day
  ),
  shares as (
    select coalesce(detail, 'other') as channel, count(*) as clicks
      from ev where event = 'share_clicked' group by 1
  ),
  failures as (
    select coalesce(detail, 'unknown') as reason, count(*) as times
      from ev where event = 'check_failed' group by 1
  ),
  interest as (
    select feature_key, count(*) as votes
      from feature_interest f, bounds b where f.created_at >= b.since group by 1
  )
select jsonb_build_object(
  'generated_at', now(),
  'days', p_days,
  'tracking_started', (select min(created_at) from usage_events),
  'unique_visitors', (select count(distinct visitor_id) from ev),
  'steps', coalesce((select jsonb_object_agg(event, jsonb_build_object('clicks', clicks, 'people', people)) from steps), '{}'::jsonb),
  'checks_all_time', (select count(*) from engine_analyses),
  'checks_in_period', (select count(*) from engine_analyses a, bounds b where a.created_at >= b.since),
  'signed_in_checkers', (select count(distinct clerk_user_id) from engine_analyses where clerk_user_id is not null),
  'certificates_all_time', (select count(*) from engine_certificates),
  'certificates_in_period', (select count(*) from engine_certificates c, bounds b where c.issued_at >= b.since),
  'per_career', coalesce((
      select jsonb_agg(jsonb_build_object(
               'career', coalesce(pc.career, s.career),
               'selections', coalesce(pc.selections, 0),
               'selected_by', coalesce(pc.selected_by, 0),
               'submitted', coalesce(pc.submitted, 0),
               'completed', coalesce(pc.completed, 0),
               'failed', coalesce(pc.failed, 0),
               'certificate_clicks', coalesce(pc.certificate_clicks, 0),
               'shares', coalesce(pc.shares, 0),
               'checks', coalesce(s.checks, 0),
               'avg_score', s.avg_score,
               'scored_70_plus', coalesce(s.scored_70_plus, 0)
             ) order by coalesce(pc.selections, 0) desc, coalesce(s.checks, 0) desc)
        from per_career pc full outer join scores s on s.career = pc.career), '[]'::jsonb),
  'daily', coalesce((select jsonb_agg(jsonb_build_object('day', day, 'visitors', visitors, 'selections', selections, 'checks', checks) order by day) from daily), '[]'::jsonb),
  'shares_by_channel', coalesce((select jsonb_agg(jsonb_build_object('channel', channel, 'clicks', clicks) order by clicks desc) from shares), '[]'::jsonb),
  'failures', coalesce((select jsonb_agg(jsonb_build_object('reason', reason, 'times', times) order by times desc) from failures), '[]'::jsonb),
  'feature_interest', coalesce((select jsonb_agg(jsonb_build_object('feature', feature_key, 'votes', votes) order by votes desc) from interest), '[]'::jsonb)
);
$$;

revoke all on function public.admin_usage_stats(integer) from public, anon, authenticated;
grant execute on function public.admin_usage_stats(integer) to service_role;

-- Retention: usage events are deleted after 12 months (Privacy Policy,
-- "How long we keep it"). Same nightly job as 0007.
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
  delete from usage_events where created_at < now() - interval '12 months';
end;
$$;

revoke all on function public.purge_expired_data() from public, anon, authenticated;
