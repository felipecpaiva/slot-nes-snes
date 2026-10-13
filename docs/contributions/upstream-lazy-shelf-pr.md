# PR title

Class a Game Boy cart's shell when its backing is drawn, not when the shelf is built

# PR body

## Problem

`Shelf::new` calls `gb_shell_of` for every cart. For Game Boy and Game Boy Color carts that opens
the ROM and reads a header byte (`slot_store::gb::class`). The result is only used in
`Shelf::draw`, to pick the backing behind a faded neighbour (`alpha < 1.0`). So on a big library
the whole scan is paid for before the shelf can appear, for carts that may never be drawn faded.

## Measurement

RG34XXSP (Allwinner H700), BaseOS, SD card, 3 cold boots with the page cache dropped, median.
Library: 1,014 GBA, 854 GBC, 1,955 NES, 770 SNES.

Built from this branch and from its parent (4a4ba92), same device, same card, interleaved:

| Build | scan to session | shelf on screen (ui faces) |
|---|---|---|
| 4a4ba92 | 1.87 s | 3.98 s |
| this branch | 0.007 s | 2.04 s |

So about 1.9 s less before the shelf appears with 854 GBC carts on the card. GBA, NES and SNES carts are not probed here, so they do not change the number.

## Change

`shells` becomes `Vec<OnceLock<Option<GbShell>>>`. `Shelf::new` only builds empty cells, and the
draw site fills a cell with `get_or_init(|| gb_shell_of(cart))`. It keeps the `.get(i)` lookup, so
a cart pushed after `new` still gets the same `None` backing as before.

## Tests

New `crates/slot-ui/tests/shelf_lazy.rs`: a GBC ROM is written after `Shelf::new`, and the faded
neighbour is drawn with the rounded backing. This fails on the old code (it read the missing file
at construction and fell back to the notched one) and passes now.

`cargo test --workspace` passes. `cargo fmt --check` only reports an existing difference in
`crates/slot/tests/prefetch.rs`, which I left alone.

## Behaviour

No change in what is drawn. A cart is classed once, on its first faded draw, and kept after that.
The one difference is timing: a ROM edited between building the shelf and drawing is now read as
it is at draw time.
