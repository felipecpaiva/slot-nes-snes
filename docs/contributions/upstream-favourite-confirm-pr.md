# PR title

Ask for a second Y before removing a favourite

# PR body

## Problem

One Y on a starred cart removes it from Favorites at once, with no undo. On the Favorites shelf
the cart also leaves the shelf, so a mis-press while browsing loses it from view.

## Change

- Y on a starred cart shows "Y Again to remove" above the cart for 3 s
  (`FAVORITE_REMOVE_MS`). A distinct second Y (a key-up in between) removes it and saves at once.
  A held Y cannot confirm.
- Any other input, a timeout, moving to another cart or leaving the shelf cancels; the next Y
  starts over.
- Starring an unstarred cart stays one Y.
- The hint is a new face: `assets/buttonlegend_round_y.png` beside the label "Again to remove",
  placed from `cart_box(platform)` and `foot_y`, clamped inside the canvas.

## Tests

- `crates/slot/tests/favorites.rs`: `unstarring_on_the_favorites_shelf_takes_the_cart_off_it` and
  `unstarring_the_last_favorite_leaves_the_empty_shelf` now press Y twice (this PR changes that
  behaviour on purpose).
- New: a held Y cannot confirm without a release; a timeout keeps the favourite and the next Y
  starts over; navigating or leaving the shelf cancels without saving; selecting another cart
  cannot confirm the previous one; removing from a system shelf also asks; the hint fades in above
  the selected cart and disappears on cancel.

## Credit

From jgraving/slot e2dc0cb (GPL-3.0), without the departure animation (37f230c, a83c345).
