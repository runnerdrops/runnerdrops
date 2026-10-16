-- brands
insert into brands (slug, name, wordmark, logo_path, website) values
  ('361', '361°', '361 Degrees', 'logos/361.png', 'https://www.361usa.com'),
  ('adidas', 'adidas', 'adidas', 'logos/adidas.png', 'https://www.adidas.com'),
  ('altra', 'Altra', 'Altra', 'logos/altra.png', 'https://www.altrarunning.com'),
  ('anta', 'ANTA', 'ANTA', 'logos/anta.png', 'https://www.anta.com'),
  ('asics', 'Asics', 'ASICS', 'logos/asics.png', 'https://www.asics.com'),
  ('brooks', 'Brooks', 'Brooks', 'logos/brooks.png', 'https://www.brooksrunning.com'),
  ('diadora', 'Diadora', 'Diadora', 'logos/diadora.png', 'https://www.diadora.com'),
  ('hoka', 'Hoka', 'HOKA', 'logos/hoka.png', 'https://www.hoka.com'),
  ('kiprun', 'Kiprun', 'Kiprun', 'logos/kiprun.png', 'https://www.decathlon.com'),
  ('li-ning', 'Li-Ning', 'Li-Ning', 'logos/li-ning.png', 'https://www.li-ning.com'),
  ('mizuno', 'Mizuno', 'Mizuno', 'logos/mizuno.png', 'https://www.mizunousa.com'),
  ('new-balance', 'New Balance', 'New Balance', 'logos/new-balance.png', 'https://www.newbalance.com'),
  ('nike', 'Nike', 'Nike', 'logos/nike.png', 'https://www.nike.com'),
  ('norda', 'Norda', 'norda', 'logos/norda.png', 'https://nordarun.com'),
  ('on', 'On', 'On', 'logos/on.png', 'https://www.on.com'),
  ('puma', 'Puma', 'PUMA', 'logos/puma.png', 'https://us.puma.com'),
  ('reebok', 'Reebok', 'Reebok', 'logos/reebok.png', 'https://www.reebok.com'),
  ('salomon', 'Salomon', 'Salomon', 'logos/salomon.png', 'https://www.salomon.com'),
  ('saucony', 'Saucony', 'Saucony', 'logos/saucony.png', 'https://www.saucony.com'),
  ('under-armour', 'Under Armour', 'Under Armour', 'logos/under-armour.png', 'https://www.underarmour.com')
on conflict (slug) do update set name=excluded.name, wordmark=excluded.wordmark, logo_path=excluded.logo_path, website=excluded.website;

