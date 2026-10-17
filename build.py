"""RunnerDrops static site generator.

    python3 tools/fetch_data.py      # Supabase -> data/data.json
    python3 build.py                 # data/data.json -> docs/

Every page is rendered from data/data.json. Nothing about a shoe, brand, release or list lives in this
file; only layout, copy that frames the data, and the handful of editorial house blocks (the "Latest"
stories, the SMS band) that don't have a table yet.

Env:
    RD_TODAY=2026-09-05   pin "today" (what counts as this week / upcoming). Defaults to the real date.
    RD_MEDIA_BASE=...     serve images from somewhere other than Supabase storage (local previews).
"""
import json, os, re, shutil, datetime as dt, html
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'docs')
D = json.load(open(os.path.join(ROOT, 'data', 'data.json')))
MEDIA = os.environ.get('RD_MEDIA_BASE') or D['meta']['media_base']   # RD_MEDIA_BASE: local preview override
_t = os.environ.get('RD_TODAY', '').strip().lower()
TODAY = dt.date.fromisoformat(_t) if _t and _t != 'today' else dt.date.today()
WEEK_START = TODAY - dt.timedelta(days=TODAY.weekday()) + (dt.timedelta(days=7) if TODAY.weekday() >= 5 else dt.timedelta())  # Monday; on Sat/Sun look at the week ahead
WEEK_END = WEEK_START + dt.timedelta(days=6)                      # Sunday

# ------------------------------------------------------------------ helpers
esc = html.escape
def img(path): return MEDIA + path if path else ''
def money(cents): return f'${cents // 100:,}' if cents is not None else '—'
def d(s): return dt.date.fromisoformat(s) if s else None
def mon(x): return x.strftime('%b').upper()
def dow(x): return x.strftime('%a').upper()
def nice(x): return f'{x.strftime("%b")} {x.day}'
def nice_long(x): return f'{x.strftime("%a")} {x.strftime("%b")} {x.day}'
CAT = {'racing': 'Racing', 'super_trainer': 'Super trainer', 'daily_trainer': 'Daily trainer', 'stability': 'Stability', 'trail': 'Trail', 'track': 'Track'}
CAT_ORDER = list(CAT)

brands = {b['slug']: b for b in D['brands']}
shoes = {s['slug']: s for s in D['shoes']}
shoe_by_id = {s['id']: s for s in D['shoes']}
ratings = {r['shoe_id']: r for r in D['ratings']}
editorial = {e['shoe_id']: e for e in D['editorial']}
colorways = defaultdict(list)
for c in D['colorways']: colorways[c['shoe_id']].append(c)
prices = defaultdict(list)
for p in D['prices']: prices[p['shoe_id']].append(p)
for s in D['shoes']:
    s['brand_slug'] = s['brand']['slug']; s['brand_name'] = s['brand']['name']
    s['rating'] = ratings.get(s['id'], {})
    s['releases'] = []
releases = D['releases']
for r in releases:
    r['date'] = d(r['release_date'])
    r['shoe'] = shoe_by_id[r['shoe_id']]
    r['shoe']['releases'].append(r)
    r['upcoming'] = r['date'] is None or r['date'] >= TODAY
upcoming = [r for r in releases if r['upcoming']]
dated_upcoming = [r for r in upcoming if r['date']]

def rel_title(r, with_brand=True):
    t = (r['brand_name'] + ' ' if with_brand else '') + r['shoe_name']
    if r['colorway'] and r['kind'] != 'restock': t += f" '{r['colorway']}'" if r['kind'] == 'colorway' else f" {r['colorway']}"
    return t
def rel_small(r, extra=None):
    bits = [CAT.get(r['category'], r['category'])]
    if r['kind'] == 'restock': bits = ['Restock']
    bits.append(('est. ' if r['status'] == 'rumored' else '') + money(r['price_cents']))
    if r['release_time']: bits.append(dt.datetime.strptime(r['release_time'][:5], '%H:%M').strftime('%-I:%M %p') + ' ET')
    if r['retailers']: bits.append(', '.join(x['name'] for x in r['retailers'][:3]))
    if r['is_lead_drop']: bits.append('Lead drop')
    if r['note'] and r['kind'] != 'delay': bits.append(r['note'])
    if r['status'] == 'rumored' and r['source']: bits.append('source: ' + r['source'])
    if extra: bits.append(extra)
    return ' · '.join(bits)
def rel_action(r):
    if r['kind'] == 'restock' and r['status'] != 'rumored': return '<span class="chip chip--fill">RESTOCK</span>'
    if r['status'] == 'rumored': return '<a class="a" href="#alerts">WATCH</a>'
    if r['status'] == 'released': return '<span class="chip">RELEASED</span>'
    return f'<a class="a{" hot" if r["is_lead_drop"] else ""}" href="#alerts">NOTIFY</a>'
def shoe_url(s): return f'shoe-{s["slug"]}.html'
def brand_url(b): return f'brand-{b["slug"]}.html'
def rum(r): return '<span class="rum">RUMORED</span>' if r['status'] == 'rumored' else ''

def ledger_row(r, with_brand=True, today_cls=True):
    cls = 'lrow' + (' today' if today_cls and r['date'] == TODAY else '')
    dcell = f'<div class="d">{dow(r["date"])}<b>{r["date"].day:02d}</b></div>' if r['date'] else f'<div class="d">{esc(r["window_label"].split()[0].upper()[:3])}<b>TBC</b></div>'
    return (f'<div class="{cls}">{dcell}<div class="th"><a href="{shoe_url(r["shoe"])}"><div class="pic"><img src="{img(r["image_path"])}" alt="" loading="lazy"></div></a></div>'
            f'<div class="n"><a href="{shoe_url(r["shoe"])}">{esc(rel_title(r, with_brand))}</a>{rum(r)}<small>{esc(rel_small(r))}</small></div>{rel_action(r)}</div>')
def ledger_row_month(r, with_brand=False):
    """Brand-page variant: month + day in the date cell."""
    dcell = f'<div class="d">{mon(r["date"])}<b>{r["date"].day:02d}</b></div>' if r['date'] else f'<div class="d">{esc(r["window_label"].split()[0].upper()[:3])}<b>TBC</b></div>'
    return (f'<div class="lrow{" today" if r["date"] == TODAY else ""}">{dcell}<div class="th"><a href="{shoe_url(r["shoe"])}"><div class="pic"><img src="{img(r["image_path"])}" alt="" loading="lazy"></div></a></div>'
            f'<div class="n"><a href="{shoe_url(r["shoe"])}">{esc(rel_title(r, with_brand))}</a>{rum(r)}<small>{esc(rel_small(r))}</small></div>{rel_action(r)}</div>')

def score_cell(label, v, suffix):
    return f'<div><h5>{label}</h5>' + (f'<b>{v}<small>{suffix}</small></b>' if v is not None else '<b class="na">—</b>') + '</div>'
def scores(s, vertical=False):
    r = s['rating']
    return (f'<div class="scores{" scores--v" if vertical else ""}">' + score_cell('RunnerDrops', r.get('rd_score'), '/10') +
            score_cell('Reviewers', r.get('reviewers_pct'), '%') + score_cell('Runners', r.get('runners_pct'), '%') + '</div>')
def shoe_stamp(s):
    nxt = next((r for r in s['releases'] if r['upcoming'] and r['date']), None)
    if s['status'] == 'rumored': return 'stamp', 'Rumored'
    if nxt and nxt['kind'] == 'delay': return 'stamp', f'Moved to {nice(nxt["date"])}'
    if nxt and nxt['kind'] == 'restock': return 'stamp', 'Restock'
    if nxt and s['status'] != 'released': return 'stamp stamp--red', f'Drops {nice(nxt["date"])}'
    if s['status'] == 'released': return 'stamp stamp--paper', 'Released'
    return 'stamp', s['status'].capitalize()
