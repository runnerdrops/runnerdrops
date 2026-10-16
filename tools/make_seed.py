"""Generate supabase/seed.sql from the mockup content.
usage: python3 tools/make_seed.py > supabase/seed.sql
Everything in here is what the September 2026 mockup shows; replace as real data lands."""

def q(v):
    if v is None: return 'null'
    if isinstance(v, bool): return 'true' if v else 'false'
    if isinstance(v, (int, float)): return str(v)
    if isinstance(v, list): return "array[" + ",".join(q(x) for x in v) + "]::text[]" if v else "'{}'::text[]"
    return "'" + str(v).replace("'", "''") + "'"

out = []
P = out.append

# ---------- brands ----------
BRANDS = [  # slug, name, wordmark, website
    ('361', '361°', '361 Degrees', 'https://www.361usa.com'),
    ('adidas', 'adidas', 'adidas', 'https://www.adidas.com'),
    ('altra', 'Altra', 'Altra', 'https://www.altrarunning.com'),
    ('anta', 'ANTA', 'ANTA', 'https://www.anta.com'),
    ('asics', 'Asics', 'ASICS', 'https://www.asics.com'),
    ('brooks', 'Brooks', 'Brooks', 'https://www.brooksrunning.com'),
    ('diadora', 'Diadora', 'Diadora', 'https://www.diadora.com'),
    ('hoka', 'Hoka', 'HOKA', 'https://www.hoka.com'),
    ('kiprun', 'Kiprun', 'Kiprun', 'https://www.decathlon.com'),
    ('li-ning', 'Li-Ning', 'Li-Ning', 'https://www.li-ning.com'),
    ('mizuno', 'Mizuno', 'Mizuno', 'https://www.mizunousa.com'),
    ('new-balance', 'New Balance', 'New Balance', 'https://www.newbalance.com'),
    ('nike', 'Nike', 'Nike', 'https://www.nike.com'),
    ('norda', 'Norda', 'norda', 'https://nordarun.com'),
    ('on', 'On', 'On', 'https://www.on.com'),
    ('puma', 'Puma', 'PUMA', 'https://us.puma.com'),
    ('reebok', 'Reebok', 'Reebok', 'https://www.reebok.com'),
    ('salomon', 'Salomon', 'Salomon', 'https://www.salomon.com'),
    ('saucony', 'Saucony', 'Saucony', 'https://www.saucony.com'),
    ('under-armour', 'Under Armour', 'Under Armour', 'https://www.underarmour.com'),
]
P("-- brands")
P("insert into brands (slug, name, wordmark, logo_path, website) values")
P(",\n".join(f"  ({q(s)}, {q(n)}, {q(w)}, {q('logos/'+s+'.png')}, {q(u)})" for s, n, w, u in BRANDS) + "\non conflict (slug) do update set name=excluded.name, wordmark=excluded.wordmark, logo_path=excluded.logo_path, website=excluded.website;")

