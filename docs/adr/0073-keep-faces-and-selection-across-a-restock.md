# 0073. Drop stale cart faces, keep faces and selection across a restock, prefer the selected cart

- Status: Accepted. Drop when the upstream PR lands (0047)
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0047](0047-upstream-first-fixes.md), [ADR 0049](0049-per-shelf-cart-memory.md), [ADR 0069](0069-ps1-jewel-case-shelf.md), patch `patches/0045-shelf-face-restock.patch`, [fork review](../research/fork-review-2026-10-18.md), marghost/slot_modded [88af60a](https://github.com/marghost/slot_modded/commit/88af60a), upstream PR text in [docs/contributions/upstream-shelf-face-restock-pr.md](../contributions/upstream-shelf-face-restock-pr.md)

## Context

Three problems in v1.7.0, all still in upstream main:

1. `CartFaces` places a built face by `(shelf, index)` only. When Favorites or Recents restocks
   while a face is being built, the face lands on whatever cart now sits at that index, and stays
   there until the next restock (`requeue` skips keys already pending).
2. `Shelf::restock` frees every face and interior and selects index 0. Toggling a favourite
   rebuilds every face on the Favorites shelf, which is slow with PS1 cover art (ADR 0069), and
   the selection jumps. ADR 0049 lists this as an open point.
3. `seated_cart`, `auto_link`, `Shelf::find` and `Shelf::behind` find the cart by stem alone, so
   on Favorites or Recents a stem two platforms share resolves to the first one.

marghost/slot_modded (GPL-3.0) fixed all three in 88af60a (with a `CartKey` type in slot-store).

## Decision

- The face worker sends back the `Cart` it built for. `place` drops the face (and the interior)
  when `face_fits` says the cart at `(shelf, index)` is not that cart. No new slot-store type.
- `App::restock` calls `restock_keeping_faces` (new file `crates/slot/src/shelf_restock.rs`): it
  takes the faces and interiors by `(platform, stem)`, runs upstream `Shelf::restock` unchanged,
  puts the matches back at their new index, frees the rest, and selects the old cart, else the
  old index clamped. Recents still selects index 0 when its list changes, as upstream does.
- `Shelf::find` and `Shelf::behind` try the selected index before the stem search, and
  `seated_cart` and `auto_link` go through `find`.

## Consequences

- A favourite toggle no longer rebuilds the shelf's faces, and the Favorites shelf keeps its
  selected game when another is added from a platform shelf (upstream selects index 0 there).
- Tests in `crates/slot/tests/shelf_restock.rs`: faces kept and the rest handed back, selection
  kept, the selected cart wins a shared stem, and a face built for the old cart at
  `(Favorites, 0)` no longer fits after a toggle while it fits at its new index. Each was red with
  its part of the fix taken out.
- Upstream `favorites.rs`, `recents.rs`, `cart_faces.rs` and `last_shelf.rs` pass unchanged.
- **Drop the patch when the upstream PR lands.**