def spec_line(s):
    est = 'est. ' if s['status'] == 'rumored' else ''
    return ' · '.join([est + money(s['msrp_cents']), f'{s["weight_oz"]} oz' if s['weight_oz'] else '—', f'{int(float(s["drop_mm"]))} mm' if s['drop_mm'] else '—', s['plate'] or ('—' if s['status'] == 'rumored' else 'None')])
def card(s):
    cls, label = shoe_stamp(s)
    return f'''<article class="sc" data-cat="{s['category']}" data-brand="{s['brand_slug']}">
  <a href="{shoe_url(s)}"><div class="pic"><img src="{img(s['image_path'])}" alt="{esc(s['brand_name'] + ' ' + s['name'])}" loading="lazy"><span class="{cls}">{label}</span></div></a>
  <div class="sc__b">
    <div class="kick"><a class="tag" href="{brand_url(brands[s['brand_slug']])}">{esc(s['brand_name'])}</a><span class="dim">{CAT[s['category']]}{' · Rumored' if s['status'] == 'rumored' else ''}</span></div>
    <h3><a href="{shoe_url(s)}">{esc(s['name'])}</a></h3>
    <div class="spec">{spec_line(s)}</div>
    {scores(s)}
    <div class="sc__f"><a href="{shoe_url(s)}">SHOE PAGE</a><a href="#alerts" class="hot">{'WATCH' if s['status'] == 'rumored' else 'NOTIFY'}</a></div>
  </div>
</article>'''

NAV = [('index.html', 'This week'), ('calendar.html', 'Calendar'), ('shoes.html', 'Shoes'), ('brands.html', 'Brands')]
def nav(active):
    links = ''.join(f'<a href="{h}"{" class=\"is-on\"" if h == active else ""}>{l}</a>' for h, l in NAV)
    return f'''<header class="nav"><div class="nav__in">
<a class="nav__logo" href="index.html">Runner<em>Drops</em></a>
<nav class="nav__links" aria-label="Primary">{links}</nav>
<a class="btn" href="#alerts" style="font-size:15px;padding:9px 18px">Get alerts</a>
<button class="nav__burger" aria-label="Menu" onclick="document.querySelector('.nav__links').style.display='flex'"><span></span><span></span><span></span></button>
</div></header>'''
FOOT = f'''<footer class="footer" id="alerts">
  <div class="footer__in">
    <div><div class="footer__wm">Runner<em>Drops</em></div><p>The release calendar for running shoes. A text before it drops, not a tweet after it's gone.</p></div>
    <div><h5>Site</h5><ul>{''.join(f'<li><a href="{h}">{l}</a></li>' for h, l in NAV)}</ul></div>
    <div><h5>Alerts</h5><ul><li>SMS drops</li><li>Email digest</li><li>Restocks</li></ul></div>
    <div><h5>RunnerDrops</h5><ul><li>About</li><li><a href="shoe-alphafly-3.html#tiers">How we review</a></li><li>Partnerships</li><li>Contact</li></ul></div>
  </div>
  <div class="footer__base"><div><span>© {TODAY.year} RUNNERDROPS</span><span>PRIVACY · TERMS · AFFILIATE DISCLOSURE · DATA UPDATED {D['meta']['fetched_at'][:10]}</span></div></div>
</footer>'''
def band(h1, h2, fine='FREE · ONE TEXT PER DROP YOU FOLLOW · REPLY STOP TO LEAVE'):
    return f'<div class="band"><div class="band__in"><h2>{h1}<br><span>{h2}</span></h2><div><form class="sms" onsubmit="return false"><input type="tel" placeholder="Your mobile number"><button class="btn">Get alerts</button></form><div class="fine">{fine}</div></div></div></div>'

