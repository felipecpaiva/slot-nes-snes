# 0036. Add Line and Pixel and make Scanlines sharp

- Status: Accepted. Amends [0026](0026-four-more-retro-shaders.md)
- Date: 2026-10-14
- Deciders: maintainer (Felipe Paiva)
- Related: [minui-screen-effects.md](../research/minui-screen-effects.md), [patch 0022](../../patches/0022-retro-line-pixel.patch), [issue 49](../../.github/issues/49-retro-line-pixel.md)

## Context

MinUI's picture on H700 handhelds is well liked. The research in
`docs/research/minui-screen-effects.md` compared its Screen Effect and Sharpness options, and
NextUI's shader presets, with our seven NES/SNES modes. Two looks were missing: MinUI's Line (a
hard scanline locked to panel rows) and NextUI's Pixel Perfect Sharp (`pixellate.glsl`). Our
Scanlines sampled the picture nearest, so it shimmers at the 2.8125x Stretch width.

## Decision

- **Line** (key `line`), after crt-1tap: the `sharp()` picture with the top panel row of every
  repeat at 50%. Repeat = max(2, floor(panel rows per source line)), counted from the picture's top
  edge with `gl_FragCoord`. The off-screen buffer is 720x480 and maps 1:1 to the RG34XXSP panel
  (`fbo.rs` `canvas_size`, the same assumption crt-pi's mask makes), so the stripes are panel rows.
  At NES and SNES Stretch the repeat is 2, which MinUI only reaches at Native (its Aspect repeat is 3).
- **Pixel** (key `pixel`), after Line: a single-pass port of libretro `pixellate.glsl`, 4 nearest
  reads weighted by area, gamma 2.0 by squaring and a square root instead of `pow`.
- **Scanlines** keeps its name and key but samples `sharp()` instead of nearest.
- `RetroShader::ALL` grows to 6, `Shader::RETRO` to 9. Only our two files change (ADR
  [0027](0027-retro-shaders-pay-once.md)), zero upstream hunks. `warm()` draws every mode, counted
  by a `RETRO_MODES` constant next to `RETRO_FRAG`, because slot-gfx cannot see slot-store.

Skipped:
- Crisp: integer prescale then linear is what our Sharp already does at 720x480.
- Soft: plain bilinear blur.
- MinUI Grid: slot's Grid covers it, and it is an LCD look on CRT era systems.
- A separate sharpness axis: about 8 to 12 upstream hunks (`slot_state.rs`, a quick menu row,
  `GAME_FRAG`) for combinations Line and Scanlines now bake in.

Licences: MinUI has no licence and NextUI is PolyForm Noncommercial 1.0.0, so no code or images
come from either; Line is our own code. `pixellate.glsl` is taken from libretro/glsl-shaders under
its ISC style notice, kept in full in the GLSL comment and in `licenses/retro-shaders.txt`.

## Consequences

- NES and SNES get a beat free, shimmer free scanline and the sharpest shimmer free scaler, each
  at 4 reads, the cost of Sharp.
- Anyone who picked Scanlines sees a sharper picture under the same lines.
- Line on hires (448 or 478 line) pictures still darkens every other panel row.
- Needs device: a `task perf:play` run per new mode, and a look at Line's row alignment.
- On each rebase: if upstream changes the off-screen buffer size or the final blit, recheck the 1:1
  claim above.
