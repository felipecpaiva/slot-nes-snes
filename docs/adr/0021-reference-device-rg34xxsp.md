# 0021. Use the Anbernic RG34XXSP as the reference and test device

- Status: Accepted. Supersedes [0003](0003-reference-device-rg35xxsp.md)
- Date: 2026-10-12
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 17](../../.github/issues/17-device-gate-log.md), [DEVICE-GATE.md](../DEVICE-GATE.md)

## Context

The maintainer's device is an RG34XXSP, not the RG35XXSP named in
[0003](0003-reference-device-rg35xxsp.md). Same H700 and stock OS.

## Decision

The reference and test device is the Anbernic RG34XXSP (720x480, 3:2).

## Consequences

- Same H700 and stock OS, so the same zip.
- The 720x480 panel is an exact 3x of GBA, so there is no bezel: GBA fills the screen and NES and
  SNES show at an integer 2x (512x480, 512x448), centred.
- The bezel decision ([0005](0005-gba-sp-bezel-on-rg35xxsp.md)) still holds for 4:3 devices and
  stays covered by harness leg B1 and `nes_window.rs`.
- The black bars at 2x led to [0022](0022-nes-snes-default-stretch.md).
