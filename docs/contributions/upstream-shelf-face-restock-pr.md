# PR title

Keep cart faces on the cart they were built for when Favorites or Recents restocks

# PR body

## Problem

1. `CartFaces::place` puts a built face at `(shelf, index)`. If Favorites or Recents restocks
   while that face is being built (a favourite toggle, a game started), the face lands on the cart
   now at that index. `requeue` skips keys already pending, so the wrong face stays until the next
   restock.
2. `Shelf::restock` frees every face and selects index 0, so a favourite toggle rebuilds every
   face on the Favorites shelf, and the Favorites shelf loses its selected game when a favourite
   is added from another shelf.
3. `seated_cart`, `auto_link`, `Shelf::find` and `Shelf::behind` look the cart up by stem only.
   On Favorites or Recents, two systems can hold the same file name, and the first one wins.

## Change

- The face worker sends back the `Cart` it built for, and `place` drops the face and interior
  when the cart at `(shelf, index)` is a different one (`platform` and `stem`).
- `App::restock` keeps the faces and interiors of carts still on the shelf, frees only the rest,
  and keeps the selected cart selected (else the old index, clamped). Recents still opens on its
  newest game when its list changes.
- `Shelf::find` and `Shelf::behind` try the selected index first; `seated_cart` and `auto_link`
  use `find`.

## Tests

New test file with four tests, each failing on the current code:

- a restock keeps each cart's face and hands back the rest;
- a restock keeps the selected cart selected;
- the selected cart wins a stem another platform shares;
- a face built for the cart at `(Favorites, 0)` no longer fits there after a favourite toggle,
  and fits at its new index.

`favorites.rs`, `recents.rs`, `cart_faces.rs` and `last_shelf.rs` pass unchanged.
`cargo test --workspace` passes.

## Credit

Reimplemented from marghost/slot_modded 88af60a (GPL-3.0).
