# 0015. Start HostExtra with only the canvas field

- Status: Accepted
- Date: 2026-10-12
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 09](../../.github/issues/09-canvas.md), [issue 14](../../.github/issues/14-libretro-env-and-hires.md), [patch 0004](../../patches/0004-canvas.patch), [patch 0006](../../patches/0006-libretro-env.patch)

## Context

The plan described `HostExtra { canvas, av_change, av_enable }` in patch 0004. Nothing in 0004
reads `av_change` or `av_enable`, and an unread field is dead code.

## Decision

`HostExtra` holds only `canvas` in patch 0004. Issue 14 adds `av_change` and `av_enable`
(PLAN.md and issue 14 Scope say so).

## Consequences

- No dead fields in any single patch.
- The struct is append-only and `Host` is still untouched ([0009](0009-host-struct-untouched.md)).