-- shoes
insert into shoes (slug, brand_id, name, category, status, msrp_cents, weight_oz, drop_mm, plate, image_path) values
  ('alphafly-3', (select id from brands where slug='nike'), 'Alphafly 3', 'racing', 'released', 30500, 7.7, 8, 'Carbon', 'shoes/NIKE_SQ.jpg'),
  ('adizero-adios-pro-4', (select id from brands where slug='adidas'), 'Adizero Adios Pro 4', 'racing', 'released', 25500, 7.1, 6, 'EnergyRods', 'shoes/ADI_SQ.jpg'),
  ('vaporfly-4', (select id from brands where slug='nike'), 'Vaporfly 4', 'racing', 'upcoming', 26000, 6.5, 6, 'Carbon', 'shoes/VF4_SQ.jpg'),
  ('vaporfly-3', (select id from brands where slug='nike'), 'Vaporfly 3', 'racing', 'released', 26000, 7.0, 8, 'Carbon', 'shoes/VF3_SQ.jpg'),
  ('endorphin-elite-2', (select id from brands where slug='saucony'), 'Endorphin Elite 2', 'racing', 'upcoming', 27500, 7.2, 8, 'Carbon', 'shoes/SAUC_SQ.jpg'),
  ('endorphin-pro-4', (select id from brands where slug='saucony'), 'Endorphin Pro 4', 'racing', 'released', 22500, 7.5, 8, 'Carbon', 'shoes/PRO4_SQ.jpg'),
  ('metaspeed-sky-paris', (select id from brands where slug='asics'), 'Metaspeed Sky Paris', 'racing', 'released', 25000, 6.5, 5, 'Carbon', 'shoes/META_SQ.jpg'),
  ('sc-elite-v5', (select id from brands where slug='new-balance'), 'SC Elite v5', 'racing', 'upcoming', 25000, 7.3, 4, 'Carbon', 'shoes/NB_SQ.jpg'),
  ('fast-r-nitro-elite-3', (select id from brands where slug='puma'), 'Fast-R Nitro Elite 3', 'racing', 'upcoming', 30000, 6.0, 8, 'Carbon', 'shoes/PUMA_SQ.jpg'),
  ('hyperion-elite-5', (select id from brands where slug='brooks'), 'Hyperion Elite 5', 'racing', 'upcoming', 27500, 7.4, 8, 'Carbon', 'shoes/BROOKS_SQ.jpg'),
  ('cielo-x1-2', (select id from brands where slug='hoka'), 'Cielo X1 2.0', 'racing', 'upcoming', 27500, 8.3, 7, 'Carbon', 'shoes/CIELO_SQ.jpg'),
  ('cloudboom-strike-ls', (select id from brands where slug='on'), 'Cloudboom Strike LS', 'racing', 'upcoming', 33000, 6.1, 4, 'Carbon', 'shoes/ON_SQ.jpg'),
  ('rocket-x-3', (select id from brands where slug='hoka'), 'Rocket X 3', 'racing', 'upcoming', 25000, 7.5, 7, 'Carbon', 'shoes/ROCKET_SQ.jpg'),
  ('mach-x-3', (select id from brands where slug='hoka'), 'Mach X 3', 'super_trainer', 'upcoming', 19000, 8.9, 5, 'Pebax', 'shoes/HOKA_SQ.jpg'),
  ('novablast-6', (select id from brands where slug='asics'), 'Novablast 6', 'daily_trainer', 'upcoming', 15000, 8.8, 8, null, 'shoes/ASICS_SQ.jpg'),
  ('clifton-10', (select id from brands where slug='hoka'), 'Clifton 10', 'daily_trainer', 'released', 15000, 9.8, 8, null, 'shoes/CLIFTON_SQ.jpg'),
  ('pegasus-42', (select id from brands where slug='nike'), 'Pegasus 42', 'daily_trainer', 'released', 15000, 9.6, 10, null, 'shoes/PEG42_SQ.jpg'),
  ('pegasus-plus-2', (select id from brands where slug='nike'), 'Pegasus Plus 2', 'daily_trainer', 'rumored', 18000, null, null, null, 'shoes/PEGPLUS2_SQ.jpg'),
  ('wave-rebellion-pro-3', (select id from brands where slug='mizuno'), 'Wave Rebellion Pro 3', 'racing', 'rumored', 25000, null, null, 'Carbon', 'shoes/MIZ_SQ.jpg'),
  ('alphafly-4', (select id from brands where slug='nike'), 'Alphafly 4', 'racing', 'rumored', 31000, null, null, 'Carbon', 'shoes/AF4_SQ.jpg')
on conflict (slug) do update set status=excluded.status, msrp_cents=excluded.msrp_cents, image_path=excluded.image_path;

-- colorways
insert into colorways (shoe_id, name) values
  ((select id from shoes where slug='alphafly-3'), 'Platinum Tint'),
  ((select id from shoes where slug='alphafly-3'), 'Volt'),
  ((select id from shoes where slug='vaporfly-4'), 'Volt'),
  ((select id from shoes where slug='vaporfly-3'), 'Volt'),
  ((select id from shoes where slug='adizero-adios-pro-4'), 'Berlin'),
  ((select id from shoes where slug='pegasus-42'), 'Shield')
on conflict do nothing;