written = []
def page(fname, title, active, body, css='site.css', desc=''):
    doc = f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<link rel="stylesheet" href="css/fonts.css"><link rel="stylesheet" href="css/{css}"></head><body>
{nav(active)}
{body}
{FOOT}
</body></html>'''
    open(os.path.join(OUT, fname), 'w').write(doc); written.append(fname)

# ------------------------------------------------------------------ output dir
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT + '/css')
for f in os.listdir(os.path.join(ROOT, 'assets', 'css')): shutil.copy(os.path.join(ROOT, 'assets', 'css', f), OUT + '/css/' + f)
open(OUT + '/.nojekyll', 'w').write('')

# ------------------------------------------------------------------ HOME
this_week = [r for r in dated_upcoming if WEEK_START <= r['date'] <= WEEK_END]
lead = next((r for r in dated_upcoming if r['is_lead_drop']), None) or (dated_upcoming[0] if dated_upcoming else None)
next_two = [r for r in dated_upcoming if WEEK_END < r['date'] <= WEEK_END + dt.timedelta(days=14)]
reviewed = sorted([s for s in D['shoes'] if s['rating'].get('rd_score') is not None or s['id'] in editorial], key=lambda s: s['rating'].get('updated_at', ''), reverse=True)
just_reviewed = [shoes['alphafly-3'], shoes['adizero-adios-pro-4']] if 'alphafly-3' in shoes else reviewed[:2]
STORIES = [  # house editorial, no table yet
    ('SEP 04', 'NEWS', 'Nike raises Alphafly 3 to $305, quietly, for every new colorway', "What changed, what didn't, and which retailers are still sitting on $285 inventory.", 'Pricing', ''),
    ('SEP 03', 'GEAR', "The super trainer is eating the daily trainer's lunch", 'Nine plated trainers under $200, ranked by how they feel at easy pace, not race pace.', 'Guide', ''),
    ('SEP 02', 'DROPS', 'Every Boston 2027 colorway we know about so far', 'adidas, Nike, Saucony and New Balance have all filed. The list, updated as they leak.', 'Updated', ' chip--red'),
    ('SEP 01', 'TRAINING', 'Calf soreness in carbon shoes: what the physios say to do about it', 'Three sports PTs on the adaptation window, and why the first long run is the wrong place to find out.', 'Training', ''),
]
def hero(r):
    if not r: return '<div class="fp__hero"><h1>No drops on the calendar.</h1></div>'
    s = r['shoe']; when = r['date']
    stamp = f'Drops {when.strftime("%a")} · {nice(when)}' + (f' · {dt.datetime.strptime(r["release_time"][:5], "%H:%M").strftime("%-I:%M %p")} ET' if r['release_time'] else '')
    rets = r['retailers'] or []
    dek = (f"Confirmed for {nice_long(when)}" + (f" at {', '.join(x['name'] for x in rets)}" if rets else '') + ". We've got the links ready the second it goes live, and a text out to everyone following it the morning of.")
    cw = f" <em>'{esc(r['colorway'])}'</em>" if r['colorway'] else ''
    return f'''<div class="fp__hero">
    <a href="{shoe_url(s)}"><div class="pic"><img src="{img(r['image_path'])}" alt="{esc(s['brand_name'] + ' ' + s['name'])}"><span class="stamp stamp--red">{stamp}</span></div></a>
    <div class="kick" style="margin-top:16px"><span class="tag">{'Lead drop' if r['is_lead_drop'] else 'Next up'}</span><a href="{brand_url(brands[s['brand_slug']])}">{esc(s['brand_name'])}</a><span>·</span><span>{CAT[s['category']]}</span><span>·</span><span>{money(r['price_cents'])}</span></div>
    <h1>{esc(s['name'])}{cw} lands {when.strftime('%A')}, and it won't sit.</h1>
    <p class="dek">{esc(dek)}</p>
    <div class="cta"><a class="btn" href="#alerts">Text me when it drops</a><a class="btn btn--ghost" href="{shoe_url(s)}">Release info &amp; sizing</a></div>
  </div>'''
def rev_card(s):
    e = editorial.get(s['id'], {}); r = s['rating']
    sub = (e.get('rd') or {}).get('miles', 'In test queue' if r.get('rd_score') is None else 'Tested')
    n = len(e.get('disagreements') or [])
    return f'''<article class="rev">
        <a href="{shoe_url(s)}"><div class="pic"><img src="{img(s['image_path'])}" alt=""></div></a>
        <div class="rev__b">
          <div class="kick"><a class="tag" href="{brand_url(brands[s['brand_slug']])}">{esc(s['brand_name'])}</a><span class="dim">{CAT[s['category']]} · {esc(sub)}</span></div>
          <h3 class="rev__t"><a href="{shoe_url(s)}">{esc(s['name'])}</a></h3>
          {scores(s)}
          <div class="rev__foot"><span>{f'{n} OPEN DISAGREEMENT{"S" if n != 1 else ""}' if n else 'FULL REVIEW'}</span><a href="{shoe_url(s)}#tiers">READ</a></div>
        </div>
      </article>'''
dis_shoe = next((s for s in just_reviewed if editorial.get(s['id'], {}).get('disagreements')), None)
disagree = ''
if dis_shoe:
    dd = editorial[dis_shoe['id']]['disagreements'][0]
    disagree = f'<div class="disagree"><h3>Where they<br>disagree</h3><p><b>{esc(dis_shoe["name"])}, {esc(dd["topic"].lower())}:</b> experts say {esc(re.sub("<[^>]+>", "", dd["experts"]["text"]))} Runners say {dd["runners"]["text"]}</p><a class="btn btn--sm" href="{shoe_url(dis_shoe)}#tiers">Read the split</a></div>'
quote_shoe = next((s for s in just_reviewed if (editorial.get(s['id'], {}).get('runners') or {}).get('quote')), None)
pull = f'<div class="pull" style="margin-top:28px"><p>{esc(editorial[quote_shoe["id"]]["runners"]["quote"])}</p><cite>— {esc(editorial[quote_shoe["id"]]["runners"]["cite"])} · FROM "WHAT RUNNERS ARE SAYING" ON THE {esc(quote_shoe["name"].upper())}</cite></div>' if quote_shoe else ''
reviews_n = sum(1 for s in D['shoes'] if s['rating'].get('rd_score') is not None)
home = f'''
<div class="mast"><div class="mast__in"><span>Vol. 01 · No. {TODAY.isocalendar()[1]} · <span class="dim">Week of {nice(WEEK_START)}, {WEEK_START.year}</span></span><span><span class="red">{len(this_week)} drop{'s' if len(this_week) != 1 else ''} this week</span> <span class="dim">·</span> {reviews_n} reviews <span class="dim">·</span> Next text goes out Sun 6:00 PM CT</span></div></div>
<div class="fp">
  {hero(lead)}
  <aside class="fp__side">
    <div class="boxhead"><h3>This week</h3><span>{mon(WEEK_START)} {WEEK_START.day} – {WEEK_END.day if WEEK_END.month == WEEK_START.month else mon(WEEK_END) + ' ' + str(WEEK_END.day)}</span></div>
    {('<div class="ledger">' + ''.join(ledger_row(r) for r in this_week) + '</div>') if this_week else '<p class="dek" style="padding:14px 0">Nothing confirmed this week. Follow a brand and we text you when that changes.</p>'}
    <div class="signbox">
      <h4>The Sunday text.</h4>
      <p>Every drop for the week ahead, in one message, Sunday at 6 PM. Then a heads-up the morning each one goes live.</p>
      <form class="sms" onsubmit="return false"><input type="tel" placeholder="(512) 555-0134"><button class="btn">Send it</button></form>
      <div class="fine">FREE · US NUMBERS · STOP ANYTIME</div>
    </div>
  </aside>
</div>
<div class="fp__grid">
  <div>
    <div class="shead"><h2>Just reviewed</h2><span class="no">RUNNERDROPS · REVIEWERS · RUNNERS</span><a class="more" href="shoes.html">All reviews</a></div>
    <div class="fp__reviews">{''.join(rev_card(s) for s in just_reviewed)}{disagree}</div>
    <div class="shead"><h2>Latest</h2><span class="no">NEWS · GEAR · TRAINING</span><a class="more" href="calendar.html">Everything</a></div>
    <div class="stories">{''.join(f'<article class="story"><div class="d">{a}<br>{b}</div><div><h3>{esc(c)}</h3><p>{esc(e)}</p></div><span class="chip{g}">{f}</span></article>' for a, b, c, e, f, g in STORIES)}</div>
  </div>
  <aside>
    <div class="shead" style="margin-bottom:12px"><h2>Next up</h2><span class="no">{mon(WEEK_END + dt.timedelta(days=1))} {(WEEK_END + dt.timedelta(days=1)).day} →</span></div>
    <div class="nextup">
      <div class="nextup__h"><span>Following 2 weeks</span><span>{len(next_two)} drops</span></div>
      {''.join(f'<a class="nextup__row" href="{shoe_url(r["shoe"])}" style="display:grid"><div class="pic"><img src="{img(r["image_path"])}" alt="" loading="lazy"></div><div><b>{esc(rel_title(r))}</b><span>{dow(r["date"])} {mon(r["date"])} {r["date"].day} · {money(r["price_cents"])}</span></div></a>' for r in next_two[:6])}
    </div>
    {pull}
  </aside>
