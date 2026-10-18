---
title: "Build Beetle NeoPop from a pinned commit for host and device and record its licence"
phase: 9
area: cores
type: feature
size: S
depends_on: [70-ngp-tracking]
---

## Why
Step 2. NGP needs its core built the slot way (ADR 0002, ADR 0090) before any platform code. Nothing here depends on the upstream version, so it lands on the v1.7.0 base.

## Scope
- [x] `cores/mednafen_ngp/build.sh` as a wrapper over `cores/lib.sh`: `core=mednafen_ngp repo=beetle-ngp-libretro`, root `Makefile`, `device_ldflags="-static-libstdc++ -static-libgcc"` (five C++ files).
- [x] `SLOT_PIN`: `mednafen_ngp_commit=a50d5ac288a81f2104ddf43195a4efdd15c72227`, `mednafen_ngp_tarball_sha256=ffeabf2a357548f3a55423d542c31bb1e08571d81d7104f8213df3bfa2eb9c9f` (checked by `build.sh fetch` against GitHub, and equal to the review's download).
- [x] Tasks `core:mednafen_ngp:src`, `core:mednafen_ngp:host`, `core:device:mednafen_ngp`; the core in `core:host`, `core:device`, `task check` and the `SLOT_REQUIRE_CORES` list in `scripts/run-tests.sh`. CI's `task core:host` picks it up.
- [x] Device gate: `is_aarch64` and `needs_old_glibc_only` (NEEDED is libc.so.6 only, GLIBC_2.17).
- [x] Licence: `COPYING` verbatim as `cores/mednafen_ngp/mednafen_ngp-GPL-2.0.txt`, `cores/mednafen_ngp/mednafen_ngp-headerless-files.txt` with its command, a LICENSING.md section, a SUPPLY-CHAIN.md row. Credit nelynes/slotPlus a8eae4c for the recipe.
- [x] The licence files move to `licenses/` and the core joins `dist:device` and `zip-check.sh` only with the platform patch (issue 72), so no release ships an unused core (the issue 57 rule; `dist-device.sh` copies all of `licenses/`).

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | build check | `.meta` stamp matches the pin; device `.so` is aarch64 with NEEDED limited to libc, libm, libdl, libpthread at GLIBC_2.17 or older |
| (new) | `ngp_core.rs` (issue 77) | the host dylib boots a generated cart |

## Edge cases
| Case | Expected handling |
|---|---|
| Archive hash changes | Build fails closed |
| A future pin pulls in `libstdc++.so.6` | `core:device:mednafen_ngp` fails on NEEDED |

## Acceptance
- [x] Host dylib and device `.so` build from a clean tree. Device `.so` sha256 `55c5fa86044e5bffd0c97bbfeff6a4731c722ec84ed08e6c54fffe65a033edb9` (rust:1-bullseye `sha256:4730e387...`, 2026-10-18), all 37 compile lines with `-mcpu=cortex-a53`.

## Device check (RG34XXSP)
None until the platform exists (issue 79 measures ms a frame).

## References
- ADR 0002, 0053, 0090; nelynes/slotPlus a8eae4c
