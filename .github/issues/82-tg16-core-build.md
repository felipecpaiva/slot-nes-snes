---
title: "Build Beetle PCE Fast from a pinned commit for host and device and record its licence"
phase: 10
area: cores
type: feature
size: S
depends_on: [81-tg16-tracking]
---

## Why
Step 2. TG16 needs its core built the slot way (ADR 0002, ADR 0091) before any platform code. Nothing here depends on the upstream version, so it lands on the v1.7.0 base.

## Scope
- [x] `cores/mednafen_pce_fast/build.sh` as a wrapper over `cores/lib.sh`: `core=mednafen_pce_fast repo=beetle-pce-fast-libretro`, root `Makefile`, `make_args="HAVE_CDROM=0 HAVE_CHD=0"`, `device_ldflags="-static-libstdc++ -static-libgcc -Wl,--as-needed"` (all C, but linked with `$(CXX)` and `-lrt`).
- [x] `powf` pinned to `GLIBC_2.17` by `cores/mednafen_pce_fast/glibc-2.17.h`, force-included through the new optional `device_include` in `cores/lib.sh` (in the device stamp; other cores' stamps unchanged).
- [x] `SLOT_PIN`: `mednafen_pce_fast_commit=3f946f277aef3aa99a95551618bbcd1dd2bda0d9`, `mednafen_pce_fast_tarball_sha256=1bc1d96f2a0957e97d50c009d25ae5725d60e80eada679dafbb214afa84cda29` (checked by `build.sh fetch` against GitHub, and equal to the review's download).
- [x] Tasks `core:mednafen_pce_fast:src`, `core:mednafen_pce_fast:host`, `core:device:mednafen_pce_fast`; the core in `core:host`, `core:device`, `task check` and the `SLOT_REQUIRE_CORES` list in `scripts/run-tests.sh`. CI's `task core:host` picks it up.
- [x] Device gate: `is_aarch64` and `needs_old_glibc_only` (NEEDED is libc.so.6 and libm.so.6, GLIBC_2.17).
- [x] Licence: `COPYING` verbatim as `cores/mednafen_pce_fast/mednafen_pce_fast-GPL-2.0.txt`, Tremor's Xiph BSD `COPYING` as `mednafen_pce_fast-tremor-BSD.txt` (Tremor is linked in), `mednafen_pce_fast-headerless-files.txt` with its command, a LICENSING.md section, a SUPPLY-CHAIN.md row. Credit nelynes/slotPlus 92b7022 for the recipe.
- [x] The licence files move to `licenses/` and the core joins `dist:device` and `zip-check.sh` only with the platform patch (issue 83), so no release ships an unused core (the issue 57 rule; `dist-device.sh` copies all of `licenses/`).

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | build check | `.meta` stamp matches the pin; device `.so` is aarch64 with NEEDED limited to libc, libm, libdl, libpthread at GLIBC_2.17 or older |
| (new) | `tg16_core.rs` (issue 88) | the host dylib boots a generated HuCard |

## Edge cases
| Case | Expected handling |
|---|---|
| Archive hash changes | Build fails closed |
| A future pin calls another re-versioned libm function (`expf`, `logf`, `pow`, ...) | `core:device:mednafen_pce_fast` fails on the GLIBC version; extend the header |
| A future pin pulls in `libstdc++.so.6` or `librt.so.1` | `core:device:mednafen_pce_fast` fails on NEEDED |

## Acceptance
- [x] Host dylib and device `.so` build from a clean tree. Device `.so` sha256 `30a4f72253f1b70102f9542303a41a69f83240b9afb608917335f95ba949b69c` (rust:1-bullseye `sha256:4730e387...`, 2026-10-18), all 60 compile lines with `-mcpu=cortex-a53`.

## Device check (RG34XXSP)
None until the platform exists (issue 90 measures ms a frame).

## References
- ADR 0002, 0053, 0091; nelynes/slotPlus 92b7022
