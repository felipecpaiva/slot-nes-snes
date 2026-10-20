---
title: "Map the 32X pad as the Mega Drive six-button pad"
phase: 15
area: input
type: feature
size: S
depends_on: [145-platform-s32x]
---

## Why
32X games use the Mega Drive pad.

## Scope
- [x] Tests only: passes_xy_through and owns_shoulders already match Mega Drive.

## Tests
| ID | File | Asserts |
|---|---|---|
| I1 | `s32x_input.rs` | every button equals Mega Drive's; X, Y, L1 and R1 reach the core; slot keeps none |

## Edge cases
| Case | Expected handling |
|---|---|
| A three-button-only game | six-button pad, as Genesis Plus GX gives the Mega Drive |

## Acceptance
- [x] I1 passes.

## Device check (RG34XXSP)
Issue 152.

## References
- ADR 0096; docs/cart-art/S32X.md