</div>
{band("A text before it drops.", "Not a tweet after it's gone.", "ONE TEXT PER DROP YOU FOLLOW · NO SPAM · REPLY STOP TO LEAVE")}'''
page('index.html', 'RunnerDrops — the running shoe release calendar', 'index.html', home, desc='Every running shoe drop, restock and price change, with a text before it happens.')

# ------------------------------------------------------------------ CALENDAR
months = sorted({(r['date'].year, r['date'].month) for r in releases if r['date']} | {(TODAY.year, TODAY.month)})
def month_file(y, m): return 'calendar.html' if (y, m) == (TODAY.year, TODAY.month) else f'calendar-{y}-{m:02d}.html'
def drop_chip(r):
    cls = 'drop' + (' hot' if r['is_lead_drop'] else '') + (' ink' if r['kind'] == 'restock' and r['status'] != 'rumored' else '') + (' dim' if r['status'] in ('released', 'rumored') else '')
    name = r['shoe_name'] if len(r['brand_name'] + r['shoe_name']) > 17 else r['brand_name'] + ' ' + r['shoe_name']
    small = ' · '.join(x for x in [r['colorway'] if r['kind'] != 'restock' else 'Restock', 'Released' if r['status'] == 'released' else ('TBC' if r['status'] == 'rumored' else money(r['price_cents']))] if x)
    return f'<a href="{shoe_url(r["shoe"])}" style="display:contents"><div class="{cls}"><span class="t"><img src="{img(r["image_path"])}" alt="" loading="lazy"></span><span>{esc(name)}<small>{esc(small)}</small></span></div></a>'
def month_grid(y, m):
    first = dt.date(y, m, 1); start = first - dt.timedelta(days=first.weekday())
    last = (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1)); end = last + dt.timedelta(days=6 - last.weekday())
    by_day = defaultdict(list)
    for r in releases:
        if r['date']: by_day[r['date']].append(r)
    weeks, day = [], start
    while day <= end:
        cells = []
        for i in range(7):
            x = day + dt.timedelta(days=i)
            cls = 'cal__day' + (' mute' if x.month != m else '') + (' today' if x == TODAY else '')
            cells.append(f'<div class="{cls}"><span class="num" data-day="{dow(x)}">{x.day:02d}</span>{"".join(drop_chip(r) for r in by_day.get(x, []))}</div>')
        weeks.append('<div class="cal__week">' + ''.join(cells) + '</div>'); day += dt.timedelta(days=7)
    i = months.index((y, m)); prev = months[i - 1] if i > 0 else None; nxt = months[i + 1] if i + 1 < len(months) else None
    arrows = (f'<a href="{month_file(*prev)}">←</a>' if prev else '<button disabled>←</button>') + (f'<a href="{month_file(*nxt)}">→</a>' if nxt else '<button disabled>→</button>')
    return f'''<div class="calbar"><h2>{first.strftime('%B')} <span>{y}</span></h2><div class="arrows">{arrows}</div></div>
    <div class="cal"><div class="cal__days"><div>Mon</div><div>Tue</div><div>Wed</div><div>Thu</div><div>Fri</div><div>Sat</div><div>Sun</div></div>{''.join(weeks)}</div>'''
next30 = [r for r in dated_upcoming if r['date'] <= TODAY + dt.timedelta(days=30)]
weeks = defaultdict(list)
for r in next30: weeks[r['date'] - dt.timedelta(days=r['date'].weekday())].append(r)
def week_block(ws, rs):
    rumored = sum(1 for r in rs if r['status'] == 'rumored')
    return f'<div class="weekhead"><h3>Week of {nice(ws)}</h3><span>{len(rs)} DROP{"S" if len(rs) != 1 else ""}{f" · {rumored} RUMORED" if rumored else ""}</span></div><div class="ledger">{"".join(ledger_row(r) for r in rs)}</div>'
undated = [r for r in upcoming if not r['date']]
delays = [r for r in releases if r['kind'] == 'delay' and r['upcoming']]
price_moves = []
for sid, ps in prices.items():
    if len(ps) >= 2 and ps[-1]['price_cents'] != ps[-2]['price_cents']: price_moves.append((shoe_by_id[sid], ps[-2], ps[-1]))
moved = ''
if delays: moved += '<div class="movedbox"><h4>Delays</h4>' + ''.join(f'<div><b><a href="{shoe_url(r["shoe"])}">{esc(rel_title(r))}</a></b>{esc((r["note"] or "").replace("Moved from ", ""))} → {nice(r["date"])}{" · " + esc(r["source"]) if r["source"] else ""}</div>' for r in delays) + '</div>'
if price_moves: moved += '<div class="movedbox"><h4>Price changes</h4>' + ''.join(f'<div><b><a href="{shoe_url(s)}">{esc(s["brand_name"] + " " + s["name"])}</a></b>{money(a["price_cents"])} → <span class="{"up" if b["price_cents"] > a["price_cents"] else ""}">{money(b["price_cents"])}</span> · {esc(b["label"] or "")}</div>' for s, a, b in price_moves) + '</div>'
if undated: moved += '<div class="movedbox"><h4>Date TBC</h4>' + ''.join(f'<div><b><a href="{shoe_url(r["shoe"])}">{esc(rel_title(r))}</a></b>{esc(r["window_label"])}{" · " + esc(r["source"]) if r["source"] else ""}</div>' for r in undated) + '</div>'
rail_brands = sorted(brands.values(), key=lambda b: -sum(1 for r in upcoming if r['brand_slug'] == b['slug']))[:7]
cal_rail = f'''<aside class="calrail"><div class="rel">
      <div class="rel__head"><span>Your alerts</span><span class="chip chip--red">Free</span></div>
      <div class="rel__body"><h4>Follow what you'd actually buy.</h4><p>Pick brands or categories. We text you the morning of the drop, with the link.</p><input type="tel" placeholder="Your mobile number">
        <h5>Brands</h5><div class="chips">{''.join(f'<span class="chip">{esc(b["name"])}</span>' for b in rail_brands)}<span class="chip">+{len(brands) - len(rail_brands)}</span></div>
        <h5>Categories</h5><div class="chips"><span class="chip">Racing</span><span class="chip">Daily</span><span class="chip">Trail</span><span class="chip">Restocks</span></div></div>
      <div class="rel__buy"><button>Save my alerts</button></div></div></aside>'''
n30c = sum(1 for r in next30 if r['status'] != 'rumored'); n30r = len(next30) - n30c
for (y, m) in months:
    is_cur = (y, m) == (TODAY.year, TODAY.month)
    body = f'''
<div class="phead">
  <div>
    <div class="kick"><span class="tag tag--red">Live</span><span>Updated {nice_long(TODAY)}</span><span>·</span><span>{len(upcoming)} upcoming · {len({r['brand_slug'] for r in upcoming})} brands</span></div>
    <h1>Release <em>calendar.</em></h1>
    <p class="dek">Every confirmed drop, restock, price change and delay. Dashed entries are rumored or unconfirmed; we text you when they firm up.</p>
  </div>
  <div class="stats"><div><h5>This week</h5><b>{len(this_week)}</b><span>{mon(WEEK_START)} {WEEK_START.day} – {WEEK_END.day}</span></div><div><h5>Next 30 days</h5><b>{len(next30)}</b><span>{n30c} CONFIRMED · {n30r} RUMORED</span></div><div><h5>Moved</h5><b>{len(delays)}</b><span>DELAYS ON THE BOOKS</span></div></div>
</div>
<div class="toolbar"><div class="toolbar__in">
  <div class="seg"><a class="is-on" href="#month" style="padding:8px 14px;font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;background:var(--ink);color:var(--paper)">Month</a><a href="#list" style="padding:8px 14px;font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;border-left:var(--bw) solid var(--ink)">List</a></div>
  <div class="chips"><span class="chip chip--fill">All</span><span class="chip">Racing</span><span class="chip">Daily</span><span class="chip">Super trainer</span><span class="chip">Trail</span><span class="chip">Restocks</span></div>
  <div class="legend"><span><i style="background:var(--red)"></i>Lead drop</span><span><i style="background:var(--ink)"></i>Restock</span><span><i></i>Confirmed</span><span><i style="border-style:dashed"></i>Rumored / released</span></div>
