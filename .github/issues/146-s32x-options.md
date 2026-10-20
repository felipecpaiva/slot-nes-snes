---
title: "Set the PicoDrive options: six-button pad, region Auto, dynarec on"
phase: 15
area: cores
type: feature
size: S
depends_on: [145-platform-s32x]
---

## Why
PicoDrive's port 1 defaults to the three-button pad; the Mega Drive on Genesis Plus GX gets six buttons.

## Scope
- [x] `PICODRIVE` list in core_options_policy.rs; frameskip `auto` like every core.

## Tests
| ID | File | Asserts |
|---|---|---|
| O1 | `s32x_options.rs` | every key answered with its value and declared by the pin (drc only on aarch64) |

## Edge cases
| Case | Expected handling |
|---|---|
| The Mac build has no picodrive_drc | slot answers it anyway; the core never asks |

## Acceptance
- [x] O1 passes.

## Device check (RG34XXSP)
Issue 152.

## References
- ADR 0096; docs/cart-art/S32X.md
