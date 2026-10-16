# 0057. Show the whole Master System box front in a tall label well

- Status: Accepted. Amends [0014](0014-real-label-art.md) and [0056](0056-sega-carts-one-box-per-platform.md)
- Date: 2026-10-16
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 52](../../.github/issues/52-platform-sms.md), [patch 0029](../../patches/0029-sms-box-art.patch), [docs/cart-art/SEGA.md](../cart-art/SEGA.md) section 8, `tools/fetch-labels.py`

## Context

ADR 0014 puts the real cart label on every cart and never box art. Master System carts carry
almost no artwork: the label is mostly the game's name on a grid strip (SEGA.md section 2), so a
shelf of them reads as a row of near identical strips. The box fronts are what people remember.
They are portrait: 397 of 408 box thumbnails in the maintainer's EmulationStation scraped
Master System library measure 0.71 width / height (393 are 456 x 640, 0.7125). Which scraper
fetched them is not recorded in the library files, so this is a measurement, not a statement
about ScreenScraper `box-2D` itself.

## Decision

- Master System uses the front box art for every game, not only as a fallback, so the shelf is
  consistent. `tools/fetch-labels.py` asks ScreenScraper for type `box-2D` (never `box-2D-side`,
  `box-2D-back` or a screenshot), in the same region order as the label scans, a PNG first. Boxes
  are cached by CRC under `ss/SMS/box-2D/`, apart from any older scan. A label already on the card
  is kept unless `--force`, and the run says so.
- The well is portrait at the box aspect: on the 360 x 218 `sms` cart, 140 x 196 (0.714), centred,
  spanning the face height; the grooves and panel rim now sit on both sides of it. The Sega Card
  takes the same tall well scaled to its face: 114 x 160 (0.7125), above the contacts.
- `label_cover` fits a Master System image whole (contain, never crop) on the mean colour of the
  image's own outer edge. The top-of-label crop stays for NES, SNES, Game Gear and Mega Drive.
- The cart outline and the 240 x 145 seated box of ADR 0056 are unchanged.

## Consequences

- Box art is user fetched like labels: nothing is committed, the 0014 rule still holds for every
  other platform, and a Master System cart never shows a screenshot.
- Only `sms_neutral.png`, `segacard_neutral.png` and `sms_cart_detail.svg` change; the other
  neutrals are byte identical when the example is rerun.
- Cards that already hold an SMS label scan keep it until the user reruns with `--force`.
- A box with another aspect is letterboxed on its edge colour, never cut.
