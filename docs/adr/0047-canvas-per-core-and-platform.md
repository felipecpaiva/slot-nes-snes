# 0047. Choose the canvas per core and platform, so Game Gear runs at 3x like Game Boy

- Status: Accepted. Amends [0004](0004-fixed-2x-canvas.md)
- Date: 2026-10-15
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0050](0050-genesis-plus-gx-for-sega.md), [issue 50](../../.github/issues/50-sega-tracking.md), [issue 51](../../.github/issues/51-platform-gg.md), [ADR 0015](0015-hostextra-canvas-only.md), [ADR 0016](0016-set-game-canvas-every-frame.md)

## Context

ADR 0004 makes `Core::canvas()` the canvas truth: mGBA and gpSP get 240x160 at 3x, the NES and
SNES cores 360x240 at 2x. That works while every core serves one canvas. Genesis Plus GX serves
three systems (ADR 0050): Game Gear outputs 160x144, the Game Boy size, while Master System
(256x192) and Mega Drive (320x224, 256x224) need the 2x canvas. With the canvas keyed by core
alone, Game Gear would sit at 2x in 360x240 (320x288 on the panel), visibly smaller than a
Game Boy cart.

## Decision

The canvas is a function of the core and the seated platform: `Core::canvas` gains the platform
argument. Game Gear on Genesis Plus GX gets 240x160 at 3x, like Game Boy on mGBA. Master System
and Mega Drive get 360x240 at 2x. Every existing pair keeps the canvas it has today. The canvas
is still chosen once at open and carried in `HostExtra` (ADR 0015).

## Consequences

- Game Gear matches Game Boy size and can use the Game Boy shader list.
- The change lives in our own canvas code; no upstream file gains a hunk for it.
- A test per pair pins the canvas, so a later core added for two platforms cannot fall back to
  the wrong one silently.
- Mega Drive switches between 320 and 256 wide mid-game. The centring copy must clear the
  borders on a width change; a test alternates 320 and 256 wide frames.
