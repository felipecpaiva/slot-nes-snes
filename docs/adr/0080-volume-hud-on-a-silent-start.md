# 0080. Show the volume HUD when a game starts muted or at zero

- Status: Accepted. Drop when the upstream PR lands (0047)
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0047](0047-upstream-first-fixes.md), patch `patches/0052-silent-start-hud.patch`, [fork review](../research/fork-review-2026-10-18.md), jgraving/slot [12f7b3a](https://github.com/jgraving/slot/commit/12f7b3a), upstream PR text in [docs/contributions/upstream-silent-start-hud-pr.md](../contributions/upstream-silent-start-hud-pr.md)

## Context

A game started with the device muted or with the volume at zero plays in silence, which reads as a
broken core, most of all on a PS1 disc or a new system. jgraving/slot 12f7b3a (GPL-3.0) shows the
volume HUD once on the phase change into `Playing`.

## Decision

- On the phase change into `Playing` in `App::update` (the end of an insert, after the core is
  ready), if `output_volume()` is 0, show the volume HUD with value 0 and the muted flag, so the
  muted or the zero glyph shows. It shows for upstream's `HUD_MS` and fades as usual.
- Not while the cart is loading (the phase is still `Inserting`), not on a wake from a doze
  (`wake()` sets `Playing` without passing that block), not on an eject to the shelf; the next
  insert shows it again.
- The logic is in `crates/slot/src/app/silent_start.rs` with a `hud_visible()` accessor for the
  tests; `app.rs` gets a `mod` line and one call.

## Consequences

- `crates/slot/tests/silent_start.rs`: zero volume and muted each show the HUD as play begins and
  not while loading; a game with sound shows none; it fades during play; a wake does not show it;
  an eject shows nothing on the shelf; the next insert shows it again.
- **Drop the patch when the upstream PR lands.**
