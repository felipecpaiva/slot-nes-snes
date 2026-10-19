---
title: "Draw NGP carts (mono and Color shells) and fetch their labels"
phase: 9
area: ui-art
type: feature
size: M
depends_on: [72-platform-ngp]
---

## Why
Step 9. Every shelf gets real-looking carts (ADR 0006, 0054). NGP carts are a small pak with a wide label and a ridged cap.

## Scope
- [x] NGP pak in the retro bitmap renderer (ADR 0054), patch 0087. Decided 2026-10-19 by the maintainer: one dark grey shell (nelynes `0x24 0x25 0x29`) for mono and Color carts alike (ADR 0090); the header byte only picks the label's ScreenScraper id.
- [x] nelynes/slotPlus `assets/src/carts.py` (a8eae4c: ridged cap, 246x133 label, SNK and NGP plaques) as a drawing reference only, credited (GPL-3.0); we draw our own.
- [x] `tools/fetch-labels.py`: an `NGP` entry with both dats, `SNK - Neo Geo Pocket` and `SNK - Neo Geo Pocket Color` (libretro-database `metadat/no-intro`), extensions `.ngp .ngc .ngpc`. `SYSTEMS` holds one ScreenScraper id per shelf and NGP has two, `ngp` 25 and `ngpc` 82 (Skyscraper `platforms_idmap.csv` at ccd49ae, the commit the script already cites). Pick the id per ROM from the header byte, which the script reads as it does for NES and SNES headers. Extend the tuple or add a small per-system id function; do not add a second shelf.
- [x] docs/cart-art/NGP.md with the shell references and sources.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `tools/tests` | a Color header asks ScreenScraper for id 82, a mono header for 25; both dats match by CRC |
| (new) | `slot-ui/tests/ngp_cart.rs`, `render_nes_shelves.rs`, `retro_bitmap.rs` | mono and Color carts take the pak and the grey; it renders at the shelf size with and without a label |

## Edge cases
| Case | Expected handling |
|---|---|
| A ROM in neither dat | Placeholder label, shell from the header |
| A mono game in a Color dat entry (compatible carts) | The header byte decides the shell; the dat only finds the label |

## Acceptance
- [ ] `task check` green, card tests included.

## Device check (RG34XXSP)
The shelf with ten carts, both shells, scrolls without a dropped frame.

## References
- ADR 0006, 0054, 0090; docs/research/ngp-plan.md section 6
