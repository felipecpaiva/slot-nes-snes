---
title: "Build ProSystem from a pinned commit for host and device and record its licence"
phase: 14
area: cores
type: feature
size: S
depends_on: [123-atari-tracking]
---

## Why
Step 2. The 7800 core built the slot way (ADR 0002, ADR 0095) before any platform code.

## Scope
- [x] `cores/prosystem/build.sh` over `cores/lib.sh`: `core=prosystem repo=prosystem-libretro`, root `Makefile`, plain C (no C++ runtime).
- [x] `device_include=cores/prosystem/glibc-2.17.h`: CoreTone calls `pow`, which glibc 2.29 re-versioned; the header binds `pow@GLIBC_2.17`. The `device_include` hook in `cores/lib.sh` is the TurboGrafx-16 groundwork's hunk, byte for byte.
- [x] `SLOT_PIN`: `prosystem_commit=8a88014287c7a01cd568067e5a557d0a2b2a051f`, `prosystem_tarball_sha256=23401c8b104ef24db111bbc4b13e37f224ffe16febfb89c704c70cdb269603bc`.
- [x] Tasks `core:prosystem:src`, `core:prosystem:host`, `core:device:prosystem`; the core in `core:host`, `core:device`, `task check` and `SLOT_REQUIRE_CORES`.
- [x] Licence: `License.txt` verbatim as `cores/prosystem/prosystem-GPL-2.0.txt`, CoreTone's `bupboop/License.txt` (zlib) as `prosystem-CoreTone-zlib.txt`, `prosystem-headerless-files.txt`; LICENSING.md section; SUPPLY-CHAIN.md row.
- [ ] The licence files move to `licenses/` and the core joins `dist:device` and `zip-check.sh` with issue 133.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | build check | `.meta` stamp matches the pin; device `.so` aarch64, NEEDED libc and libm at GLIBC_2.17 |
| (new) | `atari_core.rs` (issue 141) | the host dylib boots a generated cart |

## Edge cases
| Case | Expected handling |
|---|---|
| Archive hash changes | Build fails closed |
| The `.symver` stops matching (a newer pin adds another re-versioned libm call) | `core:device:prosystem` fails on the glibc gate; extend the header |

## Acceptance
- [x] Host dylib and device `.so` build from a clean tree. Device `.so` sha256 `489a6f71ff9e77d76e4105c9a19c18fe1ca9b59b2abd3b7fdf7055c507b08798` (rust:1-bullseye `sha256:4730e387...`, X1C, 2026-10-19), 32 compile lines all with `-mcpu=cortex-a53`. The first build needed `pow@GLIBC_2.29`; with the header it needs GLIBC_2.17 only.

## Device check (RG34XXSP)
None until the platform exists (issue 140).

## References
- ADR 0002, 0095; TurboGrafx-16 groundwork (`device_include`)
