# RunnerDrops.com

Static site, generated from Supabase. Live at **https://runnerdrops.github.io/runnerdrops/**.

```
Supabase (content)  ──fetch_data.py──▶  data/data.json  ──build.py──▶  docs/  ──GitHub Pages──▶  the site
```

A GitHub Action runs that pipeline on every push, every hour, and on demand (**Actions → Build site from Supabase → Run workflow**).
Edit a row in Supabase and the site follows within the hour; press Run workflow to make it follow now.

## Layout

| Path | What it is |
|---|---|
| `build.py` | The generator. Layout and framing copy only; all content comes from `data/data.json`. |
| `tools/fetch_data.py` | Pulls brands, shoes, releases, ratings, editorial, prices and lists from Supabase (publishable key; RLS limits it to public tables). |
| `data/data.json` | The last snapshot fetched. Committed so a build is reproducible and reviewable in a diff. |
| `assets/css/` | Design system: `fonts.css` (embedded Oswald / Archivo / JetBrains Mono), `site.css`, `shoe.css`. |
| `supabase/` | Schema migrations and seed SQL. See `supabase/README.md`. |
| `logo-src/` → `logos/` | Brand logos as supplied and the normalized black-on-transparent versions (`tools/make_logos.py`). Uploaded to the `media` bucket under `logos/`. |
| `docs/` | **Generated output.** Do not hand-edit; the next build overwrites it. |

## Pages generated

`index.html` · `calendar.html` (+ one page per month with releases) · `shoes.html` · `best-<list>.html` per published list · `brands.html` · `brand-<slug>.html` for every brand · `shoe-<slug>.html` for every shoe.

## Local build

```
pip install pillow          # only for tools/make_logos.py
python3 tools/fetch_data.py # needs network to Supabase
RD_TODAY=2026-09-05 python3 build.py
open docs/index.html
```

`RD_TODAY` pins what counts as "this week"; omit it for the real date. `RD_MEDIA_BASE=file:///path/to/media/` renders with local images when offline.

## Adding content

Everything is a row in Supabase (Table Editor), and images go in the `media` bucket:

- **A shoe**: insert into `shoes` (pick the brand, set `image_path` to `shoes/<file>.jpg` after uploading the square product shot), then add its `releases`. It appears on the Shoes grid, its brand page, the calendar, and gets its own page.
- **A drop / restock / delay**: insert into `releases`. `is_lead_drop` makes it the homepage hero. Rumored items use `status = rumored` and show dashed.
- **Scores**: `shoe_ratings` (one row per shoe). The written review goes in `shoe_editorial`.
- **A "Best for" list**: insert into `lists` (set `published`), then `list_entries` with ranks and tags. Entries with `made_cut = false` go under "Didn't make the cut".
- **A brand**: insert into `brands`, upload `logos/<slug>.png`.
