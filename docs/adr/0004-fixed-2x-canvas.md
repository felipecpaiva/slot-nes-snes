# 0004. Give NES and SNES cores a fixed 360x240 canvas at 2x

- Status: Accepted
- Date: 2026-10-11
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 09](../../.github/issues/09-canvas.md), [issue 14](../../.github/issues/14-libretro-env-and-hires.md), [issue 36](../../.github/issues/36-deferred-option-b-video.md), [patch 0004](../../patches/0004-canvas.patch), [patch 0006](../../patches/0006-libretro-env.patch)

## Context

Upstream crops every frame to 240x160 (`libretro.rs:321-330`) and the pipeline is fixed at
`SRC_W`/`SRC_H`. Option A was a fixed canvas per core. Option B was variable frames up to 512x480,
a much bigger patch.

## Decision

Option A. Mgba and Gpsp keep 240x160 at SCALE 3. Fceumm, Nestopia, Snes9x and Snes9x2005Plus use a
360x240 canvas, 2x into the same 720x480 logical space. Canvas truth is `Core::canvas()`. SNES
hi-res frames are blended 2:1 (horizontally when wider than 360, vertically when taller than 240).

## Consequences

- Smallest patch, GBA untouched. NES 256x240 is an exact 2x.
- Thumbnails keep the full 360x240 canvas, the same 3:2 as GBA, so the polaroid layout is unchanged.
- Harness leg H3 (NES, eject, GBA) must equal the GBA-only run.
- Cost: true SNES hi-res detail is lost on the rare titles that use it. Option B is deferred
  (issue 36).
