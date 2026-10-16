# 0049. Remember each shelf's cart on top of upstream's shelf memory

- Status: Accepted. Amends [0039](0039-upstream-shelf-memory.md); restores the per-shelf part of [0025](0025-shelf-memory.md)
- Date: 2026-10-15
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0047](0047-upstream-first-fixes.md), [patch 0021](../../patches/0021-shelf-cart-memory.patch), slot #53, upstream branch `per-shelf-cart-memory`

## Context

slot v1.7.0 (#53) keeps `shelf=` and `shelf_cart=` in `slot.state`, written by `remember_shelf`
at power off and restart only, and `boot` restores them through `remembered_seat`. Only the shelf
you were on keeps its cart, and a crash or a flat battery forgets the move (the open question in
ADR 0039). A new `SlotState` field would break the full literal in upstream's `durability.rs`.

## Decision

Extend #53 instead of replacing it, the same code here and in the upstream PR:
- `Config/shelf_carts.txt` holds one line per shelf, `<shelf key>=<platform>/<stem>`, the keys
  of `Rack::key` (`recents`, `favorites`, `gba` ...) and the format of `recents.txt`. It is written
  by `write_shelf_carts`, which skips an unchanged file, on the state writer thread.
- Once the cursor is at rest on the shelf (no held direction), the app sets `shelf`, `shelf_cart`
  and that shelf's line, then writes through the writer. Power off and restart still write at once.
- `boot` puts every shelf on its remembered cart, then upstream's `remembered_seat` picks the
  shelf. A seated cart still resumes. A cart that is gone leaves the shelf at its first cart.
- Recents and Favorites are shelves like any other and keep their own cart.

## Consequences

- Drop patch 0021 when the upstream PR lands; the file stays readable by upstream's code.
- A restock of Recents or Favorites in a session still starts at upstream's index; the memory
  applies at boot.
- `slot.state` gains no key and `SlotState` no field, so no upstream test changes.