# ---------- shoes ----------
# slug, brand, name, category, status, msrp, oz, drop, plate, image
SHOES = [
    ('alphafly-3', 'nike', 'Alphafly 3', 'racing', 'released', 305, 7.7, 8, 'Carbon', 'shoes/NIKE_SQ.jpg'),
    ('adizero-adios-pro-4', 'adidas', 'Adizero Adios Pro 4', 'racing', 'released', 255, 7.1, 6, 'EnergyRods', 'shoes/ADI_SQ.jpg'),
    ('vaporfly-4', 'nike', 'Vaporfly 4', 'racing', 'upcoming', 260, 6.5, 6, 'Carbon', 'shoes/VF4_SQ.jpg'),
    ('vaporfly-3', 'nike', 'Vaporfly 3', 'racing', 'released', 260, 7.0, 8, 'Carbon', 'shoes/VF3_SQ.jpg'),
    ('endorphin-elite-2', 'saucony', 'Endorphin Elite 2', 'racing', 'upcoming', 275, 7.2, 8, 'Carbon', 'shoes/SAUC_SQ.jpg'),
    ('endorphin-pro-4', 'saucony', 'Endorphin Pro 4', 'racing', 'released', 225, 7.5, 8, 'Carbon', 'shoes/PRO4_SQ.jpg'),
    ('metaspeed-sky-paris', 'asics', 'Metaspeed Sky Paris', 'racing', 'released', 250, 6.5, 5, 'Carbon', 'shoes/META_SQ.jpg'),
    ('sc-elite-v5', 'new-balance', 'SC Elite v5', 'racing', 'upcoming', 250, 7.3, 4, 'Carbon', 'shoes/NB_SQ.jpg'),
    ('fast-r-nitro-elite-3', 'puma', 'Fast-R Nitro Elite 3', 'racing', 'upcoming', 300, 6.0, 8, 'Carbon', 'shoes/PUMA_SQ.jpg'),
    ('hyperion-elite-5', 'brooks', 'Hyperion Elite 5', 'racing', 'upcoming', 275, 7.4, 8, 'Carbon', 'shoes/BROOKS_SQ.jpg'),
    ('cielo-x1-2', 'hoka', 'Cielo X1 2.0', 'racing', 'upcoming', 275, 8.3, 7, 'Carbon', 'shoes/CIELO_SQ.jpg'),
    ('cloudboom-strike-ls', 'on', 'Cloudboom Strike LS', 'racing', 'upcoming', 330, 6.1, 4, 'Carbon', 'shoes/ON_SQ.jpg'),
    ('rocket-x-3', 'hoka', 'Rocket X 3', 'racing', 'upcoming', 250, 7.5, 7, 'Carbon', 'shoes/ROCKET_SQ.jpg'),
    ('mach-x-3', 'hoka', 'Mach X 3', 'super_trainer', 'upcoming', 190, 8.9, 5, 'Pebax', 'shoes/HOKA_SQ.jpg'),
    ('novablast-6', 'asics', 'Novablast 6', 'daily_trainer', 'upcoming', 150, 8.8, 8, None, 'shoes/ASICS_SQ.jpg'),
    ('clifton-10', 'hoka', 'Clifton 10', 'daily_trainer', 'released', 150, 9.8, 8, None, 'shoes/CLIFTON_SQ.jpg'),
    ('pegasus-42', 'nike', 'Pegasus 42', 'daily_trainer', 'released', 150, 9.6, 10, None, 'shoes/PEG42_SQ.jpg'),
    ('pegasus-plus-2', 'nike', 'Pegasus Plus 2', 'daily_trainer', 'rumored', 180, None, None, None, 'shoes/PEGPLUS2_SQ.jpg'),
    ('wave-rebellion-pro-3', 'mizuno', 'Wave Rebellion Pro 3', 'racing', 'rumored', 250, None, None, 'Carbon', 'shoes/MIZ_SQ.jpg'),
    ('alphafly-4', 'nike', 'Alphafly 4', 'racing', 'rumored', 310, None, None, 'Carbon', 'shoes/AF4_SQ.jpg'),
]
P("\n-- shoes")
P("insert into shoes (slug, brand_id, name, category, status, msrp_cents, weight_oz, drop_mm, plate, image_path) values")
P(",\n".join(f"  ({q(s)}, (select id from brands where slug={q(b)}), {q(n)}, {q(c)}, {q(st)}, {q(p*100 if p else None)}, {q(oz)}, {q(dr)}, {q(pl)}, {q(img)})"
            for s, b, n, c, st, p, oz, dr, pl, img in SHOES) + "\non conflict (slug) do update set status=excluded.status, msrp_cents=excluded.msrp_cents, image_path=excluded.image_path;")

# ---------- colorways ----------
COLORWAYS = [  # shoe, name
    ('alphafly-3', 'Platinum Tint'), ('alphafly-3', 'Volt'),
    ('vaporfly-4', 'Volt'), ('vaporfly-3', 'Volt'),
    ('adizero-adios-pro-4', 'Berlin'),
    ('pegasus-42', 'Shield'),
]
P("\n-- colorways")
P("insert into colorways (shoe_id, name) values")
P(",\n".join(f"  ((select id from shoes where slug={q(s)}), {q(n)})" for s, n in COLORWAYS) + "\non conflict do nothing;")

# ---------- retailers ----------
RETAILERS = [  # slug, name, domain, network, brand store
    ('nike', 'Nike.com', 'nike.com', None, True),
    ('adidas', 'adidas.com', 'adidas.com', None, True),
    ('hoka', 'Hoka.com', 'hoka.com', None, True),
    ('asics', 'Asics.com', 'asics.com', None, True),
    ('saucony', 'Saucony.com', 'saucony.com', None, True),
    ('on', 'On.com', 'on.com', None, True),
    ('running-warehouse', 'Running Warehouse', 'runningwarehouse.com', 'Impact', False),
    ('fleet-feet', 'Fleet Feet', 'fleetfeet.com', 'Impact', False),
]
P("\n-- retailers")
P("insert into retailers (slug, name, domain, affiliate_network, is_brand_store) values")
P(",\n".join(f"  ({q(s)}, {q(n)}, {q(d)}, {q(a)}, {q(b)})" for s, n, d, a, b in RETAILERS) + "\non conflict (slug) do nothing;")

