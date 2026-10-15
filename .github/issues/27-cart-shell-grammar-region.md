---
title: "Patch 0011: Add cart_shell.txt outline words and region auto-pick for NES and SNES"
phase: 4
area: ui-art
type: feature
size: M
depends_on: [26-cart-art]
---

## Why
Users pick a cart variant per game in `cart_shell.txt`, and `auto` should pick the right variant from the cart's region (docs/PLAN.md Phase 4 deliverables, Build steps 23, 24).

## Scope
`patches/0013-cart-shell-region.patch` (0011 and 0012 were taken by earlier patches):
- [x] `slot: crates/slot-store/src/cart_shell.rs`: append `Outline::{Nes, Famicom, Snes, Sfc}` with parse and `to_value` words `nes`, `famicom`, `snes`, `sfc` (`:32-36`).
- [x] A word that doesn't match the cart's platform is treated as `auto`.
- [x] Region auto-pick (ExHiROM `0x40FFC0` probe added to `snes.rs` so `0x40FFD9` is reachable; Canada, Korea and Brazil stay `sfc`, see `VARIANTS.md` section 8):
  - SNES in `crates/slot-store/src/snes.rs`: header region byte at the offset verified in 25-cart-variant-research (LoROM/HiROM, +0x200 with copier header); Japan gives Sfc, USA gives Snes, Europe gives Sfc.
  - NES in new file `crates/slot-store/src/nes.rs`: No-Intro stem tags; `(Japan)` gives Famicom, `(USA)`/`(Europe)` give Nes, no tag gives Nes.
- [x] README section on hand-editing `Config/cart_shell.txt`.
- [ ] Cart Studio round-trip check, recorded in `docs/cart-art/VARIANTS.md`. Recorded as unverified (external tool, not run); overrides belong in `Config/cart_shell.txt`.

## Tests
| ID | File | Asserts |
|---|---|---|
| T34 | `slot-store/tests/nes_cart_shell.rs` | Parse `nes`, `famicom`, `snes`, `sfc`; unknown word: round-trip; unknown returns None; GB words unchanged |
| T35 | `slot-store/tests/snes_region.rs` | Region bytes at the verified offset, LoROM/HiROM, copier: Japan gives Sfc; USA gives Snes; Europe gives Sfc |
| T36 | `slot-store/tests/nes_region.rs` | `(Japan)`, `(USA)`, `(Europe)`, no tag: Famicom, Nes, Nes, Nes |
| T39 | `slot-ui/tests/nes_gb_outline.rs` | GB stem with `nes ...`: treated as Auto (header class) |
| extra | `slot-ui/tests/nes_region_shell.rs`, `render_nes_region.rs`, `slot/tests/nes_label_cache.rs` | Variant selection (word for own platform wins, wrong-platform word ignored), `(Japan)` NES stem draws Famicom, USA SNES ROM draws SNES, Japan SNES ROM draws SFC, shelf shadow and label cache follow the variant |

`crates/slot-store/src/nes.rs` and `snes.rs` carry `#[cfg(test)]` modules for the tag and header parsers (new code only). Upstream cart_shell tests stay unmodified.

## Edge cases
| Case | Expected handling |
|---|---|
| `cart_shell.txt` line `nes ...` read by unpatched slot | Upstream `ShellChoice::parse` returns None on an unknown outline word (`slot: crates/slot-store/src/cart_shell.rs:32-36`), so the line is dropped and the cart falls back to auto |
| GoodTools short tags (`Akumajou Dracula (J)`) | Read as regions letter by letter (`J`, `U`, `E`, cited in `VARIANTS.md` section 8): `(J)` gives Famicom, `(JU)` and `(U)` give NES. Fixed 2026-10-15 in patch 0013, tests in `nes_region.rs`; `tools/fetch-labels.py` mirrors it |
| Cart Studio may drop `nes`/`snes` lines when rewriting `Labels/cart_shell.txt` | Unverified. Phase 4 round-trip check. Until then, document "keep NES/SNES overrides in `Config/cart_shell.txt`" |

## Acceptance
- [x] T34 to T36 and T39 green (`cargo test -p slot-store -p slot-ui -p slot`: 1376 passed, 0 failed).
- [x] GBA harness compare 0 diffs (H1, H2). `task check` 2026-10-13: compare 0 diffs (H1, H1G, H2, B1, H3).
- [ ] Round-trip result (kept or dropped) recorded in `VARIANTS.md`; README states where overrides belong. README and `VARIANTS.md` section 8 done; the result itself is "unverified", so this stays open until Cart Studio is run.

## Device check (RG34XXSP)
None separate. Variant selection shows up in the phase device check in 24-phase-4-cart-art.

## Review notes
- Plan circularity, flagged not resolved: the region byte offset is only a candidate in the plan (0x7FD9 LoROM / 0xFFD9 HiROM). Use the value from 25-cart-variant-research, not the plan's candidate, and cite it in `VARIANTS.md` section 3 (code carries no comments, CONTRIBUTING section 4).
- Open question 2 (Cart Studio round-trip) is owned here; the default is the `Config/cart_shell.txt` note.
- Teaching the external Cart Studio the new words is out of scope.
- The stem-key collision in `cart_shell.txt` is documented only (35-deferred-stem-key-collision).

## References
- docs/PLAN.md: Phase 4 deliverables (0011, region, round-trip), Build steps 23, 24, Edge cases by layer (Cart art), Open questions 2
- `slot: crates/slot-store/src/cart_shell.rs:32-36`
