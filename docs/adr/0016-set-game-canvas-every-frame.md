# 0016. Call set_game_canvas every frame and return early when unchanged

- Status: Accepted
- Date: 2026-10-12
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 09](../../.github/issues/09-canvas.md), [patch 0004](../../patches/0004-canvas.patch)

## Context

The plan said to set the game canvas "on every core open". A core appears in several ways: open,
eject then insert, the core picker, and resume. Missing one leaves a stale texture.

## Decision

`Compositor::set_game_canvas` is called every frame from `Frontend::compose`.
`GamePass::set_canvas` returns at once when the size is unchanged.

## Consequences

- One call site covers every way a core appears. GBA always gets (240, 160).
- An unchanged frame costs one tuple compare.
- Harness leg H3 (NES, eject, GBA equals H1) proves no stale texture.
