---
title: "Draw Lynx cards and fetch their labels"
phase: 12
area: ui-art
type: feature
size: M
depends_on: [103-platform-lynx]
---

## Why
Step 11. Lynx games are flat cards. The shelf needs a retro bitmap card (ADR 0054) and labels.

## Scope
- [x] Retro bitmap card shape after nelynes 98419f4 (flat card with contacts, GPL-3.0, credit), drawn by our renderer.
- [x] Title from the LNX header (0x0a, 32 bytes) when present, else the stem.
- [x] `tools/fetch-labels.py` `SYSTEMS`: `Lynx` with ScreenScraper id **28** (Skyscraper `platforms_idmap.csv` at ccd49ae, row `atarilynx,28,18,4924`) and the dat `Atari - Lynx` (libretro-database `metadat/no-intro`). The CRC is of the headerless body: strip the 64-byte LNX header before hashing (No-Intro hashes headerless; the core's own list does the same).
- [x] A turned cart's label is drawn upright on the card; the turn is gameplay only.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `test_fetch_labels.py` | an `.lnx` is hashed without its header; id 28 |
| (new) | render test | the Lynx card at shelf size |

## Edge cases
| Case | Expected handling |
|---|---|
| `.lyx` (no header) | Hashed whole |

## Acceptance
- [x] `task check` green; labels fetched for the device card set.

## Status
Landed as patch 0078-lynx-carts (2026-10-19) and the `Lynx` system in `tools/fetch-labels.py`; the card is drawn at shelf size by the shared `render_nes_shelves.rs` render tests.

## Device check (RG34XXSP)
Shelf look with five labelled carts.

## References
- ADR 0054, 0093; nelynes/slotPlus 98419f4; Skyscraper ccd49ae
