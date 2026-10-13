# 0007. Toggle the SNES picture mode with SELECT+X

- Status: Accepted
- Date: 2026-10-11
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 15](../../.github/issues/15-snes-input.md), [patch 0007](../../patches/0007-input.patch)

## Context

Upstream toggles the picture mode with L1/R1 and always strips X/Y for turbo. SNES needs X, Y, L
and R as game buttons. X is unused in the SELECT chords (`gesture.rs:409-424`).

## Decision

On SNES, SELECT+X toggles Stretch and Actual. SNES passes X/Y through and L/R belong to the game.
The chord acts on SNES only.

## Consequences

- The chord is gated by `Gestures::set_video_mode_chord` (default off), so SELECT+X still reaches
  GBA games. T22b proves identical GBA input masks in both trees.
- NES keeps slot's L1/R1 picture toggle and X/Y turbo, like GB.
- The Turbo quick row is a documented no-op on SNES.
