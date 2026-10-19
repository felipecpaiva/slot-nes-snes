---
title: "Build Beetle Cygne from a pinned commit for host and device and record its licence"
phase: 11
area: cores
type: feature
size: S
depends_on: [91-wswan-tracking]
---

## Why
Step 2. WonderSwan needs its core built the slot way (ADR 0002, ADR 0092) before any platform code. Nothing here depends on the upstream version, so it lands on the v1.7.0 base.

## Scope
- [x] `cores/mednafen_wswan/build.sh` as a wrapper over `cores/lib.sh`: `core=mednafen_wswan repo=beetle-wswan-libretro`, root `Makefile`, no `device_ldflags` (plain C, linked by `$(CC)`).
- [x] `SLOT_PIN`: `mednafen_wswan_commit=4b01295838ea89e3f1355bbe4cb5cf98aa6108cd` (HEAD on 2026-10-18 by `git ls-remote`), `mednafen_wswan_tarball_sha256=bce15c0e2505e15b7b55fa1d51b4a12219d07a67be62bbca5c26678d0d89c659` (checked by `build.sh fetch` against GitHub, and equal to the fork review's download).
- [x] Tasks `core:mednafen_wswan:src`, `core:mednafen_wswan:host`, `core:device:mednafen_wswan`; the core in `core:host`, `core:device`, `task check` and the `SLOT_REQUIRE_CORES` list in `scripts/run-tests.sh`. CI's `task core:host` picks it up.
- [x] Device gate: `is_aarch64` and `needs_old_glibc_only` (NEEDED is libc.so.6 only, GLIBC_2.17).
- [x] Licence: `COPYING` verbatim as `cores/mednafen_wswan/mednafen_wswan-GPL-2.0.txt`, `cores/mednafen_wswan/mednafen_wswan-headerless-files.txt` with its command, a LICENSING.md section (including Bryan McPhail's credit notice in `v30mz.c`), a SUPPLY-CHAIN.md row. Credit nelynes/slotPlus 273ded9 for the recipe.
- [x] The licence files move to `licenses/` and the core joins `dist:device` and `zip-check.sh` only with the platform patch (issue 93), so no release ships an unused core (the issue 57 rule; `dist-device.sh` copies all of `licenses/`).

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | build check | `.meta` stamp matches the pin; device `.so` is aarch64 with NEEDED limited to libc, libm, libdl, libpthread at GLIBC_2.17 or older |
| (new) | `wswan_core.rs` (issue 97) | the host dylib boots a generated cart |

## Edge cases
| Case | Expected handling |
|---|---|
| Archive hash changes | Build fails closed |
| A future pin adds C++ files and pulls in `libstdc++.so.6` | `core:device:mednafen_wswan` fails on NEEDED; add the static runtime flags then |

## Acceptance
- [x] Host dylib and device `.so` build from a clean tree. Device `.so` sha256 `c52d0c086cc5c17b3f2b84e741c9dbebeb84288ac6eec09dbef3ddea35b1d010` (rust:1-bullseye `sha256:4730e387...`, 2026-10-18), all 16 compile lines with `-mcpu=cortex-a53`.

## Device check (RG34XXSP)
None until the platform exists (issue 99 measures ms a frame).

## References
- ADR 0002, 0053, 0092; nelynes/slotPlus 273ded9
