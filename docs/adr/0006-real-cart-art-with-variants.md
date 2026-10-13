# 0006. Ship real NES, Famicom, SNES and Super Famicom cart art with variants in v1

- Status: Accepted
- Date: 2026-10-11
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 24](../../.github/issues/24-phase-4-cart-art.md), [issue 25](../../.github/issues/25-cart-variant-research.md), [issue 26](../../.github/issues/26-cart-art.md), [issue 27](../../.github/issues/27-cart-shell-grammar-region.md), [patch 0012](../../patches/0012-cart-art.patch), [patch 0013](../../patches/0013-cart-shell-region.patch), [VARIANTS.md](../cart-art/VARIANTS.md)

## Context

slot gives GB, GBC and GBA carts real shapes and variants. The user: "A lot of the experience
around this project is based on some of the nostalgia. [...] I would like to have the same
experience for the NES and SNES because there are different versions of the cartridges as well."

## Decision

v1 ships real NES, Famicom, SNES and Super Famicom cart shapes with colour and finish variants,
at the same depth slot gives GB, GBC and GBA. Outline words `nes`, `famicom`, `snes`, `sfc`, with a
region auto-pick for `auto`.

## Consequences

- Phases 1 to 3 used a flat grey placeholder on the GBA shape until Phase 4.
- Colour tables hold only research-verified rows with a cited source (`eval-colour-sources.sh`);
  renders are judged blind against reference photos.
- Upstream `shell.rs` pins `shell_presets().len() == 25`, so the new presets live in
  `retro_presets()` instead (issue 26).
- Famicom Disk System is deferred (issue 33).
- Cart Studio may drop unknown `cart_shell.txt` lines; NES and SNES overrides belong in
  `Config/cart_shell.txt`.
