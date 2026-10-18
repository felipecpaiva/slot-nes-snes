# PR title

Show the volume HUD when a game starts muted or at zero volume

# PR body

## Problem

A game started with the device muted, or with the volume at zero, plays in silence, which looks
like a broken core.

## Change

On the phase change into `Playing` in `App::update` (the end of an insert, once the core is
ready), if `output_volume()` is 0 the volume HUD shows, with the muted or zero glyph. Not while the
cart is loading, not on a wake from a doze (`wake()` does not pass that block), not on an eject;
the next insert shows it again.

## Tests

New `crates/slot/tests/silent_start.rs`: zero volume and muted each show the HUD as play begins and
not while loading; a game with sound shows none; it fades during play; a wake does not show it; an
eject shows nothing on the shelf; the next insert shows it again. It adds one accessor,
`App::hud_visible()`.

## Credit

From jgraving/slot 12f7b3a (GPL-3.0).
