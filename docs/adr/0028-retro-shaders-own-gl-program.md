# 0028. Run the retro shaders in their own GL program

- Status: Accepted. Amends [0019](0019-unsafe-gamepass-set-canvas.md)
- Date: 2026-10-13
- Deciders: maintainer (Felipe Paiva)
- Related: [patch 0020](../../patches/0020-retro-shaders.patch), [retro-shaders.md](../research/retro-shaders.md)

## Context

Upstream draws every game effect with one fragment shader, `GAME_FRAG`, branching on `u_mode`.
New branches there would be carried by GBA, GB and GBC too.

## Decision

The retro shaders run in their own GL program (`pipeline/retro.rs`, a child module of
`pipeline.rs`). `GamePass::draw_source` hands a `Retro` effect to it; if it fails to build it logs
and NES and SNES draw plain. New named `unsafe` exception: the GL calls of that program, next to
`GamePass::set_canvas`.

## Consequences

- Upstream's game program text stays byte-identical, so GBA, GB and GBC carry no extra GLSL or
  register cost on the Mali-G31.
- A retro shader that fails to compile on a device cannot break GBA.
- Building the extra program costs boot time ([0031](0031-warm-retro-shaders-at-boot.md)).
