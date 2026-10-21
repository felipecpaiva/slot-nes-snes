---
title: "Test GBA after a flipped disk, and resume"
phase: 18
area: tests
type: test
size: S
depends_on: [198-fds-disk]
---

## Why
slot presses the core's L and R on this shelf; a GBA game afterwards must get exactly a GBA only run.

## Scope
- [x] GBA after a flipped disk: same input, frame and picture.
- [x] A disk resumes as a disk, never as a NES cart with the same name.

## Tests
| ID | File | Asserts |
|---|---|---|
| T1 | `fds_then_gba.rs` | input and picture equal a GBA only run |
| T2 | `resume_platform.rs` | Fds in the list |

## Edge cases
| Case | Expected handling |
|---|---|
| (none) | |

## Acceptance
- [x] T1 and T2 pass.

## Device check (RG34XXSP)
Issue 202.

## References
- ADR 0101
