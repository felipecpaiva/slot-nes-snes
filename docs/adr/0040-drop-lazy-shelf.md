# 0040. Drop lazy-shelf: upstream looks up shells lazily

- Status: Accepted
- Date: 2026-10-15
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0038](0038-rebase-to-slot-v1-7-0.md), BrandonKowalski/slot#75 (closed, not merged)

## Context

Our patch 0015 made `Shelf::new` stop reading every Game Boy header at boot (one `OnceLock` per
cart); on the device it took scan to session from 1.87 s to 0.007 s
([upstream-lazy-shelf-comment.md](../contributions/upstream-lazy-shelf-comment.md)). We offered it upstream as slot#75, which was
closed. slot v1.7.0 `Shelf::new` now builds `shells` and `clears` as `Vec<OnceLock<..>>` filled on
first draw, and `gb_shell_of` reads through `gb::cached_header`, a per-path cache.

## Decision

Drop patch 0015. The NES and SNES shell lookup runs at draw time with no per-shelf cache:
`retro_shell_of` is a platform match plus, for SNES only, a header read held in a per-path cache
in `retro_cart.rs` (the same shape as upstream's `cached_class`).

## Consequences

- Two fewer `shelf.rs` hunks.
- Boot time must be re-measured on the device (the ns.0 gate was 1.85 s; needs the device).
