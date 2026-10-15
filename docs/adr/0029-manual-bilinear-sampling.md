# 0029. Sample bilinearly by hand in the shaders that expect linear filtering

- Status: Accepted
- Date: 2026-10-13
- Deciders: maintainer (Felipe Paiva)
- Related: [patch 0017](../../patches/0017-retro-shaders.patch), [retro-shaders.md](../research/retro-shaders.md)

## Context

The game texture is `GL_NEAREST`. Sharp, crt-pi and crt-1tap are written for linear filtering.
Switching the texture to `GL_LINEAR` for those modes would need a hunk in `draw_source`.

## Decision

Those three shaders sample bilinearly by hand, 4 nearest reads, instead of switching the game
texture to `GL_LINEAR`.

## Consequences

- Zero upstream hunks, and no filter state to restore for GBA.
- Cost: 4 reads per pixel instead of 1 for those three modes, unmeasured on the device when decided.
- The 2026-10-13 shader device run found no measurable per-frame cost for any retro mode
  ([DEVICE-GATE.md](../DEVICE-GATE.md)).
