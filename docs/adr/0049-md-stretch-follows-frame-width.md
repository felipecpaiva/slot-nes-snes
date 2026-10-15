# 0049. Make Mega Drive Stretch follow the live frame width

- Status: Accepted. Amends [0046](0046-retro-stretch-crops-height.md)
- Date: 2026-10-15
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0022](0022-nes-snes-default-stretch.md), [ADR 0018](0018-source-rect-takes-canvas.md), [issue 53](../../.github/issues/53-platform-md.md)

## Context

Stretch crops the canvas to `Platform::picture()` (ADR 0022, 0046), a fixed size per platform.
Mega Drive games use H40 (320x224) or H32 (256x224), and some switch between them mid-game. A
fixed 320x224 picture leaves black side bars on every H32 game in Stretch; a fixed 256 would crop
H40 games.

## Decision

On the Mega Drive shelf the Stretch rect uses the width of the last frame the core produced
(320 or 256) with the 224 rows, cropping both axes as NES and SNES do (ADR 0046). Mega Drive
defaults to Stretch like NES and SNES, not to Actual.

## Consequences

- H32 and H40 games both fill the panel in Stretch, with no side bars.
- A mid-game width change changes the rect on the next frame; the picture rescales once at the
  switch. Accepted, it matches what the game does on hardware.
- `video_mode` needs the last frame size, which the canvas code already knows; GBA, GB, GBC, NES
  and SNES keep their fixed pictures and their tests.
- Interlace mode 2 (448 rows) is out of scope here: the core option stays `single field`.
