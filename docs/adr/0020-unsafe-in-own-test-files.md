# 0020. Allow unsafe in our own test files that read GL output or core symbols

- Status: Accepted
- Date: 2026-10-12
- Deciders: maintainer (Felipe Paiva)
- Related: [patch 0003](../../patches/0003-core-fceumm.patch), [patch 0004](../../patches/0004-canvas.patch), CONTRIBUTING.md section 4

## Context

Proving the NES window size and that fceumm consumed the overscan options needs the window pixels
and `retro_get_system_av_info`. slot has no safe API for either.

## Decision

`unsafe` is allowed in our own new test files that must read GL output or a core symbol slot does
not expose (`nes_window.rs`, `nes_fceumm.rs`).

## Consequences

- The window size and core options are proved, not assumed.
- Tests never ship to the device.
