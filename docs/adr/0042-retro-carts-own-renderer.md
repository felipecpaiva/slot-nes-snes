# 0042. Draw NES and SNES carts with our own procedural renderer on v1.7.0

- Status: Accepted. Amends [0006](0006-real-cart-art-with-variants.md). Amended by [0054](0054-bitmap-retro-carts.md)
- Date: 2026-10-15
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0038](0038-rebase-to-slot-v1-7-0.md), [patch 0012](../../patches/0012-cart-art.patch), [patch 0020](../../patches/0020-label-top.patch)

## Context

slot v1.7.0 draws its three moulds (GBA, notched, rounded) from hand-drawn bitmaps with an
overlay blend, and deleted the procedural pieces our NES, Famicom, SNES and SFC carts used
(`depth_map`, `Detail`, `emboss`, `rasterise_detail`, the board-through-plastic shading). Clear
carts are now three layers on the shelf: interior bitmap, board bitmap, front shell at 80%.
There is no NES or SNES bitmap art; drawing some would be invented art.

## Decision

Keep the v1.6.0 look for NES and SNES in our own files: `retro_mould.rs` holds the rasteriser
helpers copied from v1.6.0, `retro_face.rs` the shell, mould detail, recess, label and clip.
`cart_face`, `cart_face_with` and `label_size` send NES and SNES carts there; GBA and Game Boy
carts stay on upstream's bitmaps untouched. `is_clear` is false for NES and SNES (their face
already draws its own see-through plastic and board) and `cart_interior` gives the core picker an
empty face, so no GBA interior or board is drawn behind them. The Favorites star sits on the
retro label box (`retro_label_rect`). Lids rest at the cart's own aspect through `lid_rest_for`.

## Consequences

- Carts do not read the theme; only the chrome around them changes. Check both themes on the
  device.
- NES and SNES carts look like v1.6.0, not like v1.7.0's skeuomorphic carts. Bitmap NES and SNES
  moulds would need art from the maintainer (open question).
- The `silhouette.rs` visibility hunks are gone; cart.rs has 11 small hunks.