-- retailers
insert into retailers (slug, name, domain, affiliate_network, is_brand_store) values
  ('nike', 'Nike.com', 'nike.com', null, true),
  ('adidas', 'adidas.com', 'adidas.com', null, true),
  ('hoka', 'Hoka.com', 'hoka.com', null, true),
  ('asics', 'Asics.com', 'asics.com', null, true),
  ('saucony', 'Saucony.com', 'saucony.com', null, true),
  ('on', 'On.com', 'on.com', null, true),
  ('running-warehouse', 'Running Warehouse', 'runningwarehouse.com', 'Impact', false),
  ('fleet-feet', 'Fleet Feet', 'fleetfeet.com', 'Impact', false)
on conflict (slug) do nothing;

-- releases
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='clifton-10'), null, 'launch', 'released', '2026-09-01', null, null, 15000, false, null, null) returning id)
insert into release_retailers (release_id, retailer_id) select r.id, rt.id from r, retailers rt where rt.slug in ('hoka');
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='pegasus-42'), null, 'launch', 'released', '2026-09-03', null, null, 15000, false, null, null) returning id)
insert into release_retailers (release_id, retailer_id) select r.id, rt.id from r, retailers rt where rt.slug in ('nike');
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='metaspeed-sky-paris'), null, 'restock', 'released', '2026-09-05', null, null, 25000, false, null, null) returning id)
insert into release_retailers (release_id, retailer_id) select r.id, rt.id from r, retailers rt where rt.slug in ('asics');
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='mach-x-3'), null, 'launch', 'confirmed', '2026-09-07', null, null, 19000, false, null, null) returning id)
insert into release_retailers (release_id, retailer_id) select r.id, rt.id from r, retailers rt where rt.slug in ('hoka','running-warehouse');
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='novablast-6'), null, 'launch', 'confirmed', '2026-09-08', null, null, 15000, false, null, null) returning id)
insert into release_retailers (release_id, retailer_id) select r.id, rt.id from r, retailers rt where rt.slug in ('asics','fleet-feet');
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='endorphin-elite-2'), null, 'launch', 'confirmed', '2026-09-09', null, null, 27500, false, null, null) returning id)
insert into release_retailers (release_id, retailer_id) select r.id, rt.id from r, retailers rt where rt.slug in ('saucony');
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='alphafly-3'), (select id from colorways where shoe_id=(select id from shoes where slug='alphafly-3') and name='Platinum Tint'), 'colorway', 'confirmed', '2026-09-10', '10:00', null, 30500, true, null, null) returning id)
insert into release_retailers (release_id, retailer_id) select r.id, rt.id from r, retailers rt where rt.slug in ('nike');
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='cloudboom-strike-ls'), null, 'launch', 'confirmed', '2026-09-10', null, null, 33000, false, null, null) returning id)
insert into release_retailers (release_id, retailer_id) select r.id, rt.id from r, retailers rt where rt.slug in ('on');
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='adizero-adios-pro-4'), null, 'restock', 'confirmed', '2026-09-12', null, null, 25500, false, null, null) returning id)
insert into release_retailers (release_id, retailer_id) select r.id, rt.id from r, retailers rt where rt.slug in ('adidas');
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='sc-elite-v5'), null, 'launch', 'confirmed', '2026-09-14', null, null, 25000, false, null, null) returning id)
select id from r;
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='fast-r-nitro-elite-3'), null, 'launch', 'confirmed', '2026-09-16', null, null, 30000, false, null, null) returning id)
select id from r;
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='rocket-x-3'), null, 'launch', 'confirmed', '2026-09-17', null, null, 25000, false, null, null) returning id)
select id from r;
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='pegasus-plus-2'), null, 'launch', 'rumored', '2026-09-18', null, null, 18000, false, 'retailer listing', null) returning id)
select id from r;
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='adizero-adios-pro-4'), (select id from colorways where shoe_id=(select id from shoes where slug='adizero-adios-pro-4') and name='Berlin'), 'colorway', 'confirmed', '2026-09-20', null, null, 25500, true, null, 'Lead drop') returning id)
insert into release_retailers (release_id, retailer_id) select r.id, rt.id from r, retailers rt where rt.slug in ('adidas');
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='hyperion-elite-5'), null, 'launch', 'confirmed', '2026-09-22', null, null, 27500, false, null, null) returning id)
select id from r;
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='vaporfly-4'), (select id from colorways where shoe_id=(select id from shoes where slug='vaporfly-4') and name='Volt'), 'launch', 'confirmed', '2026-09-24', null, null, 26000, false, null, null) returning id)
insert into release_retailers (release_id, retailer_id) select r.id, rt.id from r, retailers rt where rt.slug in ('nike');
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='wave-rebellion-pro-3'), null, 'launch', 'rumored', '2026-09-26', null, null, 25000, false, 'Japan release', null) returning id)
select id from r;
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='cielo-x1-2'), null, 'delay', 'confirmed', '2026-10-02', null, null, 27500, false, null, 'Moved from Sep 18') returning id)
insert into release_retailers (release_id, retailer_id) select r.id, rt.id from r, retailers rt where rt.slug in ('hoka');
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='alphafly-3'), (select id from colorways where shoe_id=(select id from shoes where slug='alphafly-3') and name='Volt'), 'restock', 'confirmed', '2026-10-03', null, null, 30500, false, null, null) returning id)
insert into release_retailers (release_id, retailer_id) select r.id, rt.id from r, retailers rt where rt.slug in ('nike');
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='pegasus-42'), (select id from colorways where shoe_id=(select id from shoes where slug='pegasus-42') and name='Shield'), 'colorway', 'confirmed', '2026-10-15', null, null, 15000, false, null, 'Winterized') returning id)
insert into release_retailers (release_id, retailer_id) select r.id, rt.id from r, retailers rt where rt.slug in ('nike');
with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values ((select id from shoes where slug='alphafly-4'), null, 'launch', 'rumored', null, null, 'Nov 2026', 31000, false, 'athlete samples at Berlin', null) returning id)
select id from r;