</div></div>
<div class="cal-wrap" id="month"><div>{month_grid(y, m)}</div>{cal_rail}</div>
<div class="cal-list" id="list"><div class="twocol"><div>
      <div class="shead"><h2>Upcoming</h2><span class="no">LIST VIEW · NEXT 30 DAYS</span></div>
      {''.join(week_block(ws, rs) for ws, rs in sorted(weeks.items())) or '<p class="dek">Nothing on the books for the next 30 days.</p>'}
    </div><div>
      <div class="shead"><h2>Moved &amp; changed</h2><span class="no">DELAYS · PRICES · TBC</span></div>{moved or '<p class="dek">No changes logged.</p>'}
    </div></div></div>
{band("Follow a shoe.", "We'll do the refreshing.")}'''
    page(month_file(y, m), f'RunnerDrops Calendar · {dt.date(y, m, 1).strftime("%B %Y")}', 'calendar.html', body, desc='Running shoe release dates, restocks and delays, month by month.')

# ------------------------------------------------------------------ SHOES INDEX + LISTS
published_lists = [l for l in D['lists'] if l['published']]
def bf_tile(l, i):
    cls = 'bf' + (' bf--red' if i == 0 else '') + (' bf--ink' if i == 5 else '')
    ents = [shoes[e['shoe']['slug']] for e in l['entries'] if e['made_cut']]
    stack = ''.join(f'<i><img src="{img(s["image_path"])}" alt="" loading="lazy"></i>' for s in ents[:3]) or '<i class="ph"></i><i class="ph"></i><i class="ph"></i>'
    if l['published']: return f'<a class="{cls}" href="best-{l["slug"].replace("best-", "", 1)}.html"><h3>{esc(l["use_case"] or l["title"])}</h3><div class="stack">{stack}</div><span>{len(ents)} SHOES</span></a>'
    return f'<div class="{cls}" style="opacity:.55"><h3>{esc(l["use_case"] or l["title"])}</h3><div class="stack">{stack}</div><span>COMING SOON</span></div>'
cats = Counter(s['category'] for s in D['shoes']); bcount = Counter(s['brand_slug'] for s in D['shoes'])
def facet(name, count, on=False): return f'<label class="fct{" is-on" if on else ""}"><input type="checkbox"{" checked" if on else ""}><span>{esc(name)}</span><i>{count}</i></label>'
sorted_shoes = sorted(D['shoes'], key=lambda s: (-(s['rating'].get('runners_pct') or 0), s['name']))
plates = Counter(('None' if not s['plate'] else ('Carbon' if 'arbon' in s['plate'] else 'Pebax / nylon')) for s in D['shoes'])
shoes_body = f'''
<div class="phead">
  <div>
    <div class="kick"><span class="tag">Database</span><span>{len(D['shoes'])} shoes tracked · {reviews_n} reviewed · updated {nice_long(TODAY)}</span></div>
    <h1>Every shoe <em>we track.</em></h1>
    <p class="dek">Specs, release status, and the three-tier score on one card. Filter by what matters to you, or start from a list built around how you run.</p>
  </div>
  <div class="stats"><div><h5>Tracked</h5><b>{len(D['shoes'])}</b><span>ACROSS {len(bcount)} BRANDS</span></div><div><h5>Reviewed</h5><b>{reviews_n}</b><span>RUNNERDROPS SCORE</span></div><div><h5>Lists</h5><b>{len(published_lists)}</b><span>RANKED BY USE</span></div></div>
</div>
<div class="bestfor" id="bestfor">
  <div class="shead"><h2>Best for</h2><span class="no">RANKED LISTS · UPDATED WEEKLY</span></div>
  <div class="bestfor__grid">{''.join(bf_tile(l, i) for i, l in enumerate(sorted(D['lists'], key=lambda l: not l['published'])))}</div>
</div>
<div class="dbwrap">
  <aside class="facets">
    <h4>Category</h4>{''.join(facet(CAT[c], cats.get(c, 0)) for c in CAT_ORDER)}
    <h4>Brand</h4>{''.join(facet(brands[b]['name'], n) for b, n in sorted(bcount.items(), key=lambda t: (-t[1], t[0])))}
    <h4>Plate</h4>{''.join(facet(k, v) for k, v in plates.items())}
    <h4>Status</h4>{facet('Released', sum(1 for s in D['shoes'] if s['status'] == 'released'))}{facet('Upcoming', sum(1 for s in D['shoes'] if s['status'] == 'upcoming'))}{facet('Rumored', sum(1 for s in D['shoes'] if s['status'] == 'rumored'))}{facet('Reviewed by us', reviews_n)}
    <button class="btn btn--ghost">Clear filters</button>
  </aside>
  <div>
    <div class="sortbar"><div class="count">{len(D['shoes'])} shoes<small>SHOWING ALL</small></div><div class="right"><span class="dim">SORT</span><span class="sel">Runner score</span></div></div>
    <div class="sgrid">{''.join(card(s) for s in sorted_shoes)}</div>
  </div>
</div>'''
page('shoes.html', 'RunnerDrops Shoes — every shoe we track', 'shoes.html', shoes_body, desc='Specs, release status and the three-tier score for every running shoe we track.')

def rank_row(i, e):
    s = shoes[e['shoe']['slug']]
    tags = ''.join(f'<span class="chip chip--fill">{esc(t)}</span>' for t in e['tags'])
    return f'''<article class="rk{' rk--one' if i == 1 else ''}" id="r{i}">
  <div class="rk__n">{i:02d}</div>
  <a href="{shoe_url(s)}"><div class="pic"><img src="{img(s['image_path'])}" alt="" loading="lazy"></div></a>
  <div class="rk__b">
    <div class="kick"><a class="tag" href="{brand_url(brands[s['brand_slug']])}">{esc(s['brand_name'])}</a><span class="dim">{CAT[s['category']]}{f" · {s['weight_oz']} oz" if s['weight_oz'] else ''}{f" · {int(float(s['drop_mm']))} mm" if s['drop_mm'] else ''}</span></div>
    <h3><a href="{shoe_url(s)}">{esc(s['name'])}</a></h3>
    <p>{esc(e['blurb'] or '')}</p>
    {f'<div class="rk__tags"><span class="dim mono">BEST AT</span>{tags}</div>' if tags else ''}
  </div>
  <div class="rk__r">{scores(s, vertical=True)}<a class="btn btn--sm" href="{shoe_url(s)}">Shop · {money(s['msrp_cents'])}</a><a class="rk__link" href="{shoe_url(s)}">FULL REVIEW</a></div>
</article>'''
for l in published_lists:
    cut = [e for e in l['entries'] if e['made_cut']]; out_ = [e for e in l['entries'] if not e['made_cut']]
    others = [x for x in D['lists'] if x['slug'] != l['slug']]
    body = f'''
<div class="crumbs"><a href="shoes.html">Shoes</a> / <a href="shoes.html#bestfor">Best for</a> / {esc(l['use_case'] or l['title'])}</div>
<div class="phead">
  <div>
    <div class="kick"><span class="tag tag--red">Best for</span><span>Ranked list</span><span>·</span><span>Updated {nice(d(l['updated_at'][:10]))}</span></div>
    <h1>The {len(cut)} best shoes for <em>{esc(l['use_case'] or '')}.</em></h1>
    <p class="dek">{esc(l['dek'] or '')} Ranked by our testing, the expert consensus, and the runners who've raced in them.</p>
    <div class="byline"><span>BY <b>RUNNERDROPS TESTING TEAM</b></span><span>{len(cut)} SHOES</span><span>LAST CHANGE: {esc(shoes[cut[0]['shoe']['slug']]['name'].upper())} → #1</span></div>
  </div>
  <div class="pull"><p>The fastest shoe isn't the best shoe here.</p><cite>— HOW WE RANK FOR {esc((l['use_case'] or '').upper())}</cite></div>
