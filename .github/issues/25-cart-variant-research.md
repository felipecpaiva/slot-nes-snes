---
title: "Research and cite NES, Famicom, SNES and Super Famicom cart variants and colours"
phase: 4
area: docs
type: chore
size: M
depends_on: []
---

## Why
Phase 4 starts with research and no code: every outline, region rule and colour must come from a cited reference before any asset or table ships (docs/PLAN.md Phase 4 deliverables, Build steps 23, 24, 25).

## Scope
- [x] `docs/cart-art/VARIANTS.md` covering:
  - outline references: NES front-loader (US/EU), Famicom (short, wide), SNES NTSC-US (ridged top, grooved sides), Super Famicom/PAL (rounded);
  - the verified SNES region byte offset (candidates 0x7FD9 LoROM and 0xFFD9 HiROM, +0x200 with copier header, to be confirmed) and the region code to variant map;
  - notable carts, each with a source URL: gold The Legend of Zelda and Zelda II (NES), black unlicensed Tengen NES carts, black Killer Instinct SNES cart, Famicom per-game colours.
- [x] `docs/cart-art/refs/<variant>.jpg` reference images with source URLs, used by the blind likeness review.
- [x] No row without a cited reference.

## Tests
| ID | File | Asserts |
|---|---|---|
| (none) | | Docs only. `evals/eval-colour-sources.sh` (26-cart-art) later checks every table row has a cited `VARIANTS.md` row |

No upstream test file is touched.

## Edge cases
| Case | Expected handling |
|---|---|
| (none specific) | An uncited colour is dropped, not guessed |

## Acceptance
- [x] Every outline, region code and notable cart has a source URL.
- [x] The SNES region byte offset is stated as verified, with the reference used.
- [x] One reference image per variant in `docs/cart-art/refs/`.

## Device check (RG34XXSP)
None, research only.

## Review notes
- Reviewer checks every URL resolves and supports the row it is cited for.
- Image licences: reference photos stay in `docs/` for comparison only; note their source.

## References
- docs/PLAN.md: Phase 4 deliverables (research sub-step), Build steps 23, 24, 25, Quality bar (cart reference images)

## Completion notes
- Free reference images (public domain or CC BY / CC BY-SA, see `docs/cart-art/refs/SOURCES.md`): `nes`, `famicom`, `snes` (also shows `sfc`), `sfc`, plus extras `snes_pal` and `nes_gold_zelda`.
- Link-only: Tengen black NES cart, Killer Instinct black SNES cart (no free photo found); more Famicom colour photos are link-only.
- Known gaps recorded in VARIANTS.md section 5: Famicom shell mm, label window mm for snes/sfc/famicom, and no numeric colour values from any source.
