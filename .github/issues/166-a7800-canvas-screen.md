---
title: "Give the 7800 the 360x240 canvas with a crop rule for PAL and its own Screen section"
phase: 14
area: video
type: feature
size: S
depends_on: [164-a7800-options]
---

## Why
ProSystem hands 320x223 NTSC (fits 360x240, 640x446 on the panel) and 320x272 PAL, which `copy_centred` would halve.

## Scope
- [ ] Canvas 360x240 at 2x.
- [ ] PAL 272 rows: Actual crops to the middle 240, Stretch scales to 240.
- [ ] A7800 Screen section: Shader, Picture, PAL Speed (issue 168), BIOS (issue 165), Left and Right difficulty (issue 167).

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `a7800_canvas.rs` | 320x223 centred unscaled; 320x272 cropped from the middle; Stretch fills |

## Edge cases
| Case | Expected handling |
|---|---|
| A PAL game draws its HUD in the cropped rows | Device gate looks; Stretch is the escape |

## Acceptance
- [ ] `task check` green.

## Device check (RG34XXSP)
Part of issue 170.

## References
- ADR 0095; docs/research/atari-plan.md
