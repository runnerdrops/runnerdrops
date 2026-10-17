-- Editorial content for shoe pages (the three-tier review), plus a flag for list entries that fell outside the cut.
create table shoe_editorial (
  shoe_id             uuid primary key references shoes(id) on delete cascade,
  dek                 text,          -- intro paragraph under the gallery
  colorway_label      text,          -- 'White / Volt / Barely Volt / Black · IR1817-100'
  released_label      text,          -- 'Released Jan 4, 2024'
  release_date_label  text,          -- 'Jan 4, 2024'
  stack_label         text,          -- '39 / 31'
  foam                text,          -- 'ZoomX'
  plate_label         text,          -- 'Full carbon'
  gallery             text[] not null default '{}',   -- storage paths; falls back to shoes.image_path
  rd                  jsonb,         -- {miles, body, quote, cite, pros[], cons[]}  or {queue, empty_h, empty_p} when untested
  reviewers           jsonb,         -- {count, pos, neu, neg, paras:[{label,text}], sources[]}
  runners             jsonb,         -- {count, pos, neu, neg, paras:[{label,text}], quote, cite, sources[]}
  disagreements       jsonb,         -- [{topic, sub, experts:{text,who}, runners:{text,who}}]
  retailers           jsonb,         -- [{name, status, price, url}]
  other_colorways     jsonb,         -- [{name, status}]
  updated_at          timestamptz not null default now()
);
create trigger shoe_editorial_updated before update on shoe_editorial for each row execute function set_updated_at();
alter table shoe_editorial enable row level security;
create policy "public read" on shoe_editorial for select using (true);

alter table list_entries add column made_cut boolean not null default true;