-- price history
insert into price_history (shoe_id, observed_on, price_cents, label) values
  ((select id from shoes where slug='alphafly-3'), '2026-06-01', 28500, 'Jun 2026'),
  ((select id from shoes where slug='alphafly-3'), '2026-09-01', 30500, 'Sep 2026'),
  ((select id from shoes where slug='vaporfly-4'), '2026-09-24', 26000, 'Launch'),
  ((select id from shoes where slug='pegasus-42'), '2026-08-01', 15000, 'Aug 2026');

-- review sources
insert into review_sources (slug, name, domain) values
  ('believe-in-the-run', 'Believe in the Run', 'believeintherun.com'),
  ('doctors-of-running', 'Doctors of Running', 'doctorsofrunning.com'),
  ('road-trail-run', 'Road Trail Run', 'roadtrailrun.com'),
  ('runrepeat', 'RunRepeat', 'runrepeat.com'),
  ('runnersworld', 'Runner''s World', 'runnersworld.com')
on conflict (slug) do nothing;

-- shoe ratings (01 RunnerDrops / 02 Reviewers / 03 Runners)
insert into shoe_ratings (shoe_id, rd_score, reviewers_pct, runners_pct) values
  ((select id from shoes where slug='alphafly-3'), 9.2, 91, 87),
  ((select id from shoes where slug='adizero-adios-pro-4'), null, 88, 78),
  ((select id from shoes where slug='vaporfly-4'), null, 90, 84),
  ((select id from shoes where slug='vaporfly-3'), 8.8, 89, 86),
  ((select id from shoes where slug='endorphin-elite-2'), null, 86, 80),
  ((select id from shoes where slug='endorphin-pro-4'), 8.4, 85, 83),
  ((select id from shoes where slug='metaspeed-sky-paris'), 8.9, 92, 85),
  ((select id from shoes where slug='sc-elite-v5'), null, 84, 79),
  ((select id from shoes where slug='fast-r-nitro-elite-3'), null, 93, 81),
  ((select id from shoes where slug='hyperion-elite-5'), null, 82, 76),
  ((select id from shoes where slug='cielo-x1-2'), 8.1, 83, 77),
  ((select id from shoes where slug='cloudboom-strike-ls'), null, 80, 72),
  ((select id from shoes where slug='rocket-x-3'), null, 85, 80),
  ((select id from shoes where slug='mach-x-3'), 8.7, 90, 88),
  ((select id from shoes where slug='novablast-6'), 8.5, 88, 91),
  ((select id from shoes where slug='pegasus-42'), 8.0, 84, 89)
