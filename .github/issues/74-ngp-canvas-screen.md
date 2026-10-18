---
title: "Give NGP a 240x160 canvas and its own Screen section with Shader and Picture rows"
phase: 9
area: video
type: feature
size: S
depends_on: [73-ngp-options]
---

## Why
Step 6. Every system gets its own Screen section (the maintainer's rule; ADR 0061, 0065). NGP is an exact 3x fit, so the picture work is small.

## Scope
- [ ] `Core::canvas(MednafenNgp, Ngp) = (240, 160)`: the 160x152 frame centred at (40, 4), Actual 480x456 on the panel, Stretch to 720x480.
- [ ] `SCREEN_NGP` section with a Shader row (Off, LCD3x, then the shared retro list; the ADR 0060 Game Gear precedent for LCD3x) stored in its own `Config/` file (ADR 0051), and a Picture row (Actual default, Stretch; no Crop, NGP has no overscan) in `Config/picture.txt` (ADR 0061).
- [ ] **No PAL Speed row**: 60.25 fps is inside ADR 0071's 2 fps window and NGP has no PAL variant.
- [ ] The in-game quick menu Shader row offers the same list.
- [ ] Named test sites (g) and (h) gain the NGP Screen tokens (ADR 0055); CONTRIBUTING.md in the same patch.
- [ ] Credit nelynes/slotPlus a8eae4c (Screen page) and 1ef7226 (stretch both ways).

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `ngp_screen.rs` | the section lists Shader and Picture only; values round-trip through their files |
| (new) | `ngp_canvas.rs` | every pixel of the 160x152 picture at (40, 4), black bars, on the real core |

## Edge cases
| Case | Expected handling |
|---|---|
| `Config/picture.txt` has no NGP line | Actual |
| An unknown shader value in the NGP file | Off, logged |

## Acceptance
- [ ] `task check` green; frontend cost inside the GBA budget (same 240x160 path).

## Device check (RG34XXSP)
LCD3x and Stretch look right on a real cart (issue 79).

## References
- ADR 0050, 0051, 0060, 0061, 0071, 0090; docs/research/ngp-plan.md section 4