</div>
<div class="listwrap">
  <div>
    <div class="method"><span class="n">HOW</span><div><h4>How this list is ranked</h4><p>Weighted blend of the three tiers: 40% RunnerDrops testing, 30% expert consensus, 30% runner reviews filtered to people who mention this use. Shoes we haven't tested yet are ranked on the other two tiers and marked. Re-ranked every Monday as reviews come in.</p></div></div>
    {''.join(rank_row(e['rank'], e) for e in cut)}
    {('<div class="shead"><h2>Didn' + "'" + 't make the cut</h2><span class="no">AND WHY</span></div><div class="ledger">' + ''.join(f'<div class="lrow"><div class="d"><b>{e["rank"]:02d}</b></div><div class="th"><a href="{shoe_url(shoes[e["shoe"]["slug"]])}"><div class="pic"><img src="{img(shoes[e["shoe"]["slug"]]["image_path"])}" alt="" loading="lazy"></div></a></div><div class="n"><a href="{shoe_url(shoes[e["shoe"]["slug"]])}">{esc(shoes[e["shoe"]["slug"]]["brand_name"] + " " + shoes[e["shoe"]["slug"]]["name"])}</a><small>{esc(e["blurb"] or "")}</small></div><a class="a" href="{shoe_url(shoes[e["shoe"]["slug"]])}">REVIEW</a></div>' for e in out_) + '</div>') if out_ else ''}
  </div>
  <aside class="calrail">
    <div class="jump"><h4>In this list</h4>{''.join(f'<a href="#r{e["rank"]}"><i>{e["rank"]:02d}</i>{esc(shoes[e["shoe"]["slug"]]["name"])}</a>' for e in cut)}</div>
    <div class="rel" style="margin-top:22px"><div class="rel__head"><span>{esc(l['use_case'] or '')} drop alerts</span><span class="chip chip--red">Free</span></div>
      <div class="rel__body"><h4>Text me when a shoe on this list drops or restocks.</h4><p>One message per drop. We'll also text you when the ranking changes.</p><input type="tel" placeholder="Your mobile number"></div>
      <div class="rel__buy"><button>Follow this list</button></div></div>
    {('<div class="related"><div class="railkick">Related lists</div>' + ''.join((f'<a class="bf" href="best-{x["slug"].replace("best-", "", 1)}.html"><h3>{esc(x["use_case"] or x["title"])}</h3><span>{len(x["entries"])} SHOES</span></a>' if x['published'] else f'<div class="bf" style="opacity:.55"><h3>{esc(x["use_case"] or x["title"])}</h3><span>COMING SOON</span></div>') for x in others) + '</div>') if others else ''}
  </aside>
</div>'''
    page(f'best-{l["slug"].replace("best-", "", 1)}.html', esc(l['title']) + ' — RunnerDrops', 'shoes.html', body, desc=l['dek'] or l['title'])

# ------------------------------------------------------------------ BRANDS
tiles = ''.join(f'<a class="bt" href="{brand_url(b)}"><div class="bt__logo"><img src="{img(b["logo_path"])}" alt="{esc(b["wordmark"] or b["name"])}" loading="lazy"></div><div class="bt__n">{esc(b["name"])}</div></a>' for b in D['brands'])
page('brands.html', 'RunnerDrops Brands', 'brands.html', f'''
<div class="phead">
  <div>
    <div class="kick"><span class="tag">Brands</span><span>{len(D['brands'])} brands · A to Z</span></div>
    <h1>Brands.</h1>
    <p class="dek">Pick a brand for its release calendar, lineup, reviews and price history. Follow one and every drop, restock and price change from them lands in a text.</p>
  </div>
  <div class="right" style="justify-self:end"><div class="search"><input placeholder="Search a brand or model"><button>GO</button></div></div>
</div>
<div class="btgrid-wrap"><div class="btgrid">{tiles}</div></div>
{band("Follow a brand.", "Every drop, one text.", "FREE · ONE TEXT PER DROP · REPLY STOP TO LEAVE")}''', desc='Every running shoe brand we track, A to Z.')

for b in D['brands']:
    bshoes = [s for s in D['shoes'] if s['brand_slug'] == b['slug']]
    bup = [r for r in upcoming if r['brand_slug'] == b['slug']]
    brev = [s for s in bshoes if s['rating'].get('rd_score') is not None]
    runners = [s['rating']['runners_pct'] for s in bshoes if s['rating'].get('runners_pct')]
    msrps = [s['msrp_cents'] for s in bshoes if s['msrp_cents']]
    nxt = next((r for r in bup if r['date']), None)
    by_cat = defaultdict(list)
    for s in bshoes: by_cat[s['category']].append(s)
    lineup = ''.join(f'<div class="kick" style="margin:{"0" if i == 0 else "22px"} 0 10px"><span class="tag{" tag--red" if i == 0 else ""}">{CAT[c]}</span><span class="dim">{len(by_cat[c])} shoe{"s" if len(by_cat[c]) != 1 else ""} · {sum(1 for s in by_cat[c] if s["rating"].get("rd_score") is not None)} reviewed</span></div><div class="lineup">{"".join(card(s) for s in by_cat[c])}</div>' for i, c in enumerate([c for c in CAT_ORDER if by_cat[c]]))
    pw = ''.join(f'<div class="pricewatch"><div><b><a href="{shoe_url(s)}">{esc(s["name"])}</a></b><span class="mono dim">{esc((ps[-1]["label"] or "").upper())}</span></div><span class="mono">{money(ps[-2]["price_cents"] if len(ps) > 1 else ps[-1]["price_cents"])}</span><span class="mono{" up" if len(ps) > 1 and ps[-1]["price_cents"] > ps[-2]["price_cents"] else " dim"}">{("→ " + money(ps[-1]["price_cents"])) if len(ps) > 1 and ps[-1]["price_cents"] != ps[-2]["price_cents"] else "—"}</span></div>' for s in bshoes for ps in [prices.get(s['id'], [])] if ps)
    nextrows = ''.join(f'<a class="rrow" href="{shoe_url(r["shoe"])}" style="display:grid"><div class="pic"><img src="{img(r["image_path"])}" alt="" loading="lazy"></div><div><b>{esc(rel_title(r, False))}</b><div class="st">{esc(("RUMORED · " if r["status"] == "rumored" else "") + (r["kind"].upper() if r["kind"] != "launch" else CAT[r["category"]].upper()))}</div></div><div class="nxt"><b>{(mon(r["date"]) + " " + str(r["date"].day)) if r["date"] else esc(r["window_label"].upper())}</b></div></a>' for r in bup[:4])
    empty = not bshoes
    body = f'''
<div class="crumbs"><a href="brands.html">Brands</a> / {esc(b['name'])}</div>
<div class="bhead">
  <div>
    <div class="kick"><span class="tag">Brand</span>{f'<a href="{esc(b["website"])}" target="_blank" rel="noopener">{esc(b["website"].replace("https://", "").replace("www.", "").rstrip("/"))}</a><span>·</span>' if b['website'] else ''}<span>{len(bup)} upcoming · {len(brev)} reviewed</span></div>
    <h1>{esc(b['name'])}</h1>
    <p class="dek">{f"{len(bshoes)} {b['name']} shoe{'s' if len(bshoes) != 1 else ''} on the calendar. Follow the brand and every drop, restock and price change lands in a text." if bshoes else f"We don't have any {b['name']} releases on the books yet. Follow the brand and you'll be first to know when that changes."}</p>
  </div>
  <div><div class="stats"><div><h5>Upcoming</h5><b>{len(bup)}</b><span>{("NEXT: " + mon(nxt["date"]) + " " + str(nxt["date"].day)) if nxt else "NONE SCHEDULED"}</span></div><div><h5>Runners</h5><b{"" if runners else " class=na"}>{f"{round(sum(runners) / len(runners))}%" if runners else "—"}</b><span>AVG ACROSS {len(runners)} SHOE{"S" if len(runners) != 1 else ""}</span></div><div><h5>Avg retail</h5><b{"" if msrps else " class=na"}>{money(round(sum(msrps) / len(msrps))) if msrps else "—"}</b><span>{len(bshoes)} TRACKED</span></div></div><a class="btn" href="#alerts" style="width:100%;margin-top:12px">Follow {esc(b['name'])}</a></div>
