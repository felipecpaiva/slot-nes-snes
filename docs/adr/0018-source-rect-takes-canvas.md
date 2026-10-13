# 0018. Pass the canvas to video_mode::source_rect

- Status: Accepted
- Date: 2026-10-12
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 09](../../.github/issues/09-canvas.md), [patch 0004](../../patches/0004-canvas.patch)

## Context

`video_mode::source_rect` derived its centring offsets from the fixed `SRC_W`/`SRC_H`, which is
wrong for a 360x240 canvas.

## Decision

`source_rect` takes the canvas as a second parameter: `source_rect(platform, canvas, mode)`.
`Core::canvas_f32` (new, in `core_policy.rs`) keeps the `app.rs` `picture_rect` hunk to one line.

## Consequences

- Its only caller is `App::source_rect`, and no upstream test calls it.
- On each rebase: if upstream adds a caller or a test of `source_rect`, it will not compile.
