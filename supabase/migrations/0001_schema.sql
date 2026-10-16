-- RunnerDrops schema v1
-- Content tables are public-read. Subscriber tables are private (service role only),
-- with a single security-definer RPC for sign-up from the site.

create extension if not exists "pgcrypto";

-- ---------- enums ----------
create type shoe_category   as enum ('racing','super_trainer','daily_trainer','stability','trail','track');
create type shoe_status     as enum ('rumored','upcoming','released','discontinued');
create type release_kind    as enum ('launch','colorway','restock','price_change','delay');
create type release_status  as enum ('rumored','confirmed','released','sold_out','cancelled');
create type subscriber_status as enum ('pending','active','stopped');

-- ---------- updated_at helper ----------
create or replace function set_updated_at() returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end $$;

-- ---------- brands ----------
create table brands (
  id          uuid primary key default gen_random_uuid(),
  slug        text not null unique,            -- 'new-balance'
  name        text not null,                   -- 'New Balance'
  wordmark    text,                            -- how the brand writes itself: 'HOKA', 'norda'
  logo_path   text,                            -- storage path: logos/new-balance.png
  website     text,
  sort_name   text generated always as (lower(regexp_replace(name,'[^A-Za-z0-9]','','g'))) stored,
  created_at  timestamptz not null default now()
);

