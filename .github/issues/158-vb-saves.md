---
title: "Virtual Boy saves: the ordinary .sav for the 64 KB cart RAM"
phase: 16
area: platform
type: chore
size: S
depends_on: [155-platform-vb]
---

## Why
Beetle VB gives every cart 64 KB of cart RAM, so the .sav path must hold it.

## Scope
- [x] Tests only: the .sav is written on eject, survives a reinsert, a RetroArch .srm loads.

## Tests
| ID | File | Asserts |
|---|---|---|
| V1 | `vb_saves.rs` | eject writes the cart RAM, reinsert reads it, a never-saving cart leaves 64 KB of zeros, .srm loads |

## Edge cases
| Case | Expected handling |
|---|---|
| A game that never saves | a 64 KB .sav of zeros, like a HuCard |

## Acceptance
- [x] V1 passes.

## Device check (RG34XXSP)
Issue 162.

## References
- ADR 0097; docs/cart-art/VB.md
