# 0066. Turn rewind and run-ahead off for PS1

- Status: Accepted
- Date: 2026-10-17
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0063](0063-ps1-in-scope-on-pcsx-rearmed.md), [ADR 0068](0068-ps1-input-digital-then-analog.md), [PS1 plan](../research/ps1-plan.md) section 3, [issue 59](../../.github/issues/59-ps1-options.md)

## Context

A pcsx state is 0x440000 bytes (4,456,448, about 4.4 MB).
slot's rewind ring is 20 MB (`rewind.rs:3`), so it holds about 4 uncompressed states, and a
4.4 MB serialize on every capture is costly on the A53. bently and tray ship PS1 rewind (tray
with a 48 MB ring). omega-zero turns it off. Run-ahead in v1.7.0 is gated to mGBA
(`session.rs:401`), and bently's PS1 run-ahead loads a second copy of the core and needs a new
dependency.

## Decision

- `Platform::Ps1` answers no rewind: no capture, no ring and no rewind gesture. L2 goes to the
  game (ADR 0068).
- Run-ahead stays off for PS1. The mGBA gate is not widened.
- Manual save states, the autosave on eject and the lid-close save stay on.

## Consequences

- No rewind memory or capture cost on PS1.
- L2 and R2 belong to the game, so PS1 fast-forward moves to SELECT+R2, the maintainer's choice
  (2026-10-17, as omega-zero does it). The quick menu keeps its rows.
- PS1 is not listed under rewind in the parity table. The README known gaps say so.
- Revisit only with numbers: a compressed ring that fits, and a capture cost under budget.
