# 0054. Draw NES and SNES carts from generated neutral bitmaps with upstream's Overlay

- Status: Accepted. Amends [0042](0042-retro-carts-own-renderer.md)
- Date: 2026-10-16
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0042](0042-retro-carts-own-renderer.md), [patch 0023](../../patches/0023-retro-bitmap-carts.patch), [docs/cart-art/VARIANTS.md](../cart-art/VARIANTS.md)

## Context

slot v1.7.0 draws GBA, GB and GBC carts from the hand painted 50% grey shells
(`assets/*_neutral.png`): the game's colour goes onto the grey with Photoshop Overlay, so the
painted bevel, grain and label well follow any colour. Our NES, Famicom, SNES and SFC carts were
still the flat v1.6.0 fill plus code-drawn grooves and a 2-3 px hard label bevel (ADR 0042), and
looked flat next to them. ADR 0042 left "bitmap moulds need art" open. The maintainer chose to
generate the four shells now (option a of the bitmap-carts research) and decide separately
whether to offer them to Markus (@MarkusMaribu, slot PR #74) as paint-over bases.

## Decision

`crates/slot-ui/examples/retro_neutrals.rs` writes `crates/slot-ui/assets/retro/{nes,famicom,
snes,sfc}_neutral.png` (312x328 and 360x225, the existing cart boxes). Its only inputs are our
outlines and detail SVGs, our label rects (`retro_label_rect`) and lighting measured at run time
from upstream's `assets/gba_neutral.png`: body 128.4, grain std 3.39 in 2 px blocks, a 16 px
outer bevel profile by distance from the edge, well 116.1 and a 3 px lip on each side of the
well. Grooves take the darkest lip value (84) and ridges the lightest (162). The grain is an
integer hash, so a rerun is byte-identical. It is a Rust example, not a Python script, because
our Python tooling is standard library only and the shapes need resvg, which slot-ui already has.

`retro_face.rs` blends each pixel's colour (flat for Solid, the board-through-plastic tint for
Clear and Glitter, as before) onto the neutral with its own copy of upstream's 8-line `overlay`.
The label rect keeps the neutral's grey and the label is pasted flat. The face stays opaque
inside the outline (no 80% clear shell: NES and SNES have no interior or board layer behind
them, ADR 0042). `mould_detail`, `recess_label`, the detail rasteriser, the empty
`lettering_nes.png` and `lettering_snes.png` and our hunk in upstream's `examples/lettering.rs`
are gone.

## Consequences

- NES and SNES carts read as the same family as v1.7.0's carts (grain, soft edge, recessed well)
  in both themes. They still lack Markus's hand-placed corner highlights.
- `cart.rs`, `bitmaps.rs` and every GBA, GB and GBC path are untouched, and the upstream touch
  point map loses one file.
- `cart_shell.txt` colours, finishes and the region pick work as before. No shell in
  VARIANTS.md is two-tone, so each neutral is one layer.
- A hand-painted replacement only has to keep the file size and the label well position; the
  tests in `tests/retro_bitmap.rs` check both. Rerun the example if an outline, detail SVG or
  label rect changes, or if upstream repaints `gba_neutral.png`.