# ---------- releases (September–November 2026 as shown on the mockup) ----------
# shoe, colorway, kind, status, date, window, price, lead, source, note, retailers
RELEASES = [
    ('clifton-10', None, 'launch', 'released', '2026-09-01', None, 150, False, None, None, ['hoka']),
    ('pegasus-42', None, 'launch', 'released', '2026-09-03', None, 150, False, None, None, ['nike']),
    ('metaspeed-sky-paris', None, 'restock', 'released', '2026-09-05', None, 250, False, None, None, ['asics']),
    ('mach-x-3', None, 'launch', 'confirmed', '2026-09-07', None, 190, False, None, None, ['hoka', 'running-warehouse']),
    ('novablast-6', None, 'launch', 'confirmed', '2026-09-08', None, 150, False, None, None, ['asics', 'fleet-feet']),
    ('endorphin-elite-2', None, 'launch', 'confirmed', '2026-09-09', None, 275, False, None, None, ['saucony']),
    ('alphafly-3', 'Platinum Tint', 'colorway', 'confirmed', '2026-09-10', None, 305, True, None, '10:00 AM ET', ['nike']),
    ('cloudboom-strike-ls', None, 'launch', 'confirmed', '2026-09-10', None, 330, False, None, None, ['on']),
    ('adizero-adios-pro-4', None, 'restock', 'confirmed', '2026-09-12', None, 255, False, None, None, ['adidas']),
    ('sc-elite-v5', None, 'launch', 'confirmed', '2026-09-14', None, 250, False, None, None, []),
    ('fast-r-nitro-elite-3', None, 'launch', 'confirmed', '2026-09-16', None, 300, False, None, None, []),
    ('rocket-x-3', None, 'launch', 'confirmed', '2026-09-17', None, 250, False, None, None, []),
    ('pegasus-plus-2', None, 'launch', 'rumored', '2026-09-18', None, 180, False, 'retailer listing', None, []),
    ('adizero-adios-pro-4', 'Berlin', 'colorway', 'confirmed', '2026-09-20', None, 255, True, None, 'Lead drop', ['adidas']),
    ('hyperion-elite-5', None, 'launch', 'confirmed', '2026-09-22', None, 275, False, None, None, []),
    ('vaporfly-4', 'Volt', 'launch', 'confirmed', '2026-09-24', None, 260, False, None, None, ['nike']),
    ('wave-rebellion-pro-3', None, 'launch', 'rumored', '2026-09-26', None, 250, False, 'Japan release', None, []),
    ('cielo-x1-2', None, 'delay', 'confirmed', '2026-10-02', None, 275, False, None, 'Moved from Sep 18', ['hoka']),
    ('alphafly-3', 'Volt', 'restock', 'confirmed', '2026-10-03', None, 305, False, None, None, ['nike']),
    ('pegasus-42', 'Shield', 'colorway', 'confirmed', '2026-10-15', None, 150, False, None, 'Winterized', ['nike']),
    ('alphafly-4', None, 'launch', 'rumored', None, 'Nov 2026', 310, False, 'athlete samples at Berlin', None, []),
]
P("\n-- releases")
for s, cw, kind, st, date, win, price, lead, src, note, rets in RELEASES:
    cw_sql = f"(select id from colorways where shoe_id=(select id from shoes where slug={q(s)}) and name={q(cw)})" if cw else 'null'
    P(f"with r as (insert into releases (shoe_id, colorway_id, kind, status, release_date, release_time, window_label, price_cents, is_lead_drop, source, note) values "
      f"((select id from shoes where slug={q(s)}), {cw_sql}, {q(kind)}, {q(st)}, {q(date)}, {q('10:00' if note == '10:00 AM ET' else None)}, {q(win)}, {q(price*100)}, {q(lead)}, {q(src)}, {q(None if note == '10:00 AM ET' else note)}) returning id)")
    if rets:
        P("insert into release_retailers (release_id, retailer_id) select r.id, rt.id from r, retailers rt where rt.slug in (" + ",".join(q(x) for x in rets) + ");")
    else:
        P("select id from r;")

# ---------- price history (Nike price watch on the brand page) ----------
PRICES = [
    ('alphafly-3', '2026-06-01', 285, 'Jun 2026'), ('alphafly-3', '2026-09-01', 305, 'Sep 2026'),
    ('vaporfly-4', '2026-09-24', 260, 'Launch'),
    ('pegasus-42', '2026-08-01', 150, 'Aug 2026'),
]
P("\n-- price history")
P("insert into price_history (shoe_id, observed_on, price_cents, label) values")
P(",\n".join(f"  ((select id from shoes where slug={q(s)}), {q(d)}, {p*100}, {q(l)})" for s, d, p, l in PRICES) + ";")