-- ---------- shoes (a model, e.g. Alphafly 3) ----------
create table shoes (
  id            uuid primary key default gen_random_uuid(),
  brand_id      uuid not null references brands(id) on delete restrict,
  slug          text not null unique,          -- 'alphafly-3'
  name          text not null,                 -- 'Alphafly 3' (no brand)
  category      shoe_category not null,
  status        shoe_status not null default 'upcoming',
  msrp_cents    integer check (msrp_cents >= 0),
  weight_oz     numeric(4,1),
  drop_mm       numeric(3,1),
  plate         text,                          -- 'Carbon', 'Pebax', 'EnergyRods', null = none
  stack_mm      numeric(4,1),
  image_path    text,                          -- storage path for the square product shot
  summary       text,                          -- one-paragraph RunnerDrops take
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
create index shoes_brand_idx on shoes(brand_id);
create index shoes_category_idx on shoes(category);
create trigger shoes_updated before update on shoes for each row execute function set_updated_at();

-- ---------- colorways ----------
create table colorways (
  id          uuid primary key default gen_random_uuid(),
  shoe_id     uuid not null references shoes(id) on delete cascade,
  name        text not null,                   -- 'Volt', 'Platinum Tint', 'Berlin'
  sku         text,
  image_path  text,
  created_at  timestamptz not null default now(),
  unique (shoe_id, name)
);

-- ---------- retailers ----------
create table retailers (
  id                 uuid primary key default gen_random_uuid(),
  slug               text not null unique,
  name               text not null,
  domain             text,
  affiliate_network  text,                     -- 'CJ', 'Impact', 'Awin', null
  is_brand_store     boolean not null default false
);

-- ---------- releases: every dated event on the calendar ----------
create table releases (
  id            uuid primary key default gen_random_uuid(),
  shoe_id       uuid not null references shoes(id) on delete cascade,
  colorway_id   uuid references colorways(id) on delete set null,
  kind          release_kind not null default 'launch',
  status        release_status not null default 'confirmed',
  release_date  date,                          -- null when only a window is known
  release_time  time,                          -- local time of drop, if announced
  tz            text not null default 'America/New_York',
  window_label  text,                          -- 'Nov 2026', 'Holiday 2026' when release_date is null
  price_cents   integer check (price_cents >= 0),
  is_lead_drop  boolean not null default false, -- the one we feature that week
  source        text,                          -- 'retailer listing', 'athlete samples at Berlin'
  note          text,                          -- 'Winterized', 'Moved from Sep 18'
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  check (release_date is not null or window_label is not null)
);
create index releases_date_idx on releases(release_date);
create index releases_shoe_idx on releases(shoe_id);
create trigger releases_updated before update on releases for each row execute function set_updated_at();

-- where to buy a given release
create table release_retailers (
  release_id   uuid not null references releases(id) on delete cascade,
  retailer_id  uuid not null references retailers(id) on delete cascade,
  url          text,
  primary key (release_id, retailer_id)
);

-- ---------- price history (powers "Price watch") ----------
create table price_history (
  id           uuid primary key default gen_random_uuid(),
  shoe_id      uuid not null references shoes(id) on delete cascade,
  retailer_id  uuid references retailers(id) on delete set null,
  observed_on  date not null default current_date,
  price_cents  integer not null check (price_cents >= 0),
  label        text                            -- 'Launch', 'Jun 2026'
);
create index price_history_shoe_idx on price_history(shoe_id, observed_on desc);

-- ---------- the three-tier review system ----------
-- 01 RunnerDrops: our own score and verdict (lives on shoe_ratings)
-- 02 Reviewers:   individual outside reviews, aggregated into reviewers_pct
-- 03 Runners:     owner votes, aggregated into runners_pct
create table review_sources (
  id      uuid primary key default gen_random_uuid(),
  slug    text not null unique,
  name    text not null,
  domain  text
);

create table reviews (
  id            uuid primary key default gen_random_uuid(),
  shoe_id       uuid not null references shoes(id) on delete cascade,
  source_id     uuid not null references review_sources(id) on delete cascade,
  score         numeric(4,1),                  -- as published
  scale         numeric(4,1) not null default 10,
  url           text,
  pull_quote    text,
  published_on  date,
  unique (shoe_id, source_id)
);

create table runner_votes (
  id          uuid primary key default gen_random_uuid(),
  shoe_id     uuid not null references shoes(id) on delete cascade,
  voter_hash  text not null,                   -- hashed phone or device id; never raw
  would_buy_again boolean not null,
  created_at  timestamptz not null default now(),
  unique (shoe_id, voter_hash)
);

create table shoe_ratings (
  shoe_id          uuid primary key references shoes(id) on delete cascade,
  rd_score         numeric(3,1) check (rd_score between 0 and 10),
  rd_verdict       text,                       -- one-line RunnerDrops verdict
  reviewers_pct    smallint check (reviewers_pct between 0 and 100),
  reviewers_count  smallint,
  runners_pct      smallint check (runners_pct between 0 and 100),
  runners_count    integer,
  disagreement     text,                       -- the "Where they disagree" paragraph
  updated_at       timestamptz not null default now()
);
create trigger shoe_ratings_updated before update on shoe_ratings for each row execute function set_updated_at();

-- ---------- ranked "Best for" lists ----------
create table lists (
  id          uuid primary key default gen_random_uuid(),
  slug        text not null unique,            -- 'best-shoes-for-hyrox'
  title       text not null,                   -- 'Best shoes for HYROX'
  dek         text,
  use_case    text,                            -- 'HYROX', 'Trail', 'Under $150'
  published   boolean not null default false,
  updated_at  timestamptz not null default now()
);
create trigger lists_updated before update on lists for each row execute function set_updated_at();

create table list_entries (
  list_id   uuid not null references lists(id) on delete cascade,
  shoe_id   uuid not null references shoes(id) on delete cascade,
  rank      smallint not null,
  blurb     text,
  tags      text[] not null default '{}',      -- station / use tags: {'Sled push','8K run'}
  primary key (list_id, shoe_id),
  unique (list_id, rank)
);

-- ---------- subscribers (private) ----------
create table subscribers (
  id              uuid primary key default gen_random_uuid(),
  phone_e164      text not null unique check (phone_e164 ~ '^\+[1-9][0-9]{6,14}$'),
  status          subscriber_status not null default 'pending',
  consent_source  text,                        -- 'site:homepage', 'site:brand-nike'
  consented_at    timestamptz,
  stopped_at      timestamptz,
  created_at      timestamptz not null default now()
);

create table follows (
  id             uuid primary key default gen_random_uuid(),
  subscriber_id  uuid not null references subscribers(id) on delete cascade,
  brand_id       uuid references brands(id) on delete cascade,
  shoe_id        uuid references shoes(id) on delete cascade,
  category       shoe_category,
  restocks       boolean not null default false,   -- "Restocks" toggle
  created_at     timestamptz not null default now(),
  check (num_nonnulls(brand_id, shoe_id, category) = 1 or restocks),
  unique (subscriber_id, brand_id, shoe_id, category)
);
create index follows_subscriber_idx on follows(subscriber_id);

-- one row per text we send; enforces "one text per drop"
create table sms_messages (
  id             uuid primary key default gen_random_uuid(),
  subscriber_id  uuid not null references subscribers(id) on delete cascade,
  release_id     uuid references releases(id) on delete set null,
  body           text not null,
  provider_sid   text,
  status         text not null default 'queued',
  sent_at        timestamptz,
  created_at     timestamptz not null default now(),
  unique (subscriber_id, release_id)
);

-- ---------- views the site reads ----------
create view v_calendar as
select r.id, r.release_date, r.release_time, r.tz, r.window_label, r.kind, r.status,
       r.price_cents, r.is_lead_drop, r.source, r.note,
       s.id as shoe_id, s.slug as shoe_slug, s.name as shoe_name, s.category, s.image_path as shoe_image,
       c.name as colorway, coalesce(c.image_path, s.image_path) as image_path,
       b.slug as brand_slug, b.name as brand_name,
       (select array_agg(json_build_object('name', rt.name, 'url', rr.url) order by rt.is_brand_store desc, rt.name)
          from release_retailers rr join retailers rt on rt.id = rr.retailer_id where rr.release_id = r.id) as retailers
from releases r
join shoes s on s.id = r.shoe_id
join brands b on b.id = s.brand_id
left join colorways c on c.id = r.colorway_id;

create view v_shoe_cards as
select s.id, s.slug, s.name, s.category, s.status, s.msrp_cents, s.weight_oz, s.drop_mm, s.plate, s.image_path,
       b.slug as brand_slug, b.name as brand_name,
       sr.rd_score, sr.reviewers_pct, sr.runners_pct,
       (select min(release_date) from releases r where r.shoe_id = s.id and r.release_date >= current_date) as next_release_date
from shoes s
join brands b on b.id = s.brand_id
left join shoe_ratings sr on sr.shoe_id = s.id;

-- ---------- row level security ----------
alter table brands            enable row level security;
alter table shoes             enable row level security;
alter table colorways         enable row level security;
alter table retailers         enable row level security;
alter table releases          enable row level security;
alter table release_retailers enable row level security;
alter table price_history     enable row level security;
alter table review_sources    enable row level security;
alter table reviews           enable row level security;
alter table runner_votes      enable row level security;
alter table shoe_ratings      enable row level security;
alter table lists             enable row level security;
alter table list_entries      enable row level security;
alter table subscribers       enable row level security;
alter table follows           enable row level security;
alter table sms_messages      enable row level security;

-- public read on content
create policy "public read" on brands            for select using (true);
create policy "public read" on shoes             for select using (true);
create policy "public read" on colorways         for select using (true);
create policy "public read" on retailers         for select using (true);
create policy "public read" on releases          for select using (true);
create policy "public read" on release_retailers for select using (true);
create policy "public read" on price_history     for select using (true);
create policy "public read" on review_sources    for select using (true);
create policy "public read" on reviews           for select using (true);
create policy "public read" on shoe_ratings      for select using (true);
create policy "public read" on lists             for select using (published);
create policy "public read" on list_entries      for select using (exists (select 1 from lists l where l.id = list_id and l.published));
-- subscribers, follows, sms_messages, runner_votes: no public policies -> service role only

-- ---------- sign-up RPC (the only write the public site can make) ----------
create or replace function subscribe(
  p_phone        text,
  p_brands       text[]  default '{}',   -- brand slugs
  p_shoes        text[]  default '{}',   -- shoe slugs
  p_categories   text[]  default '{}',   -- shoe_category values
  p_restocks     boolean default false,
  p_source       text    default 'site'
) returns uuid
language plpgsql security definer set search_path = public as $$
declare v_id uuid;
begin
  insert into subscribers (phone_e164, consent_source)
  values (p_phone, p_source)
  on conflict (phone_e164) do update set consent_source = excluded.consent_source
  returning id into v_id;

  insert into follows (subscriber_id, brand_id)
  select v_id, b.id from brands b where b.slug = any(p_brands)
  on conflict do nothing;

  insert into follows (subscriber_id, shoe_id)
  select v_id, s.id from shoes s where s.slug = any(p_shoes)
  on conflict do nothing;

  insert into follows (subscriber_id, category)
  select v_id, c::shoe_category from unnest(p_categories) c
  on conflict do nothing;

  if p_restocks then
    insert into follows (subscriber_id, restocks) values (v_id, true) on conflict do nothing;
  end if;

  return v_id;
end $$;
revoke all on function subscribe from public;
grant execute on function subscribe to anon, authenticated;
