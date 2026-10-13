# 0009. Keep the Host struct unchanged and put new libretro state in a side struct

- Status: Accepted
- Date: 2026-10-11
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 09](../../.github/issues/09-canvas.md), [issue 14](../../.github/issues/14-libretro-env-and-hires.md), [patch 0004](../../patches/0004-canvas.patch), [patch 0006](../../patches/0006-libretro-env.patch)

## Context

The upstream in-source test helper `host_with()` (`libretro.rs:701-718`) builds `Host` with every
field listed. Any new field breaks an upstream test. NES and SNES need new libretro state (canvas,
av change, av enable).

## Decision

The `Host` field list and `Active::bind`'s signature stay unchanged. New state lives in
`HostExtra`, owned by `LibretroCore`, with its own thread-local pointer bound next to every
`Active::bind` call.

## Consequences

- Upstream tests compile unchanged. Failure injection proved it: adding a field to `Host` fails
  to compile in `host_with()`.
- When `HostExtra` is unbound (the in-source tests), `video_refresh` and `environment` must behave
  exactly like upstream. Review that branch line by line.
- On each rebase: check that `host_with()` and the `Active::bind` call sites did not move.
