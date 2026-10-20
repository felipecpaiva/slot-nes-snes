---
title: "Test the 32X with a generated cart whose SH-2s must answer, and Mega Drive after 32X"
phase: 15
area: tests
type: test
size: S
depends_on: [144-s32x-core-build]
---

## Why
A generated cart only proves 32X emulation if something only the 32X produces is asserted.

## Scope
- [x] Core facts (patch 0090): the 68000 paints only after the master SH-2's M_OK.
- [x] Mega Drive after 32X equals Mega Drive only (patch 0096); resume keeps the 32X platform.

## Tests
| ID | File | Asserts |
|---|---|---|
| T1 | `s32x_core.rs` | boot, 60 fps, 44100 Hz, 320x224 in 360x240, state round trip, save RAM |
| T2 | `s32x_then_md.rs` | input, frame, rect and shader equal to a Mega Drive only run |

## Edge cases
| Case | Expected handling |
|---|---|
| ADEN never written | the SH-2s never answer, nothing paints (the break check) |

## Acceptance
- [x] T1 and T2 pass.

## Device check (RG34XXSP)
Issue 152.

## References
- ADR 0096; docs/cart-art/S32X.md
