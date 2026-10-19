---
title: "Give the 2600 the 360x240 canvas with doubled columns, a crop rule for tall frames, and its own Screen section"
phase: 14
area: video
type: feature
size: M
depends_on: [127-a2600-options]
---

## Why
Stella hands 160 columns and the game's own rows: 210 by default, 250 PAL, 220 to 256 for 7 of the maintainer's NTSC dumps (tested and from Stella's database). In the 360x240 canvas a 160-wide frame would be squeezed, and `copy_centred` halves anything over 240 rows.

## Scope
- [ ] Canvas 360x240 at 2x (ADR 0050). A 2600-only copy rule doubles each column (160 to 320), so 160x210 shows as 640x420 centred.
- [ ] Rows over 240: Actual crops to the middle 240, never halves. Stretch scales the frame to the canvas.
- [ ] A2600 Screen section: Shader (retro list), Picture (Actual, Stretch), PAL Speed (issue 130), Left and Right difficulty, TV type (issue 129).

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `a2600_canvas.rs` | 160x210 lands 320x210 centred; 160x250 lands 320x240 cropped from the middle; Stretch fills |
| (new) | render test | Screen section rows present |

## Edge cases
| Case | Expected handling |
|---|---|
| A game changes its row count mid-play (some do on reset) | Each frame is placed from its own size; margins cleared |

## Acceptance
- [ ] `task check` green; GBA harness 0 diffs.

## Device check (RG34XXSP)
Part of issue 132: crop rows on a PAL dump.

## References
- ADR 0095; docs/research/atari-plan.md
