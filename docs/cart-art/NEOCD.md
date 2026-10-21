# Neo Geo CD jewel case (ADR 0106)

Same rules as [PS1.md](PS1.md): every value cites a page opened on 2026-10-21, or says that nothing was
found. The Neo Geo CD shelf draws the PlayStation's jewel case and disc unchanged, as the PC Engine CD
shelf does ([PCECD.md](PCECD.md)); this page records why that is the right object and what was looked for.

## 1. The case

| Item | Value | Source |
|---|---|---|
| Case | the standard three-piece jewel case, 142 x 125 x 10 mm | [Wikipedia: Optical disc packaging](https://en.wikipedia.org/wiki/Optical_disc_packaging); the same row as PS1.md |
| Neo Geo CD games in it | "Typically with case and manual, but without spine card"; a mint copy "would include spine card" | [Racketboy: Neo-Geo CD Price Guide and English Version Rarity](https://racketboy.com/?p=11240) |
| Japanese spine strip (obi) | "folded over the left side of music CDs, video games, LaserDiscs, or DVDs" | [Wikipedia: Obi (publishing)](https://en.wikipedia.org/wiki/Obi_(publishing)) |
| Disc | 120 mm, 15 mm centre hole | [Wikipedia: Compact disc](https://en.wikipedia.org/wiki/Compact_disc); PS1.md section 1 |

Not found: a page that could be opened showing a Neo Geo CD case that differs from the standard jewel case
on its front. A collectors' thread says some cases carry an etched Neo Geo logo in a corner of the
plastic and others do not (videogameforums.com, "NGCD Jewel Cases", in a search result only; the page
returned 503), so no etched variant is drawn. The NEO-GEO CD logo is printed on each game's own cover and
disc, so the cover art carries it.

## 2. What slot draws

| Shell | When | Notes |
|---|---|---|
| `jewel_jp` | the file name carries a `Japan` tag (`ps1_case::tag_region`) | the PS1 case with the spine strip; both of the maintainer's discs |
| `jewel_us` | any other disc (`USA`, `World`, no tag) | the plain case |
| disc | every disc, on insert | the PS1 disc: printed from radius 51 to 177 px, hub and hole generated |

The region comes from the name tags only. A Neo Geo CD disc has no `SYSTEM.CNF` serial and slot never
groups discs, so there is no double case.

## 3. Images

- Cover: ScreenScraper `box-2D`, at `Labels/NEOCD/<stem>.png`, fitted whole in the square well.
- Disc: ScreenScraper `support-2D`, at `Labels/NEOCD/disc/<stem>.png`, printed on the disc's print area.
- Both by name under system id 70 (`tools/fetch-labels.py --only NEOCD --by-name --logo-fallback`).
- The translation has no ScreenScraper or Redump name of its own. For its logo, pass an alias line (the
  `--aliases` format, [BY-NAME.md](BY-NAME.md)) naming the original Japanese title, which
  libretro-thumbnails "SNK - Neo Geo CD" has as a Named_Logo:

  ```
  NEOCD	Samurai Shodown RPG (Japan) (En)	sibling:Shinsetsu Samurai Spirits - Bushidou Retsuden (Japan)
  ```

  A ScreenScraper game id (`ss:<id>`) can replace it once the name pass suggests one (`--suggest`).
