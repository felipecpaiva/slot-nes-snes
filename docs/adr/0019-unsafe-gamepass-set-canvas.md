# 0019. Allow unsafe for the GL texture re-allocation in GamePass::set_canvas

- Status: Accepted, amended by [0028](0028-retro-shaders-own-gl-program.md)
- Date: 2026-10-12
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 09](../../.github/issues/09-canvas.md), [patch 0004](../../patches/0004-canvas.patch), CONTRIBUTING.md section 4

## Context

CONTRIBUTING.md allows `unsafe` only in `slot-retro`, where the libretro FFI lives. Re-allocating
the game texture needs GL calls (`DeleteTextures`, `UseProgram`, `Uniform2f`) in `slot-gfx`.

## Decision

A named exception: the GL calls in `slot-gfx` `GamePass::set_canvas`.

## Consequences

- `GamePass` owns the texture and uniform locations, and its other GL calls are already unsafe
  blocks in the same file.
- Rejected: a safe wrapper, which would add a new GL helper to an upstream file.
- Each block carries a single-line `// SAFETY:` comment.
