---
title: "Map the 7800 joystick, buttons and console switches"
phase: 14
area: input
type: feature
size: M
depends_on: [163-platform-a7800]
---

## Why
ProSystem reads button 1 on RetroPad B and 2 on A, and counts every switch only while held: L and R difficulty, X Reset, SELECT, START Pause (tested). Held clears the SWCHB bit, so holding is B.

## Scope
- [ ] D-pad joystick; B button 1, A button 2; X and Y turbo 1 and 2.
- [ ] SELECT Select, START Pause.
- [ ] Left and Right difficulty rows (A / B, default B): slot holds L or R every frame while B is chosen.
- [ ] An in-game menu row "Reset console" holds X for 3 frames (X is turbo).

## Tests
| ID | File | Asserts |
|---|---|---|
| (done) | `atari_core.rs` | every switch momentary (patch 0099) |
| (new) | `a7800_input.rs` | difficulty B holds the bit every frame; Reset row pulses X; turbo still works |

## Edge cases
| Case | Expected handling |
|---|---|
| A save state then a row change | The row is input every frame, so it applies at once |

## Acceptance
- [ ] `task check` green.

## Device check (RG34XXSP)
Part of issue 170.

## References
- ADR 0095; docs/research/atari-plan.md