on conflict (shoe_id) do update set rd_score=excluded.rd_score, reviewers_pct=excluded.reviewers_pct, runners_pct=excluded.runners_pct;

-- lists
insert into lists (slug, title, dek, use_case, published) values ('best-shoes-for-hyrox', 'Best shoes for HYROX', 'Ranked for the 8K of running and the eight stations in between.', 'HYROX', true) on conflict (slug) do nothing;
insert into lists (slug, title, use_case, published) values ('best-trail-running-shoes', 'Best trail running shoes', 'Trail', false), ('best-daily-trainers-under-150', 'Best daily trainers under $150', 'Under $150', false) on conflict (slug) do nothing;
insert into list_entries (list_id, shoe_id, rank, blurb, tags) values
  ((select id from lists where slug='best-shoes-for-hyrox'), (select id from shoes where slug='mach-x-3'), 1, 'The default answer. Enough plate to push the 8K splits, enough rubber up front to hold a sled push. Runners rank it #1 for stations.', array['Sled push','8K run']::text[]),
  ((select id from lists where slug='best-shoes-for-hyrox'), (select id from shoes where slug='novablast-6'), 2, 'Unplated, which is the point: stable on the lateral stations and no calf tax on the burpee broad jumps. Best value here.', array['Burpee BJ','Lunges']::text[]),
  ((select id from lists where slug='best-shoes-for-hyrox'), (select id from shoes where slug='fast-r-nitro-elite-3'), 3, 'The racers'' pick. Lightest plated shoe on the list, and the PWRPLATE is forgiving enough for farmer carries. Narrow heel though.', array['8K run','Carries']::text[]),
  ((select id from lists where slug='best-shoes-for-hyrox'), (select id from shoes where slug='endorphin-pro-4'), 4, 'More shoe than the Elite, less money. Wider platform than most carbon racers, which matters on the wall balls.', array['Wall balls','8K run']::text[]),
  ((select id from lists where slug='best-shoes-for-hyrox'), (select id from shoes where slug='adizero-adios-pro-4'), 5, 'Fast and soft, but the soft narrow heel is a liability on sled pull. Pro Solo and Elite 15 territory only.', array['8K run']::text[]),
  ((select id from lists where slug='best-shoes-for-hyrox'), (select id from shoes where slug='vaporfly-3'), 6, 'Reliable, widely available, and a known quantity. Outsole is the weak point on the SkiErg-to-sled transition.', array['8K run']::text[]),
  ((select id from lists where slug='best-shoes-for-hyrox'), (select id from shoes where slug='cloudboom-strike-ls'), 7, 'Grippy and stable, but the price and low drop make it a hard sell for a station race.', array['Sled pull']::text[]),
  ((select id from lists where slug='best-shoes-for-hyrox'), (select id from shoes where slug='sc-elite-v5'), 8, 'Low 4 mm drop and a firm platform. Good for midfoot strikers, divisive for everyone else.', array['Rowing']::text[]),
  ((select id from lists where slug='best-shoes-for-hyrox'), (select id from shoes where slug='alphafly-3'), 9, 'Our 9.2, but the Air pods are a liability on the sled push and burpees. Marathon shoe, not a HYROX shoe.', '{}'::text[]),
  ((select id from lists where slug='best-shoes-for-hyrox'), (select id from shoes where slug='cielo-x1-2'), 10, 'Too much stack for the lateral stations. Great on the road, unstable on the carpet.', '{}'::text[])
on conflict do nothing;
