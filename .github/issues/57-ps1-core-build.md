---
title: "Build pcsx_rearmed from a pinned commit for host and device and record its licence"
phase: 8
area: cores
type: feature
size: M
depends_on: [56-ps1-tracking]
---

## Why
Step 4. PS1 needs its core built the slot way (ADR 0002, ADR 0063), before any platform code.

## Scope
- [ ] `cores/pcsx_rearmed/build.sh` as a wrapper over `cores/lib.sh`, `makefile=Makefile.libretro`.
- [ ] `SLOT_PIN`: `pcsx_rearmed_commit=c8816799b50388e61cfe237fe2cdbb7d8175f20a`, `pcsx_rearmed_tarball_sha256=edeb21fdeef8815521cb9d4488d2cd35746607c968ca9b26cce4e42c09f2dc99`.
- [ ] Device: `platform=unix HAVE_PHYSICAL_CDROM=0 BUILTIN_GPU=neon`, `-mcpu=cortex-a53`, CHD on (the default). ari64 is the aarch64 default. Do not put `DYNAREC` in shared `make_args`, because it would override osx's `DYNAREC := 0`.
- [ ] Host: `platform=osx`, interpreter.
- [ ] Tasks `core:pcsx_rearmed:host` and `core:device:pcsx_rearmed`. Assert ari64 from the build log or a symbol check.
- [ ] `licenses/pcsx_rearmed.txt` (GPL-2.0-or-later), a LICENSING.md section listing the bundled deps (lightrec, lightning, libchdr and its lzma, zstd and miniz), SUPPLY-CHAIN.md row. Credit bently0602 and oauramos for the recipe facts.
- [ ] The core joins `dist:device` and `zip-check.sh` only with the platform patch (issue 58), so no release ships an unused core.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | build check | `.meta` stamp matches the pin; device `.so` is aarch64 with NEEDED limited to libc, libm, libdl, libpthread at GLIBC_2.17 or older |

## Edge cases
| Case | Expected handling |
|---|---|
| Archive hash changes | Build fails closed |

## Acceptance
- [ ] Host dylib and device `.so` build from a clean tree; the device `.so` sha256 is recorded.

## Device check (RG34XXSP)
None beyond the spike's build, which used the same flags.

## References
- ADR 0002, 0063; docs/research/ps1-spike.md "What was built"
