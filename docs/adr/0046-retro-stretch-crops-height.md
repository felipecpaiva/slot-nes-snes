# 0046. Keep the NES and SNES stretch crop on both axes

- Status: Accepted. Amends [0018](0018-source-rect-takes-canvas.md). Amended by [0052](0052-md-stretch-follows-frame-width.md) and [0062](0062-crop-overscan-picture.md)
- Date: 2026-10-15
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0038](0038-rebase-to-slot-v1-7-0.md), [ADR 0022](0022-nes-snes-default-stretch.md), [patch 0004](../../patches/0004-canvas.patch)

## Context

slot v1.7.0 ("GB stretch only widens") changed `video_mode::source_rect` to crop only the width
and keep the full 160 rows for Game Boy. Our canvas patch centres the crop in the core's canvas
on both axes, which for SNES (256x224 in a 360x240 canvas) drops the 8 black rows above and below.

## Decision

`source_rect` keeps upstream's widen-only rect for GBA, GB and GBC and crops both axes for NES and
SNES, chosen by `Platform::stretch_crops_height` in `platform_policy.rs`.

## Consequences

- GB and GBC stretch matches upstream byte for byte; NES (256x240) is the same either way; SNES
  stretch looks as it did on ns.0.
