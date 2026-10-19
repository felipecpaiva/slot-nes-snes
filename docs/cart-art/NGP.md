# Neo Geo Pocket cart art (issue 78)

Same rules as [VARIANTS.md](VARIANTS.md): every value cites its source, or says it is the
maintainer's choice. Nothing is guessed.

## The pak

One mould for Neo Geo Pocket and Pocket Color carts, `RetroShell::Ngp` (patch 0087).

| Value | Ours | Source |
|---|---|---|
| Pak size | 312 x 268 px, seated at 240 x 206 on the shelf | nelynes/slotPlus [a8eae4c](https://github.com/nelynes/slotPlus/commit/a8eae4c) `assets/src/carts.py` `neogeo_pocket()` (`w, h = 312, 268`) |
| Cap | full width, `round(h * 0.12)` tall, corners r 9, eight grooves at `h * (0.03 + k * 0.019)` from `w * 0.09` to `w * 0.91` | same function |
| Body under the cap | inset 2 px each side, corners r 6 | same function (inset 3); ours keeps a 1 px margin round the outline, so the body sits 2 px in from the cap |
| Label well | permille 115, 215, 905, 712 of the pak (246 x 133 px) | same function, and `ngp_label_panel` in nelynes `slot-ui/src/cart.rs` |
| Label frame | rounded ring `w * 0.092 .. 0.928`, `h * 0.195 .. 0.732`, r 9 | same function |
| Seam, plaques, arrow | seam at `h * 0.79`; plaques `w * 0.08 .. 0.355` and `w * 0.645 .. 0.92` by `h * 0.835 .. 0.948`, r 3; arrow `(w * 0.425, h * 0.842)`, `(w * 0.582, h * 0.842)`, `(w * 0.5035, h * 0.948)` | same function. The SNK and NGP lettering is left out (usvg draws no text without fonts) |

Drawn by us as `crates/slot-ui/assets/ngp_cart.svg` (outline) and `ngp_cart_detail.svg` (relief),
lit into `assets/retro/ngp_neutral.png` by `examples/retro_neutrals.rs`. nelynes' pixels are not
used; their geometry is credited (GPL-3.0).

## Shell colour

| Carts | Colour | Source |
|---|---|---|
| Neo Geo Pocket (header byte 0x23 = 0x00) | `24 25 29`, solid | nelynes/slotPlus a8eae4c `slot-ui/src/shell.rs` `NGP_SHELL` |
| Neo Geo Pocket Color (0x23 = 0x10) | `24 25 29`, solid | Maintainer's choice, 2026-10-19 (ADR 0090): no source for a separate Color shell was found, so Color carts reuse the grey |

A colour in `Config/cart_shell.txt` still overrides it.

## Labels

`tools/fetch-labels.py`, system `NGP`: dats `SNK - Neo Geo Pocket` and `SNK - Neo Geo Pocket Color`
(libretro-database `metadat/no-intro`); ScreenScraper `ngp` 25 or `ngpc` 82 by header byte 0x23, for
CRC matches (Skyscraper `platforms_idmap.csv` at ccd49ae, plan section 6). Name searches ask under 25.
