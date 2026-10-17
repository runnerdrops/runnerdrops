"""Pull everything the site needs from Supabase into data/data.json.

usage: SUPABASE_URL=https://xxx.supabase.co SUPABASE_KEY=sb_publishable_... python3 tools/fetch_data.py
Both values are public (the key is the publishable/anon key; row-level security does the gating).
Only tables with a public-read policy are readable, so subscriber data can never end up in here.
"""
import os, json, sys, urllib.request, urllib.parse, datetime

URL = os.environ.get('SUPABASE_URL', 'https://ktqligbqigndccaeygvi.supabase.co').rstrip('/')
KEY = os.environ.get('SUPABASE_KEY', 'sb_publishable_Echb1Z1JCnQz80uVzRdA0w_-uT_LBSa')
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'data.json')

def get(table, params):
    q = urllib.parse.urlencode(params, safe='*,().')
    req = urllib.request.Request(f'{URL}/rest/v1/{table}?{q}', headers={'apikey': KEY, 'Authorization': f'Bearer {KEY}'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

data = {
    'meta': {'fetched_at': datetime.datetime.utcnow().isoformat(timespec='seconds') + 'Z',
             'media_base': f'{URL}/storage/v1/object/public/media/'},
    'brands':    get('brands', {'select': '*', 'order': 'sort_name'}),
    'shoes':     get('shoes', {'select': '*,brand:brands(slug,name,wordmark)', 'order': 'name'}),
    'colorways': get('colorways', {'select': '*'}),
    'retailers': get('retailers', {'select': '*'}),
    'releases':  get('v_calendar', {'select': '*', 'order': 'release_date.asc.nullslast,release_time.asc.nullslast'}),
    'ratings':   get('shoe_ratings', {'select': '*'}),
    'editorial': get('shoe_editorial', {'select': '*'}),
    'prices':    get('price_history', {'select': '*', 'order': 'shoe_id,observed_on'}),
    'lists':     get('lists', {'select': '*,entries:list_entries(*,shoe:shoes(slug))', 'order': 'title'}),
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(data, open(OUT, 'w'), indent=1, default=str)
print({k: len(v) for k, v in data.items() if isinstance(v, list)}, '->', os.path.relpath(OUT))
