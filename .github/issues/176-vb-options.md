---
title: "Set the Beetle VB options: anaglyph with the preset off, the right stick as the right D-pad"
phase: 16
area: cores
type: feature
size: S
depends_on: [175-platform-vb]
---

## Why
The flat single picture and the right stick both come from core options, and 3D mode needs a restart.

## Scope
- [x] `BEETLE_VB`: vb_3dmode anaglyph, vb_anaglyph_preset disabled, vb_right_analog_to_digital enabled, vb_opposite_directions disabled, vb_cpu_emulation fast.

## Tests
| ID | File | Asserts |
|---|---|---|
| O1 | `vb_options.rs` | every option answered with its own value, every key and value declared by the pin |
| O2 | `vb_core.rs` | the preset off shows the left eye alone; a real preset shows both eyes |

## Edge cases
| Case | Expected handling |
|---|---|
| A pin bump renames a value | O1 fails |

## Acceptance
- [x] O1 and O2 pass.

## Device check (RG34XXSP)
Issue 182.

## References
- ADR 0097; docs/cart-art/VB.md
