---
title: "Patch: Add Sharp, Scanlines, crt-pi and crt-1tap shaders for NES and SNES"
phase: 3
area: video
type: feature
size: M
depends_on: [21-shaders, 44-quick-menu-retro-shaders]
---

## Why
NES and SNES had only Off, Grid and Dot (upstream's effects). The maintainer asked for the best and most used retro shaders. Research (docs/research/retro-shaders.md) ranked the light ones the H700 firmwares ship by default and that fit slot's single-pass GLSL ES 1.00 pipeline on the Mali-G31.

## Scope
`patches/0017-retro-shaders.patch`:
- [x] Four modes after Off, Grid, Dot in `Shader::RETRO`: Sharp (sharp-bilinear-simple, public domain), Scanlines (scanlines-sine-abs, public domain), crt-pi (GPL-2+), crt-1tap (CC0). NES and SNES only; GBA, GB and GBC lists unchanged.
- [x] "Pay once" hook: one payload variant per enum (`Shader::Retro`, `Toast::Retro`, `QuickValue::Retro`, `ScreenEffect::Retro(u8)`). The list, names and GLSL live in our files (`slot-store/src/retro_shader.rs`, `slot-gfx/src/pipeline/retro.rs`), so the next shader touches no upstream file.
- [x] Own GL program, so upstream's `GAME_FRAG` stays byte-identical; if it fails to build, NES/SNES draw plain.
- [x] Bilinear by hand (4 nearest reads) for the modes that expect linear filtering; no filter state change.
- [x] Licences in `licenses/retro-shaders.txt`, shipped in the zip.
- [x] Warm-up: the program draws each mode once off screen when it is built (PR #92), so the driver's first-draw cost is paid at boot, not in a game.

## Tests
| ID | File | Asserts |
|---|---|---|
| T77 | `slot-gfx/tests/retro_pipeline.rs` | every mode builds and changes a stretched frame, deterministically; Sharp equals Off at an exact 2x |
| T78 | `slot-store/tests/retro_shader_state.rs` | order, names, slot.state round-trip, old values load, GBA/GB keys refuse retro names |
| T79 | `slot-ui/tests/retro_faces.rs` | quick menu faces, labels, toast text |

## Acceptance
- [x] task check green, harness compare 0 diffs (GBA, GB, GBC byte-identical).
- [x] On the RG34XXSP every mode builds and adds no measurable per-frame cost (docs/DEVICE-GATE.md, 2026-10-13).
- [x] Boot cost of building and warming the program (about 150 ms) accepted by the maintainer.

## Device check (RG34XXSP)
In an NES and an SNES game, Quick menu, Screen, shader row: cycle Off, Grid, Dot, Sharp, Scanlines, crt-pi, crt-1tap.
