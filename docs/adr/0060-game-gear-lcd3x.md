# 0060. Offer upstream's LCD3x for Game Gear, right after Off

- Status: Accepted. Amends 0051
- Date: 2026-10-16
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0050](0050-canvas-per-core-and-platform.md), [ADR 0051](0051-sega-shaders-outside-slot-state.md), [ADR 0031](0031-warm-retro-shaders-at-boot.md), [issue 51](../../.github/issues/51-platform-gg.md), patches/0031-gg-lcd.patch

## Context

The Game Gear is a colour LCD handheld. ADR 0050 puts it on the Game Boy geometry: a 240x160
canvas drawn at exactly 3x on the 720x480 panel, with the 160x144 picture in the middle. ADR 0051
gave it the NES and SNES list, `Shader::RETRO`, which has no LCD look. Upstream already ships one
for the Game Boy and Game Boy Color, LCD3x (`Shader::Lcd3x`, mode 1 of `GAME_FRAG` in
`slot-gfx/src/shaders.rs`): a per-texel sine mask that gives each source pixel three subpixel
columns and a faint row gap, made for exact 3x. The maintainer rule is that every system has its
own filter section; a shared list may be reused, but the setting is per system.

## Decision

Game Gear reuses upstream's LCD3x as is. `Shader::GG` is the shared retro list with `Lcd3x` right
after `Off` (Off, LCD3x, Grid, Dot, Sharp, Scanlines, crt-pi, crt-1tap, Line, Pixel), the place
LCD3x has in upstream's GB and GBA lists. Off stays the default. `Platform::Gg.shader_choices()`
returns it, and it drives the Game Gear Screen row, the in-game Shader row, SELECT+A/B and the
`gg=` line of `Config/sega_shaders.txt` (`gg=lcd3x`). NES, SNES, Master System and Mega Drive keep
`Shader::RETRO`; a `sms=lcd3x` or `md=lcd3x` line reads as Off.

No shader code changes. `frontend.rs` already maps `Shader::Lcd3x` to `ScreenEffect::Lcd3x` for
every platform, and the `u_pic` gate in `GAME_FRAG` keeps the border black. So `GAME_FRAG`,
`lcd3x.rs`, `Shader::GB` and `Shader::GBA` are untouched and GB, GBC and GBA draw byte for byte as
before. No new retro mode was needed, so `RETRO_MODES` and `warm()` stay at 6: ADR 0031's warm-up
is for the retro program, which nothing draws before a retro game starts, while `GAME_FRAG` is the
program every game already draws with.

## Consequences

- The Game Gear gets the same LCD look as the Game Boy at no shader cost; the only app.rs change is
  one token on a line patch 0027 already owns (`Shader::RETRO` to `Shader::GG` on the Game Gear
  arm of the SELECT+A/B list).
- LCD3x is upstream's RGB stripe mask, tuned for the Game Boy, not a model of the Game Gear's
  own panel. A Game Gear specific mask would be a new retro mode in `RETRO_FRAG` (and a seventh
  warm-up draw); not done until someone asks for it.
- A card written by this build with `gg=lcd3x` reads as Off on an older build (its reader only
  accepts `Shader::RETRO`); nothing else in the file changes.
- On a rebase, check that upstream's `Shader::Lcd3x` and mode 1 of `GAME_FRAG` still exist.
