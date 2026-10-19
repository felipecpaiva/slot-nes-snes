---
title: "Map the 2600 joystick and console switches"
phase: 14
area: input
type: feature
size: M
depends_on: [126-platform-a2600]
---

## Why
Stella reads fire on RetroPad B only, latches the difficulty (L/L2, R/R2) and TV type (L3/R3) switches, and counts SELECT and START (Reset) while held (tested in `atari_core.rs`). slot keeps L1 and R1, and the RG34XXSP's stick clicks are not mapped, so the latched switches become rows.

## Scope
- [ ] D-pad joystick; device B and A both send RetroPad B (fire); X and Y turbo fire as on NES.
- [ ] SELECT is Select, START is Reset (as the core maps them).
- [ ] Left difficulty, Right difficulty (A / B, default B) and TV type (Colour / B&W, default Colour) rows: slot sends one frame of the core's button at load, after a state load, and on change.
- [ ] Rows stored in a `Config/` file through upstream's `ini::write`, like `picture.txt`.

## Tests
| ID | File | Asserts |
|---|---|---|
| (done) | `atari_core.rs` | latch and momentary semantics, fire on B (patch 0060) |
| (new) | `a2600_input.rs` | device A and B both fire; a row change reaches SWCHB in the next frame; the value survives eject and reseat |

## Edge cases
| Case | Expected handling |
|---|---|
| A save state taken with difficulty A, loaded with the row on B | The row wins: slot re-sends the switch after the state load |
| Paddle or keypad game | Plays with the joystick map; listed in issue 142 |

## Acceptance
- [ ] `task check` green.

## Device check (RG34XXSP)
Part of issue 132.

## References
- ADR 0095; docs/research/atari-plan.md
