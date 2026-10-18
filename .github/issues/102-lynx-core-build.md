---
title: "Build Beetle Lynx from a pinned commit for host and device and record its licence"
phase: 12
area: cores
type: feature
size: S
depends_on: [101-lynx-tracking]
---

## Why
Step 2. Lynx needs its core built the slot way (ADR 0002, ADR 0093) before any platform code. Nothing here depends on the upstream version, so it lands on the v1.7.0 base.

## Scope
- [x] `cores/mednafen_lynx/build.sh` over `cores/lib.sh`: `core=mednafen_lynx repo=beetle-lynx-libretro`, root `Makefile`, `device_ldflags="-static-libstdc++ -static-libgcc"` (the emulator is C++).
- [x] `SLOT_PIN`: `mednafen_lynx_commit=fcdefcfb3c11d6d2e71be076a5d3df2e88ab73ed`, `mednafen_lynx_tarball_sha256=3dd45a6f6585c444a415cb097996c572467754748e7163eca466d89b31bd8b37` (checked by `build.sh fetch` against GitHub; equal to the fork review's download).
- [x] Tasks `core:mednafen_lynx:src`, `core:mednafen_lynx:host`, `core:device:mednafen_lynx`; the core in `core:host`, `core:device`, `task check` and the `SLOT_REQUIRE_CORES` list in `scripts/run-tests.sh`.
- [x] Device gate: `is_aarch64` and `needs_old_glibc_only`.
- [x] Licence: `COPYING` verbatim as `cores/mednafen_lynx/mednafen_lynx-GPL-2.0.txt`, the Handy zlib text (`mednafen/lynx/license.txt`) as `cores/mednafen_lynx/mednafen_lynx-Handy-zlib.txt`, `cores/mednafen_lynx/mednafen_lynx-headerless-files.txt` with its command, a LICENSING.md section, a SUPPLY-CHAIN.md row. Credit nelynes/slotPlus 749523c.
- [x] The licence files move to `licenses/` and the core joins `dist:device` and `zip-check.sh` only with the platform patch (issue 103), the issue 57 rule.
- If the maintainer picks Handy (ADR 0093): the same steps for `libretro/libretro-handy` (`core=handy`), plus a written answer for the unlicensed `lynx/lynxdec.cpp` before it can ship.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | build check | `.meta` stamp matches the pin; device `.so` is aarch64 with NEEDED limited to libc, libm, libdl, libpthread at GLIBC_2.17 or older |
| (new) | `lynx_core.rs` (issue 110) | the host dylib runs a homebrew image and pins the missing-BIOS signature |

## Edge cases
| Case | Expected handling |
|---|---|
| Archive hash changes | Build fails closed |
| A future pin pulls in `libstdc++.so.6` | `core:device:mednafen_lynx` fails on NEEDED |

## Acceptance
- [x] Host dylib and device `.so` build from a clean tree. Device `.so` sha256 `8c81d44977e563029522e49528f6f1d613fbfcb38ed40a42cdd304a9be71da32` (rust:1-bullseye `sha256:4730e387...`, 2026-10-18), all 29 compile lines with `-mcpu=cortex-a53`.

## Device check (RG34XXSP)
None until the platform exists (issue 112 measures ms a frame).

## References
- ADR 0002, 0083, 0093; nelynes/slotPlus 749523c
