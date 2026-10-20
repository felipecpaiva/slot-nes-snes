---
title: "Map the Virtual Boy pad: the right stick as the right D-pad, an ABXY fallback"
phase: 16
area: input
type: feature
size: M
depends_on: [175-platform-vb]
---

## Why
The Virtual Boy has two D-pads; the device has a D-pad and two analog sticks (ADR 0068).

## Scope
- [x] Stick (default): Beetle VB plugged as a plain pad, so it reads the right stick; X and Y never reach the core (X is its low battery switch).
- [x] ABXY: X, A, B, Y are right up, right, down, left; A and B on R2 and L2, which go to the game the PS1 way, latched at start.
- [x] `ButtonMask::L3` and `R3` (ids 14 and 15).

## Tests
| ID | File | Asserts |
|---|---|---|
| I1 | `vb_input.rs` | both maps, every button and the stick reach the game through a generated cart that reads the pad, L2 and R2 stay slot's in Stick mode and go to the game in ABXY mode |

## Edge cases
| Case | Expected handling |
|---|---|
| X pressed | never reaches the core in either mode |
| ABXY then a GBA game | the GBA game gets L2 and R2 as rewind and fast forward (issue 180) |

## Acceptance
- [x] I1 passes; mGBA and gpSP still see centred sticks.

## Device check (RG34XXSP)
Issue 182.

## References
- ADR 0097; docs/cart-art/VB.md
