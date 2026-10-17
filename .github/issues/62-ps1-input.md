---
title: "Hand L1, R1, L2 and R2 to PS1 games and map the PlayStation face buttons"
phase: 8
area: input
type: feature
size: S
depends_on: [58-platform-ps1]
---

## Why
Step 9. v1 is the digital pad with all four shoulders (ADR 0068).

## Scope
- [x] `owns_shoulders` false for PS1 (slot does not own L1 and R1, so they go to the game, as SNES and MD); in-game picture toggle on SELECT+X (ADR 0007, 0068).
- [x] `owns_triggers` policy, false for PS1 only (slot keeps L2 and R2 everywhere else), checked at the L2/R2 arms of `gesture.rs` (gmaster1998's toggle shape). Every other platform keeps rewind and FF.
- [x] `ButtonMask` bits 12 and 13 (L2, R2) reach `input_state` for PS1.
- [x] Face buttons by position: Cross B, Circle A, Square Y, Triangle X. Turbo: pass-through.
- [x] Fast-forward on SELECT+R2 (maintainer's choice, ADR 0066); SELECT+R2 never reaches the game.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot/tests/ps1_input.rs`, `slot-input/tests/ps1_gesture.rs` | L1, R1, L2 and R2 reach the core on PS1; SELECT+X flips the picture; on GBA they still start rewind and FF; face mapping |

## Edge cases
| Case | Expected handling |
|---|---|
| L2 held while ejecting | Released to the core before the eject (`ps1_input.rs`) |

## Acceptance
- [x] Tests green; GBA harness compare at 0 diffs.

## Device check (RG34XXSP)
A game that uses L2 and R2 (a racer or Tekken 3) in play.

## References
- ADR 0066, 0068
