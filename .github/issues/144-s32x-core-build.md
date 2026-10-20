---
title: "Build PicoDrive and its three submodules from pinned commits for host and device and record its licence"
phase: 15
area: cores
type: feature
size: M
depends_on: [143-s32x-tracking]
---

## Why
The GitHub archive of libretro/picodrive has no submodules, and the libretro build compiles emu2413 and dr_mp3 and includes libpicofe's plat.h. The licence is the MAME-style non-commercial one.

## Scope
- [x] `cores/picodrive/build.sh` with `modules` (new optional `cores/lib.sh` variable; the other cores' stamps unchanged).
- [x] `SLOT_PIN` keys for the core and each submodule, with archive sha256s.
- [x] `use_libchdr=0`, `PLATFORM_TREMOR=1`, `PLATFORM_ZLIB=1`, `GIT_REVISION`.
- [x] Device build: SH-2 dynarec on, `log` and `pow` bound to GLIBC_2.17 under `-flto-partition=one`.
- [x] LICENSING.md section, licence files, headerless list.

## Tests
| ID | File | Asserts |
|---|---|---|
| C1 | `task core:device:picodrive` | aarch64 ELF, NEEDED libc and libm only, GLIBC_2.17 or older |
| C2 | `s32x_core.rs` | the core loads and runs a generated 32X cart |

## Edge cases
| Case | Expected handling |
|---|---|
| A submodule archive changes on GitHub | the sha256 check fails the fetch; nothing is unpacked |
| A pin bump adds a re-versioned libm symbol | `needs_old_glibc_only` fails the device build |

## Acceptance
- [x] Host and device builds pass; the dist ships the core, four source tarballs and the licences.

## Device check (RG34XXSP)
Issue 152.

## References
- ADR 0096; docs/cart-art/S32X.md
