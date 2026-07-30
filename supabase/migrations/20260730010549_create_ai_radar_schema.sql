create table public.radar_snapshots (
  radar_date date primary key,
  contract_version text not null check (contract_version ~ '^\d+\.\d+\.\d+$'),
  generated_at timestamptz not null,
  topic text not null check (length(btrim(topic)) > 0),
  locale text not null check (length(btrim(locale)) >= 2),
  source_file text not null unique,
  created_at timestamptz not null default now()
);

create table public.signals (
  id text primary key check (id ~ '^\d{4}-\d{2}-\d{2}-[a-z0-9-]+$'),
  radar_date date not null references public.radar_snapshots (radar_date) on delete cascade,
  title text not null check (length(btrim(title)) > 0),
  source_name text not null check (length(btrim(source_name)) > 0),
  source_url text not null check (source_url ~ '^https?://'),
  published_at date not null,
  retrieved_at date not null,
  source_type text not null check (
    source_type in ('news', 'official', 'paper', 'repo', 'product', 'social')
  ),
  evidence jsonb not null check (
    jsonb_typeof(evidence) = 'array' and jsonb_array_length(evidence) > 0
  ),
  impact_level text not null check (
    impact_level in ('low', 'medium', 'medium-high', 'high')
  ),
  impact_summary text not null check (length(btrim(impact_summary)) > 0),
  action text not null check (length(btrim(action)) > 0),
  status text not null check (
    status in ('candidate', 'debated', 'evolving', 'confirmed', 'actionable', 'archived')
  ),
  tags jsonb not null check (
    jsonb_typeof(tags) = 'array' and jsonb_array_length(tags) > 0
  ),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (id like radar_date::text || '-%')
);

create table public.rankings (
  radar_date date primary key,
  generated_at timestamptz not null,
  reviewed_snapshot text not null,
  scoring_version text not null check (scoring_version ~ '^\d+\.\d+\.\d+$'),
  weights jsonb not null check (jsonb_typeof(weights) = 'object'),
  audit jsonb not null check (jsonb_typeof(audit) = 'object'),
  source_file text not null unique,
  created_at timestamptz not null default now()
);

create table public.ranking_entries (
  ranking_date date not null references public.rankings (radar_date) on delete cascade,
  signal_id text not null references public.signals (id) on delete cascade,
  rank integer not null check (rank > 0),
  score numeric(4, 2) not null check (score >= 0 and score <= 5),
  dimensions jsonb not null check (jsonb_typeof(dimensions) = 'object'),
  reason text not null check (length(btrim(reason)) > 0),
  primary key (ranking_date, signal_id),
  unique (ranking_date, rank)
);

create table public.source_candidate_batches (
  source_file text primary key,
  generated_at timestamptz not null,
  retrieved_from text not null check (length(btrim(retrieved_from)) > 0),
  topic text not null check (length(btrim(topic)) > 0),
  locale text not null check (length(btrim(locale)) >= 2),
  window_from date,
  window_to date,
  created_at timestamptz not null default now(),
  check (
    (window_from is null and window_to is null)
    or (window_from is not null and window_to is not null and window_from <= window_to)
  )
);

create table public.source_candidates (
  batch_file text not null references public.source_candidate_batches (source_file) on delete cascade,
  source_id text not null,
  canonical_url text not null check (canonical_url ~ '^https?://'),
  source_name text not null check (length(btrim(source_name)) > 0),
  source_type text not null check (
    source_type in ('news', 'official', 'paper', 'repo', 'product', 'social')
  ),
  title text not null check (length(btrim(title)) > 0),
  published_at date not null,
  retrieved_at date not null,
  actors jsonb not null check (jsonb_typeof(actors) = 'array'),
  topics jsonb not null check (jsonb_typeof(topics) = 'array'),
  raw_input text not null,
  facts jsonb not null check (
    jsonb_typeof(facts) = 'array' and jsonb_array_length(facts) > 0
  ),
  inferences jsonb not null check (jsonb_typeof(inferences) = 'array'),
  confidence text not null check (confidence in ('low', 'medium', 'high')),
  created_at timestamptz not null default now(),
  primary key (batch_file, source_id)
);

create index signals_radar_date_idx on public.signals (radar_date);
create index signals_published_at_idx on public.signals (published_at desc);
create index signals_status_idx on public.signals (status);
create index signals_source_type_idx on public.signals (source_type);
create index signals_tags_gin_idx on public.signals using gin (tags);
create index ranking_entries_signal_id_idx on public.ranking_entries (signal_id);
create index source_candidates_published_at_idx on public.source_candidates (published_at desc);
create index source_candidates_topics_gin_idx on public.source_candidates using gin (topics);

alter table public.radar_snapshots enable row level security;
alter table public.signals enable row level security;
alter table public.rankings enable row level security;
alter table public.ranking_entries enable row level security;
alter table public.source_candidate_batches enable row level security;
alter table public.source_candidates enable row level security;

revoke all on table public.radar_snapshots from anon, authenticated;
revoke all on table public.signals from anon, authenticated;
revoke all on table public.rankings from anon, authenticated;
revoke all on table public.ranking_entries from anon, authenticated;
revoke all on table public.source_candidate_batches from anon, authenticated;
revoke all on table public.source_candidates from anon, authenticated;

grant select on table public.radar_snapshots to anon, authenticated;
grant select on table public.signals to anon, authenticated;
grant select on table public.rankings to anon, authenticated;
grant select on table public.ranking_entries to anon, authenticated;

grant all on table public.radar_snapshots to service_role;
grant all on table public.signals to service_role;
grant all on table public.rankings to service_role;
grant all on table public.ranking_entries to service_role;
grant all on table public.source_candidate_batches to service_role;
grant all on table public.source_candidates to service_role;

create policy "Published snapshots are publicly readable"
on public.radar_snapshots
for select
to anon, authenticated
using (true);

create policy "Published signals are publicly readable"
on public.signals
for select
to anon, authenticated
using (true);

create policy "Published rankings are publicly readable"
on public.rankings
for select
to anon, authenticated
using (true);

create policy "Published ranking entries are publicly readable"
on public.ranking_entries
for select
to anon, authenticated
using (true);

comment on table public.radar_snapshots is
  'Versioned metadata for each curated AI Radar daily snapshot.';
comment on table public.signals is
  'Published, curated AI Radar signals. Public roles have read-only access.';
comment on table public.rankings is
  'Metadata and audit details for deterministic editorial rankings.';
comment on table public.ranking_entries is
  'Ordered signal scores belonging to a deterministic ranking.';
comment on table public.source_candidate_batches is
  'Internal provenance for pre-curation candidate batches.';
comment on table public.source_candidates is
  'Internal normalized candidates; intentionally inaccessible to public API roles.';
