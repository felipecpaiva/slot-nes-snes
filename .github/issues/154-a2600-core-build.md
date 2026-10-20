---
title: "Build Stella 2014 from a pinned commit for host and device and record its licence"
phase: 14
area: cores
type: feature
size: S
depends_on: [153-atari-tracking]
---

## Why
Step 2. The 2600 core built the slot way (ADR 0002, ADR 0095) before any platform code. Nothing here depends on the platform.

## Scope
- [x] `cores/stella2014/build.sh` over `cores/lib.sh`: `core=stella2014 repo=stella2014-libretro`, root `Makefile`, `device_ldflags="-static-libstdc++ -static-libgcc"` (C++).
- [x] `SLOT_PIN`: `stella2014_commit=7d1361e407e63f29e52892655069e5fb4096e691`, `stella2014_tarball_sha256=c0f5e53f3c21e7760e434784634d44a02e57a30917da5279cfd3add4736afd82` (checked by `build.sh fetch` against GitHub).
- [x] Tasks `core:stella2014:src`, `core:stella2014:host`, `core:device:stella2014`; the core in `core:host`, `core:device`, `task check` and `SLOT_REQUIRE_CORES` in `scripts/run-tests.sh`.
- [x] Licence: `stella/license.txt` verbatim as `cores/stella2014/stella2014-GPL-2.0.txt`; Stella's own `Copyright.txt` at tag `release-3.9.3` (the or-later grant, not in the tarball) as `stella2014-Copyright-3.9.3.txt`; `stella2014-headerless-files.txt` with its command; LICENSING.md section; SUPPLY-CHAIN.md row.
- [ ] The licence files move to `licenses/` and the core joins `dist:device` and `zip-check.sh` with issue 156.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | build check | `.meta` stamp matches the pin; device `.so` is aarch64 with NEEDED limited to libc, libm, libdl, libpthread at GLIBC_2.17 or older |
| (new) | `atari_core.rs` (issue 171) | the host dylib boots a generated cart |

## Edge cases
| Case | Expected handling |
|---|---|
| Archive hash changes | Build fails closed |
| A future pin pulls in `libstdc++.so.6` | `core:device:stella2014` fails on NEEDED |

## Acceptance
- [x] Host dylib and device `.so` build from a clean tree. Device `.so` sha256 `aff1feb9e5398d7924b31ead921cca17a72efcff145c0c3dfca9d4b862a76a87` (rust:1-bullseye `sha256:4730e387...`, X1C, 2026-10-19), 98 compile lines all with `-mcpu=cortex-a53`, NEEDED libc.so.6 only.

## Device check (RG34XXSP)
None until the platform exists (issue 162 measures ms a frame).

## References
- ADR 0002, 0095; stella-emu/stella `release-3.9.3` Copyright.txt
