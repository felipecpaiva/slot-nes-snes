# 0005. Keep the GBA SP bezel for NES and SNES on the RG35XXSP

- Status: Accepted (still holds for 4:3 devices, see [0021](0021-reference-device-rg34xxsp.md))
- Date: 2026-10-11
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 09](../../.github/issues/09-canvas.md), [patch 0004](../../patches/0004-canvas.patch), [PLAN.md](../PLAN.md) Context and Gotcha 6

## Context

On the RG35XXSP slot shows GBA in a 640x427 window with the GBA SP bezel below it (rows 427 to 479).
NES and SNES needed a place on that screen. Decided by the user during planning.

## Decision

NES and SNES keep the GBA SP bezel on the RG35XXSP, in the same 640x427 window as GBA.

## Consequences

- Same nostalgia look as GBA.
- NES shows about 455x427 and SNES about 455x398, non-integer, the same treatment GBA gets. Do not
  "fix" this to 512x480.
- Covered by harness leg B1 and `nes_window.rs`.
- Since [0021](0021-reference-device-rg34xxsp.md) the reference device has no bezel. This decision
  still holds for 4:3 devices.
