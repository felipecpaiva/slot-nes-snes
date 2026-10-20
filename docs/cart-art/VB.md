# Virtual Boy cart art (issue 181)

Same rules as [VARIANTS.md](VARIANTS.md): every value cites its source, or says it is the
maintainer's choice. Nothing is guessed.

## The cart

One cart for every Virtual Boy game, `RetroShell::Vb` (patch 0109).

| Value | Ours | Source |
|---|---|---|
| One cart for every region | one shell, no region variants | ConsoleMods, [Dimensions for Game Cartridges](https://consolemods.org/wiki/Dimensions_for_Game_Cartridges), checked 2026-10-20: "the NTSC-U and NTSC-J cartridges are identical" |
| Size | seated 240 x 234, drawn 360 x 351 | same page: 75.8 mm wide, 68.36 mm tall, "73.74 mm tall when including the dust cap"; 73.74 / 75.8 x 240 = 233.5, rounded up |
| Outline | rounded top corners (r 11 of 240), small bottom corners (r 3) | the photo below; the radii are ours |
| Dust cap | the bottom 18 of 234 (5.4 mm of 73.74), drawn darker | the size difference above; the dark cap is in the photo |
| Relief | a line across the body at y 204 and the cap seam at y 216 | the photo below; positions are ours |
| Label well | permille 158, 80, 842, 680 (246 x 211 px) | measured on the photo below (Mario Clash cart), rounded |

Reference photo: Wikimedia Commons [Virtual Boy Game Paks](https://commons.wikimedia.org/wiki/File:Virtual_Boy_Game_Paks.jpg)
(Joshua W, CC BY-SA 2.0), 378 x 155 px. Used for proportions only, not shipped.

Drawn by us as `crates/slot-ui/assets/vb_cart.svg` (outline) and `vb_cart_detail.svg` (relief and the
darker cap), lit into `assets/retro/vb_neutral.png` by `examples/retro_neutrals.rs`. Every other neutral
regenerates byte for byte (sha256 compared before and after).

## Shell colour

| Carts | Colour | Source |
|---|---|---|
| Every Virtual Boy cart | `9f 9c a2`, solid | Maintainer's choice (ADR 0097): the carts are light grey in the photo, which is too warm and too small to measure, so they take the measured SNES grey. To be checked against a real cart |

A colour in `Config/cart_shell.txt` still overrides it.

## Labels

`tools/fetch-labels.py`, system `VB`: dat `Nintendo - Virtual Boy` (libretro-database
`metadat/no-intro`); ScreenScraper `virtualboy` 11 (Skyscraper `platforms_idmap.csv` at ccd49ae, row
`virtualboy,11,38,4918`). libretro-thumbnails has `Nintendo - Virtual Boy` Named_Logos (22 files,
checked 2026-10-20) for the Logo Only fallback. On Wario Land, Jack Bros., Red Alarm and Teleroboxer all
four labels came by CRC.
