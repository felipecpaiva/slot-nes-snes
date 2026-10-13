# 0026. Add Sharp, Scanlines, crt-pi and crt-1tap for NES and SNES

- Status: Accepted
- Date: 2026-10-13
- Deciders: maintainer (Felipe Paiva)
- Related: [retro-shaders.md](../research/retro-shaders.md), [patch 0020](../../patches/0020-retro-shaders.patch)

## Context

NES and SNES had only Off, Grid and Dot. The research in `docs/research/retro-shaders.md` ranked
candidates by use on handheld firmwares and cost on the Mali-G31.

## Decision

NES and SNES get four more shaders after Off, Grid, Dot: Sharp (sharp-bilinear-simple), Scanlines
(scanlines-sine-abs), crt-pi and crt-1tap, in that order in `Shader::RETRO`. GBA, GB and GBC lists
are unchanged and their `slot.state` keys refuse the new names.

## Consequences

- Sharp fixes the 2.8125x Stretch shimmer; the other three are the most used light scanline and
  CRT looks on H700 firmwares.
- 2026-10-13 device run: all four build on the Mali-G31 and add no measurable per-frame cost
  ([DEVICE-GATE.md](../DEVICE-GATE.md)).
- Each new mode showed one long first present, handled by [0031](0031-warm-retro-shaders-at-boot.md).