# ---------- review sources ----------
SOURCES = [('believe-in-the-run', 'Believe in the Run', 'believeintherun.com'), ('doctors-of-running', 'Doctors of Running', 'doctorsofrunning.com'),
           ('road-trail-run', 'Road Trail Run', 'roadtrailrun.com'), ('runrepeat', 'RunRepeat', 'runrepeat.com'), ('runnersworld', "Runner's World", 'runnersworld.com')]
P("\n-- review sources")
P("insert into review_sources (slug, name, domain) values")
P(",\n".join(f"  ({q(s)}, {q(n)}, {q(d)})" for s, n, d in SOURCES) + "\non conflict (slug) do nothing;")

# ---------- three-tier ratings ----------
# slug, rd_score, reviewers_pct, runners_pct
RATINGS = [
    ('alphafly-3', 9.2, 91, 87), ('adizero-adios-pro-4', None, 88, 78), ('vaporfly-4', None, 90, 84), ('vaporfly-3', 8.8, 89, 86),
    ('endorphin-elite-2', None, 86, 80), ('endorphin-pro-4', 8.4, 85, 83), ('metaspeed-sky-paris', 8.9, 92, 85), ('sc-elite-v5', None, 84, 79),
    ('fast-r-nitro-elite-3', None, 93, 81), ('hyperion-elite-5', None, 82, 76), ('cielo-x1-2', 8.1, 83, 77), ('cloudboom-strike-ls', None, 80, 72),
    ('rocket-x-3', None, 85, 80), ('mach-x-3', 8.7, 90, 88), ('novablast-6', 8.5, 88, 91), ('pegasus-42', 8.0, 84, 89),
]
P("\n-- shoe ratings (01 RunnerDrops / 02 Reviewers / 03 Runners)")
P("insert into shoe_ratings (shoe_id, rd_score, reviewers_pct, runners_pct) values")
P(",\n".join(f"  ((select id from shoes where slug={q(s)}), {q(rd)}, {rv}, {ru})" for s, rd, rv, ru in RATINGS)
  + "\non conflict (shoe_id) do update set rd_score=excluded.rd_score, reviewers_pct=excluded.reviewers_pct, runners_pct=excluded.runners_pct;")

# ---------- Best for HYROX ----------
HYROX = [
    ('mach-x-3', 'The default answer. Enough plate to push the 8K splits, enough rubber up front to hold a sled push. Runners rank it #1 for stations.', ['Sled push', '8K run']),
    ('novablast-6', 'Unplated, which is the point: stable on the lateral stations and no calf tax on the burpee broad jumps. Best value here.', ['Burpee BJ', 'Lunges']),
    ('fast-r-nitro-elite-3', "The racers' pick. Lightest plated shoe on the list, and the PWRPLATE is forgiving enough for farmer carries. Narrow heel though.", ['8K run', 'Carries']),
    ('endorphin-pro-4', 'More shoe than the Elite, less money. Wider platform than most carbon racers, which matters on the wall balls.', ['Wall balls', '8K run']),
    ('adizero-adios-pro-4', 'Fast and soft, but the soft narrow heel is a liability on sled pull. Pro Solo and Elite 15 territory only.', ['8K run']),
    ('vaporfly-3', 'Reliable, widely available, and a known quantity. Outsole is the weak point on the SkiErg-to-sled transition.', ['8K run']),
    ('cloudboom-strike-ls', 'Grippy and stable, but the price and low drop make it a hard sell for a station race.', ['Sled pull']),
    ('sc-elite-v5', 'Low 4 mm drop and a firm platform. Good for midfoot strikers, divisive for everyone else.', ['Rowing']),
    ('alphafly-3', 'Our 9.2, but the Air pods are a liability on the sled push and burpees. Marathon shoe, not a HYROX shoe.', []),
    ('cielo-x1-2', 'Too much stack for the lateral stations. Great on the road, unstable on the carpet.', []),
]
P("\n-- lists")
P("insert into lists (slug, title, dek, use_case, published) values ('best-shoes-for-hyrox', 'Best shoes for HYROX', 'Ranked for the 8K of running and the eight stations in between.', 'HYROX', true) on conflict (slug) do nothing;")
P("insert into lists (slug, title, use_case, published) values ('best-trail-running-shoes', 'Best trail running shoes', 'Trail', false), ('best-daily-trainers-under-150', 'Best daily trainers under $150', 'Under $150', false) on conflict (slug) do nothing;")
P("insert into list_entries (list_id, shoe_id, rank, blurb, tags) values")
P(",\n".join(f"  ((select id from lists where slug='best-shoes-for-hyrox'), (select id from shoes where slug={q(s)}), {i+1}, {q(b)}, {q(t)})" for i, (s, b, t) in enumerate(HYROX)) + "\non conflict do nothing;")

print("\n".join(out))
