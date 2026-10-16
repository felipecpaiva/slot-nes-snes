# 0051. Store the Sega shader settings in their own file, outside slot.state

- Status: Accepted
- Date: 2026-10-15
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0034](0034-durability-shader-lines.md), [ADR 0043](0043-retro-shader-rows-on-v1-7-0-menus.md), [ADR 0025](0025-shelf-memory.md), [issue 50](../../.github/issues/50-sega-tracking.md)

## Context

NES and SNES store their shaders as `shader_nes` and `shader_snes` in `SlotState`. Upstream's
`durability.rs` builds a full `SlotState` literal, and ADR 0034 allows exactly those two lines
there (named test site f). Three more fields for Game Gear, Master System and Mega Drive would
break that literal again and widen site (f).

## Decision

The Game Gear, Master System and Mega Drive shader choices live in a file of our own under
`Config/` (the pattern ADR 0025 used for shelf memory), written by the existing state writer.
`SlotState` gains no field, and named test site (f) stays exactly as ADR 0034 defines it.

Built in patch 0027 (`sega-shaders`): the file is `Config/sega_shaders.txt`, three lines
`gg=`, `sms=` and `md=` with a retro shader name each (`crates/slot-store/src/sega_shader.rs`). The
list offered is the NES and SNES one, `Shader::RETRO` (Off, Grid, Dot, Sharp, Scanlines, crt-pi,
crt-1tap, Line, Pixel), on the Screen page (Game Gear, Master System, Mega Drive rows) and in game
(the Shader row and SELECT+A/B). The default for each system is Off, and while all three are Off
and no file exists, none is written.

## Consequences

- `durability.rs` and the upstream test guard are unchanged; slot.state stays byte-identical, so
  older builds and upstream read the card as before.
- A second small file to read at start and write on change; a missing or damaged file means the
  default shader per platform.
- NES and SNES keep their fields in `SlotState`; only the new platforms use the side file.
