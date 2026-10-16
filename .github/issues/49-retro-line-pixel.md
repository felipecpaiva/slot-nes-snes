---
title: "Patch: Add Line and Pixel shaders for NES and SNES and make Scanlines sharp"
phase: 3
area: video
type: feature
size: S
depends_on: [46-retro-shaders]
---

## Why
MinUI's picture on H700 handhelds is well liked. Research (docs/research/minui-screen-effects.md) found two looks we lacked: MinUI's Line (a hard scanline locked to panel rows) and NextUI's Pixel Perfect Sharp (`pixellate.glsl`). Our Scanlines sampled nearest and shimmered at the 2.8125x Stretch width. Decision: [ADR 0036](../../docs/adr/0036-line-pixel-sharp-scanlines.md).

## Scope
`patches/0019-retro-line-pixel.patch`:
- [x] Line after crt-1tap (key `line`): the Sharp picture with the top panel row of every repeat at 50%, repeat = max(2, floor(panel rows per source line)), counted from the picture top with `gl_FragCoord`. Our own code; no MinUI code or images (no licence).
- [x] Pixel after Line (key `pixel`): single-pass port of libretro `pixellate.glsl`, 4 nearest reads, gamma by squaring and a square root. Full ISC style notice in the GLSL comment and in `licenses/retro-shaders.txt`.
- [x] Scanlines samples `sharp()` instead of nearest; name and key unchanged.
- [x] `warm()` draws all six retro modes (`RETRO_MODES`, next to `RETRO_FRAG`).
- [x] Only `slot-store/src/retro_shader.rs` and `slot-gfx/src/pipeline/retro.rs` change in source; zero new upstream hunks.
- [x] Skipped, with reasons in ADR 0036: Crisp (same as Sharp), Soft, MinUI Grid, a separate sharpness axis.

## Tests
| ID | File | Asserts |
|---|---|---|
| T77 | `slot-gfx/tests/retro_pipeline.rs` | all six modes build and change a stretched NES frame deterministically, each different from Off and the others |
| T80 | `slot-gfx/tests/retro_pipeline.rs` | Line halves the top panel row of each repeat, down one column, at 2x and SNES Stretch (repeat 2) and at 3x (repeat 3) |
| T81 | `slot-gfx/tests/retro_pipeline.rs` | Pixel equals Off at an exact 2x |
| T82 | `slot-gfx/tests/retro_pipeline.rs` | Scanlines at NES Stretch shows blended edges where Off shows only two values (it samples Sharp) |
| T78 | `slot-store/tests/retro_shader_state.rs` | nine-step order, names, labels, slot.state round-trip |
| T79 | `slot-ui/tests/retro_faces.rs` | quick menu faces and toast text for Line and Pixel |
| - | `slot/tests/quick_retro_shader.rs`, `slot/tests/nes_snes_shader.rs` | quick menu and SELECT+A/B cycle the nine steps, a step back from Off lands on Pixel |

Each new test was seen red with its line broken: Scanlines back to nearest, Line repeat fixed at 2, Line dark row moved down one, Pixel without the square root.

## Acceptance
- [x] task check green, harness compare 0 diffs (GBA, GB, GBC byte-identical).
- [x] Zero new upstream touch points (`task diffsurface` unchanged).
- [x] On the RG34XXSP Line and Pixel build and add no measurable per-frame cost (`task perf:play`, one run per new mode against Off).

## Device check (RG34XXSP)
- [x] In an NES and an SNES game, Quick menu, Screen, shader row: cycle Off, Grid, Dot, Sharp, Scanlines, crt-pi, crt-1tap, Line, Pixel.
- [x] Line: dark rows even and evenly spaced at Stretch and Actual, one dark row on top of each NES line at 2x.
- [x] Scanlines no longer shimmers when the picture scrolls sideways at Stretch.
