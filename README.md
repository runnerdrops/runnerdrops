# RunnerDrops — site mockup

High-fidelity static mockup of RunnerDrops.com in the Nice Kicks 2026 paste-up design system.

## Layout

| Path | What it is |
|---|---|
| `build_pages.py` | Content (shoes, calendar rows, HYROX ranking, brands, Nike lineup) + page templates. **Edit content here.** |
| `build_site.py` | Turns the templates into the multi-page site in `site/`, wires links, writes images. |
| `imgs.json` | Every product photo, cropped and keyed (`NIKE_LAT`, `HOKA_SQ`, …). |
| `fonts.css`, `shared.css` | Embedded fonts (Oswald / Archivo / JetBrains Mono) and shared design tokens. |
| `cal_block.html`, `nav.html`, `foot.html` | Shared fragments. |
| `site/` | **Generated output.** Open `site/index.html` in a browser. Do not hand-edit. |

## Rebuild

```
python3 build_pages.py && python3 build_site.py
```

Requires Python 3 + Pillow (`pip install pillow`).

## Pages

index.html (home A) · home-calendar.html (B) · home-board.html (C) · calendar.html · shoes.html · best-hyrox.html · brands.html · brand-nike.html · shoe-alphafly-3.html · shoe-adios-pro-4.html

## Adding a shoe photo

Drop the source image in `src-images/`, run the crop helper (see `tools/add_image.py`), then reference the new key as `{{KEY}}` in `build_pages.py` or `cal_block.html`.
