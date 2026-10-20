---
title: "Test the Virtual Boy with a generated two-eye cart, and GBA after the Virtual Boy"
phase: 16
area: tests
type: test
size: S
depends_on: [174-vb-core-build]
---

## Why
A real cart is never committed; a generated cart proves what each eye shows, and the triggers latch must reset.

## Scope
- [x] Core half: `vb_core.rs` and `vb_common` (patch 0102).
- [x] Platform half: `vb_then_gba.rs` and the resume test (patch 0108).

## Tests
| ID | File | Asserts |
|---|---|---|
| T1 | `vb_then_gba.rs` | a GBA game after a Virtual Boy game on ABXY gets the GBA-only input, fast forward and picture |
| T2 | `resume_platform.rs` | a Virtual Boy cart resumes as one |

## Edge cases
| Case | Expected handling |
|---|---|
| The latch kept after the Virtual Boy | T1 fails (checked by breaking it) |

## Acceptance
- [x] T1 and T2 pass.

## Device check (RG34XXSP)
Issue 182.

## References
- ADR 0097; docs/cart-art/VB.md
