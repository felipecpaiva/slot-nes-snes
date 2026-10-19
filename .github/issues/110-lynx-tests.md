---
title: "Test Lynx with a homebrew image, synthetic carts and the real BIOS when present"
phase: 12
area: tests
type: test
size: S
depends_on: [102-lynx-core-build]
---

## Why
No BIOS can be committed, so CI cannot boot a Lynx cart. The core tests split into those that need no BIOS and those that read the maintainer's own boot ROM (ADR 0093).

## Scope
- [x] Patch 0070 `crates/slot/tests/lynx_core.rs`, needing no BIOS (always run, CI included):
  - a BS93 homebrew image (copied to RAM, boot ROM skipped) paints 160x102 red in the middle of 240x160; reports 75 fps while running 59.9 Hz frames;
  - `lynx_force_60hz` changes only the reported fps;
  - a game that sets 75 Hz gets 75 Hz frames;
  - state round-trip; no save RAM;
  - the missing-BIOS signature (loads, never draws, frames run to the cycle cap) and the short-BIOS case.
- [x] BIOS-gated (`SLOT_LYNX_BIOS` = path to `lynxboot.img`, 512 bytes, crc32 `0d973c9d`): a synthetic `.lnx` boots through the cc65 encrypted loader, draws, runs at the boot ROM's 59.9 Hz, round-trips its state; the pad rotation contract.
- [x] Without the variable, or with a file that is not the known dump, those tests print `skipping: no Lynx BIOS, ...`. `run-tests.sh` lists a skip naming a BIOS as a ROM skip, never CORE MISSING, so `SLOT_REQUIRE_CORES=1` (and CI) stays green; the core itself is still required first.
- [x] Platform half, one per step: `lynx_platform.rs`, `lynx_bios.rs`, `lynx_seat.rs` (BIOS-gated), `lynx_pacing.rs` (MockCore), `lynx_rotation.rs`, `lynx_then_gba.rs`.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `lynx_core.rs` | 10 tests, 7 without a BIOS, 3 BIOS-gated; all pass locally with `SLOT_LYNX_BIOS` set (2026-10-18) |

## Edge cases
| Case | Expected handling |
|---|---|
| `SLOT_LYNX_BIOS` points at a 0-byte placeholder | Skip naming the file, size and crc |

## Acceptance
- [x] Core half green with and without `SLOT_LYNX_BIOS`.

## Status
Platform half landed with each patch: `lynx_platform.rs` (0071), `lynx_bios.rs` (0072), `lynx_options.rs` (0073), `lynx_screen.rs` (0074 to 0077), `lynx_pacing.rs` (0075), `lynx_seat.rs` (0071, 0076), `lynx_rotation.rs` (0077), `lynx_then_gba.rs` (0079).

## Device check (RG34XXSP)
None (host only).

## References
- ADR 0093; cc65 libsrc/lynx/bootldr.s (Karri Kaksonen, zlib)