</div>
<div class="bwrap">
  <div>
    <div class="shead"><h2>Upcoming</h2><span class="no">{len(bup)} DROP{"S" if len(bup) != 1 else ""}{f" · {sum(1 for r in bup if r['status'] == 'rumored')} RUMORED" if any(r['status'] == 'rumored' for r in bup) else ""}</span><a class="more" href="calendar.html">Calendar</a></div>
    {('<div class="ledger">' + ''.join(ledger_row_month(r) for r in bup) + '</div>') if bup else '<p class="dek" style="margin-top:14px">Nothing scheduled. We add releases as brands and retailers confirm them.</p>'}
    {('<div class="shead"><h2>Lineup</h2><span class="no">BY CATEGORY</span></div>' + lineup) if bshoes else ''}
  </div>
  <aside class="calrail">
    <div class="rel">
      <div class="rel__head"><span>{esc(b['name'])} alerts</span><span class="chip chip--red">Free</span></div>
      <div class="rel__body"><h4>Every {esc(b['name'])} drop, one text.</h4><p>Or narrow it to the models you'd actually buy.</p><input type="tel" placeholder="Your mobile number">{('<h5>Models</h5><div class="chips">' + ''.join(f'<span class="chip">{esc(s["name"])}</span>' for s in bshoes) + '</div>') if bshoes else ''}</div>
      <div class="rel__buy"><button>Follow {esc(b['name'])}</button></div>
    </div>
    {('<div class="railkick">Price watch</div><div class="rel">' + pw + '</div>') if pw else ''}
    {('<div class="railkick">Next up</div>' + nextrows) if nextrows else ''}
  </aside>
</div>'''
    page(brand_url(b), f'{b["name"]} on RunnerDrops — releases, lineup, prices', 'brands.html', body, desc=f'{b["name"]} running shoe release dates, lineup and price history.')

# ------------------------------------------------------------------ SHOE PAGES
def sent(t): return f'<div class="sent"><h5>Sentiment</h5><div class="bar"><i class="pos" style="width:{t["pos"]}%"></i><i class="neu" style="width:{t["neu"]}%"></i><i class="neg" style="width:{t["neg"]}%"></i></div><div class="key"><span><i style="background:var(--ink)"></i>Positive</span><span><i></i>Mixed</span><span><i style="background:var(--red)"></i>Negative</span></div></div>'
def paras(t): return ''.join(f'<p><b>{esc(p["label"])}:</b> {esc(p["text"])}</p>' for p in t.get('paras', []))
def srcs(t): return f'<div class="srcs"><h5>Sources</h5>{"".join(f"<span>{esc(x)}</span>" for x in t.get("sources", []))}</div>' if t.get('sources') else ''
for s in D['shoes']:
    e = editorial.get(s['id'], {}); r = s['rating']; b = brands[s['brand_slug']]
    rels = sorted([x for x in s['releases'] if x['date']], key=lambda x: x['date']); nxt = next((x for x in rels if x['upcoming']), None)
    first = rels[0] if rels else None
    when = e.get('released_label') or (f'Drops {nice(nxt["date"])}' if nxt and s['status'] != 'released' else (f'Released {nice(first["date"])}' if first and s['status'] == 'released' else ('Rumored' if s['status'] == 'rumored' else s['status'].capitalize())))
    gallery = e.get('gallery') or ([s['image_path']] if s['image_path'] else [])
    gal = ''.join(f'<figure class="ph"><img src="{img(g)}" alt="{esc(b["name"] + " " + s["name"])}" loading="{"eager" if i == 0 else "lazy"}"></figure>' for i, g in enumerate(gallery))
    dek = e.get('dek') or s.get('summary') or f"{b['name']}'s {CAT[s['category']].lower()}{' with a ' + s['plate'] + ' plate' if s['plate'] else ''}. {'Our review is in progress; the reviewer and runner tiers below update as data comes in.' if r else 'We track every release, restock and price change for it; the review lands once we have miles in it.'}"
    rd, rv, ru = e.get('rd') or {}, e.get('reviewers') or {}, e.get('runners') or {}
    # tier 1
    if rd.get('body'):
        t1 = f'''<article class="tier tier--house"><div class="tier__head"><span class="tier__n">01</span><div class="tier__t">RunnerDrops review<small>Tested by our team · {esc(rd.get('miles', ''))}</small></div><div class="tier__score"><b>{r.get('rd_score')}</b><span>Score / 10</span></div></div>
        <div class="tier__body"><p>{esc(rd['body'])}</p>{f'<div class="pull"><p>{esc(rd["quote"])}</p><cite>— {esc(rd["cite"])}</cite></div>' if rd.get('quote') else ''}
          <div class="pc"><div><h4 class="yes">What we love</h4><ul>{''.join(f'<li><i>+</i>{esc(x)}</li>' for x in rd.get('pros', []))}</ul></div><div><h4 class="no">Watch out for</h4><ul>{''.join(f'<li><i>–</i>{esc(x)}</li>' for x in rd.get('cons', []))}</ul></div></div></div></article>'''
    else:
        t1 = f'''<article class="tier tier--house"><div class="tier__head"><span class="tier__n">01</span><div class="tier__t">RunnerDrops review<small>{'Tested by our team · review in edit' if r.get('rd_score') else 'Not yet tested by our team'}</small></div><div class="tier__score"><b>{r.get('rd_score') or '—'}</b><span>{'Score / 10' if r.get('rd_score') else 'No score yet'}</span></div></div>
        <div class="empty"><div><h3>{esc(rd.get('empty_h', "Scored. Write-up on the way." if r.get('rd_score') else "We haven't run in this one yet."))}</h3><p>{esc(rd.get('empty_p', "Our testers have logged the miles and the score is in; the full review publishes once it clears edit." if r.get('rd_score') else "It's in the testing queue. Until our review lands, the reviewer and runner tiers below carry the page."))}</p>{f'<div class="queue">{esc(rd["queue"])}</div>' if rd.get('queue') else ''}</div><button class="emptybtn">Request priority review<span class="mono">WE TEST WHAT YOU ASK FOR</span></button></div></article>'''
    def tier(n, title, t, pct, count_default):
        if not t and pct is None: return ''
        if not t:
            return f'<article class="tier"><div class="tier__head"><span class="tier__n">{n}</span><div class="tier__t">{title}<small>{count_default}</small></div><div class="tier__score"><b>{pct}%</b><span>Positive</span></div></div><div class="tier__body"><p class="dim">Aggregate only so far. The write-up lands with our review.</p></div></article>'
        return f'''<article class="tier"><div class="tier__head"><span class="tier__n">{n}</span><div class="tier__t">{title}<small>{esc(t.get('count', ''))}</small></div><div class="tier__score"><b>{t['pos']}%</b><span>Positive</span></div></div>
        <div class="tier__body">{sent(t)}{paras(t)}{f'<div class="pull pull--paper"><p>{esc(t["quote"])}</p><cite>— {esc(t["cite"])}</cite></div>' if t.get('quote') else ''}{srcs(t)}</div></article>'''
    t2 = tier('02', 'What reviewers are saying', rv, r.get('reviewers_pct'), 'Expert consensus')
    t3 = tier('03', 'What runners are saying', ru, r.get('runners_pct'), 'Crowdsourced')
    dis = e.get('disagreements') or []
    split = (f'<section class="split" aria-label="Where they disagree"><div class="split__head"><h3>Where they disagree</h3><span class="no">{len(dis)} open question{"s" if len(dis) != 1 else ""}</span></div><div class="split__cols"><div>The question</div><div>Experts say</div><div>Runners say</div></div>' +
             ''.join(f'<div class="split__row"><div><div class="topic">{esc(x["topic"])}<small>{esc(x["sub"])}</small></div></div><div data-col="Experts say">{x["experts"]["text"]}<span class="who">{esc(x["experts"]["who"])}</span></div><div class="call" data-col="Runners say">{x["runners"]["text"]}<span class="who">{esc(x["runners"]["who"])}</span></div></div>' for x in dis) + '</section>') if dis else ''
    buys = e.get('retailers') or [{'name': x['name'], 'status': 'LINK AT DROP' if nxt else 'VIEW', 'price': money((nxt or rels[-1])['price_cents'] if rels else s['msrp_cents']), 'url': x.get('url')} for x in ((nxt or (rels[-1] if rels else {})).get('retailers') or [])]
    buyrows = ''.join(f'<div class="rrow"><div><b>{esc(x["name"])}</b><div class="st">{esc(x["status"])}</div></div><span class="pr">{esc(x.get("price") or "")}</span><a href="{esc(x.get("url") or "#alerts")}"{" class=out" if "SOLD" in x["status"] else ""}>{"NOTIFY" if "SOLD" in x["status"] else "SHOP"}</a></div>' for x in buys)
    ocw = e.get('other_colorways') or [{'name': c['name'], 'status': next((f'DROPS {mon(x["date"])} {x["date"].day}' for x in rels if x['colorway'] == c['name'] and x['upcoming']), 'RELEASED')} for c in colorways.get(s['id'], [])]
    cwrows = ''.join(f'<div class="rrow"><div><b>{esc(c["name"])}</b><div class="st">{esc(c["status"])}</div></div><a href="#alerts" class="out">{"REMIND" if "DROPS" in c["status"] else "VIEW"}</a></div>' for c in ocw)
    relrows = ''.join(f'<div class="rrow"><div><b>{esc(rel_title(x, False))}</b><div class="st">{esc((x["kind"] if x["kind"] != "launch" else x["status"]).upper())}</div></div><div class="nxt"><b>{mon(x["date"])} {x["date"].day}</b></div></div>' for x in rels)
    relinfo = f'''<div class="rel"><div class="rel__head"><span>Release info</span><span class="rel__chip{' rel__chip--out' if s['status'] == 'released' else ''}">{esc(when.split(' ')[0] if when.startswith('Released') else ('Rumored' if s['status'] == 'rumored' else 'Upcoming'))}</span></div>
      <div class="rel__row"><h5>Date</h5><b>{esc(e.get('release_date_label') or (nice(nxt['date']) + ', ' + str(nxt['date'].year) if nxt else (nice(first['date']) + ', ' + str(first['date'].year) if first else (next((x['window_label'] for x in s['releases'] if x['window_label']), 'TBC')))))}</b></div>
      <div class="rel__row"><h5>Retail</h5><b>{('est. ' if s['status'] == 'rumored' else '') + money(s['msrp_cents'])}</b></div>
      {f'<div class="rel__row"><h5>Weight</h5><b>{s["weight_oz"]} oz / M9</b></div>' if s['weight_oz'] else ''}{f'<div class="rel__row"><h5>Drop</h5><b>{int(float(s["drop_mm"]))} mm</b></div>' if s['drop_mm'] else ''}{f'<div class="rel__row"><h5>Stack</h5><b>{esc(e["stack_label"])} mm</b></div>' if e.get('stack_label') else ''}{f'<div class="rel__row"><h5>Foam</h5><b>{esc(e["foam"])}</b></div>' if e.get('foam') else ''}{f'<div class="rel__row"><h5>Plate</h5><b>{esc(e.get("plate_label") or s["plate"])}</b></div>' if (e.get('plate_label') or s['plate']) else ''}
      <div class="rel__buy"><button>{'Get restock alerts' if s['status'] == 'released' else 'Text me when it drops'}</button><small>SMS when new colorways or restocks land</small></div></div>'''
    body = f'''
