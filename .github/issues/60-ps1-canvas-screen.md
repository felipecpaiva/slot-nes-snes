---
title: "Give PS1 a 640x480 canvas and its own Screen section with Shader and Picture rows"
phase: 8
area: video
type: feature
size: M
depends_on: [59-ps1-options]
---

## Why
Step 7. ADR 0065: a fixed 640x480 canvas (the 1:1 4:3 picture on the 720x480 panel), its own budget, its own Screen section.

## Scope
- [x] `Core::canvas(PcsxRearmed, Ps1) = (640, 480)`; horizontal resample to 640 (exact for 320 and 640), row doubling for 240-line frames, border clear on a size change. The RGB565 path shared with gpSP stays bit-identical; PS1 gets its own path.
- [x] 4:3 thumbnails and polaroids for PS1.
- [x] `SCREEN_PS1` with a Shader row (the shared retro list) and a Picture row (Actual default, Stretch; no Crop). Shader stored in its own `Config/` file (ADR 0051 pattern), picture default in `Config/picture.txt`.
- [x] Named test sites (g) and (h) gain the PS1 Screen tokens, (b) and (e) the platform tokens (ADR 0055). CONTRIBUTING.md updated in the same patch.
- [x] docs/PERFORMANCE.md: a PS1 frontend budget line, convert at most 2 ms a frame and convert plus upload under about 3 ms (ADR 0065).

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot/tests/ps1_canvas.rs`, `slot-retro/src/canvas.rs`, `slot-gfx/tests/ps1_pipeline.rs` | canvas is 640x480; 320x240 maps 2x; 256 and 512 widths fill 640; 640x480 interlaced passes 1:1; alternating sizes clear the borders |
| (new) | `slot/tests/ps1_screen.rs` (patch 0034) | PS1 Screen page rows and their stored values |

## Edge cases
| Case | Expected handling |
|---|---|
| Frame wider than 640 or taller than 480 | Halved, never written past the canvas |
| A retro shader over budget at 640x480 | Hidden for PS1 only, recorded here |

## Acceptance
- [x] Tests green; GBA harness compare at 0 diffs; touch-point map regenerated.

## Device check (RG34XXSP)
Convert under 2 ms and convert plus upload under about 3 ms; each shader timed on a 512x240 game.

## References
- ADR 0050, 0051, 0055, 0061, 0065
