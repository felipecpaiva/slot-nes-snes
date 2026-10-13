# 0031. Build and warm the retro shader program at start-up

- Status: Accepted
- Date: 2026-10-13
- Deciders: maintainer (Felipe Paiva)
- Related: [patch 0020](../../patches/0020-retro-shaders.patch), [DEVICE-GATE.md](../DEVICE-GATE.md) (2026-10-13)

## Context

In the 2026-10-13 shader run each new mode showed one long present (31 to 67 ms) in its first
window, most likely the driver finishing the retro program on its first draw. The program could be
built at boot or at the first NES/SNES insert.

## Decision

The retro shader program is built and warmed (one off-screen draw per mode) at start-up, for every
user. Maintainer's choice: a slower boot is preferred to a pause in the insert animation.

## Consequences

- First-window longest present: Sharp on Super Mario RPG 33.95 to 19.45 ms, crt-pi on Battletoads
  66.66 to 23.59 ms. crt-pi on Super Mario RPG went 30.97 to 29.90 ms (one run), so that spike is
  not shown to be the shader.
- Cost: `boot: compositor` went from 172 ms to about 306 ms, plus about 15 to 25 ms for the warm-up,
  for every user, GBA-only users included.