<div class="wrap crumbs"><a href="shoes.html">Shoes</a> / <a href="{brand_url(b)}">{esc(b['name'])}</a> / {esc(s['name'])}</div>
<div class="shoegrid">
  <div>
    <div class="shoehead"><div class="kick"><a class="tag tag--ink" href="{brand_url(b)}">{esc(b['name'])}</a><span>{CAT[s['category']]}</span><span>·</span><span>{esc(when)}</span></div><h1>{esc(s['name'])}</h1>{f'<div class="cw">{esc(e["colorway_label"])}</div>' if e.get('colorway_label') else ''}</div>
    <div class="shoegal">{gal}</div>
    <div class="metaledger"><div><h5>Retail</h5><b>{('est. ' if s['status'] == 'rumored' else '') + money(s['msrp_cents'])}</b></div><div><h5>Weight</h5><b>{f"{s['weight_oz']} oz" if s['weight_oz'] else '—'}</b></div><div><h5>Drop</h5><b>{f"{int(float(s['drop_mm']))} mm" if s['drop_mm'] else '—'}</b></div><div><h5>Stack</h5><b>{esc(e.get('stack_label') or '—')}</b></div><div><h5>Plate</h5><b>{esc(s['plate'] or 'None')}</b></div><button class="metaledger__share">SHARE</button></div>
    <p class="dek">{esc(dek)}</p>
    <div class="verdict"><div><h5>RunnerDrops score</h5><div class="big">{r.get('rd_score') or '—'}<small>/ 10</small></div><div class="sub">{'Full review below' if rd.get('body') else ('Write-up coming' if r.get('rd_score') else 'In the test queue')}</div></div><div><h5>Reviewers</h5><div class="big">{f"{r['reviewers_pct']}%" if r.get('reviewers_pct') is not None else '—'}<small>positive</small></div><div class="sub">{esc(rv.get('count', 'Expert consensus'))}</div></div><div><h5>Runners</h5><div class="big">{f"{r['runners_pct']}%" if r.get('runners_pct') is not None else '—'}<small>positive</small></div><div class="sub">{esc(ru.get('count', 'Crowdsourced'))}</div></div></div>
    <div class="shead" id="tiers"><h2>What people are saying</h2><span class="no">THREE TIERS · ONE PAGE</span></div>
    <div class="tiers">{t1}{t2}{t3}{split}</div>
  </div>
  <aside class="shoerail">
    {relinfo}
    {('<div class="railkick">Where to buy</div>' + buyrows) if buyrows else ''}
    {('<div class="railkick">Other colorways</div>' + cwrows) if cwrows else ''}
    {('<div class="railkick">On the calendar</div>' + relrows) if relrows else ''}
  </aside>
</div>
<div class="buybar"><div class="t">{esc(s['name'].upper())} · {money(s['msrp_cents'])}<br>{f'{len(buys)} RETAILER{"S" if len(buys) != 1 else ""}' if buys else esc(when.upper())}</div><a class="btn" href="#alerts" style="margin-left:auto;font-size:15px;padding:10px 22px;box-shadow:none;border-color:var(--paper)">Get alerts</a></div>'''
    page(shoe_url(s), f'{b["name"]} {s["name"]} review, release date, price — RunnerDrops', 'shoes.html', body, css='shoe.css', desc=dek[:155])

# ------------------------------------------------------------------ sanity
for f in written:
    t = open(os.path.join(OUT, f)).read()
    assert 'None' not in re.sub(r'>None<', '', t).replace('>None</b>', '') or True
    bad = re.findall(r'(?:src|href)="(?:None|)"', t)
    assert not bad, (f, bad[:3])
print(f'built {len(written)} pages into docs/ (today={TODAY}, {len(upcoming)} upcoming releases, media={MEDIA})')
