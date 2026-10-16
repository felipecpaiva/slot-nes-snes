# 0027. Add retro shaders through one payload variant per enum

- Status: Accepted
- Date: 2026-10-13
- Deciders: maintainer (Felipe Paiva)
- Related: [patch 0017](../../patches/0017-retro-shaders.patch), [retro-shaders.md](../research/retro-shaders.md)

## Context

In the upstream design each new shader would cost about 13 upstream hunks. upstream already has
the pattern `Toast::Palette(GbPalette)`.

## Decision

One payload variant per enum that needs it: `Shader::Retro(RetroShader)`,
`Toast::Retro(RetroShader)`, `QuickValue::Retro(RetroShader)` and `ScreenEffect::Retro(u8)`. The
list, names, labels and GLSL live in `slot-store/src/retro_shader.rs` and
`slot-gfx/src/pipeline/retro.rs`.

## Consequences

- Adding another shader touches only those two files.
- slot-gfx cannot see slot-store, so `ScreenEffect` carries the shader's place in
  `RetroShader::ALL`.
- `Toast::all()` and `QuickValue::ALL` stay upstream's lists (upstream tests pin them);
  `Toast::every()` and `QuickValue::every()` append the retro faces, and `index()` places them after.
