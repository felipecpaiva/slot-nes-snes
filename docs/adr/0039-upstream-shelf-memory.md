# 0039. Use upstream's shelf memory and drop Config/shelf.state

- Status: Accepted. Supersedes [0025](0025-shelf-memory.md). Amended by [0049](0049-per-shelf-cart-memory.md)
- Date: 2026-10-15
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0038](0038-rebase-to-slot-v1-7-0.md), [issue 45](../../.github/issues/45-shelf-memory.md), slot #53, `crates/slot/tests/nes_shelf_memory.rs`

## Context

Our patch 0019 kept the last shelf and each shelf's cart in `Config/shelf.state`. slot v1.7.0
(#53) remembers the shelf and its cart in `slot.state` (`shelf=` and `shelf_cart=platform/stem`)
when slot powers off or restarts, and boots back onto them. It keys shelves by
`dir_name().to_ascii_lowercase()` and parses carts through `platform_value`, which our patches
0002 and 0005 already point at `Platform::SHELVES`.

## Decision

Drop patch 0019 and `Config/shelf.state`. NES and SNES use upstream's memory, Favorites
(`favorites.txt`) and Recents (`recents.txt`) through the `SHELVES` hunks in `shelves_of` and
`platform_value`. `nes_shelf_memory.rs` proves it: power off on an SNES cart boots back onto it,
Y stars a NES cart into `favorites.txt` and the Favorites shelf, NES and SNES recents stock the
Recents shelf. All three fail if `platform_value` goes back to `Platform::ALL`.

## Consequences

- Removes `shelf_recall.rs`, two `Shelf` hunks and six `app.rs` hunks.
- Lost: per-shelf cart memory (only the shelf you were on keeps its cart) and saving on every
  rest (upstream saves at power off and restart, so a flat battery forgets the move). Open
  question for the maintainer if either matters.
- A stale `Config/shelf.state` from ns.0 is ignored; nothing deletes it.
