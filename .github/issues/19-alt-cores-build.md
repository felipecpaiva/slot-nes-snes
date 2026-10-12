---
title: "Build nestopia and snes9x2005_plus for host and device and record their licences"
phase: 3
area: cores
type: feature
size: M
depends_on: [04-fceumm-core-build]
---

## Why
The core picker offers a second core per platform: nestopia for NES and snes9x2005_plus for SNES (docs/DECISIONS.md, docs/PLAN.md Phase 3 deliverables, Build steps 8, 9).

## Scope
- [x] `cores/nestopia/build.sh`: build in `libretro/`; device `platform=unix` with `-mcpu=cortex-a53`; host `platform=osx`; binary-type assertion; `.meta`; source tarball.
- [x] `cores/snes9x2005_plus/build.sh`: same, with `USE_BLARGG_APU=1`; copy the produced file to the `snes9x2005_plus_libretro.*` name.
- [x] `task core:host`, `task core:device` and `task dist:device` cover all 6 cores.
- [x] `licenses/nestopia-GPL-2.0.txt` and `licenses/snes9x2005-LICENSE.txt` verbatim from the pinned sources.
- [x] **Licence gate:** nestopia GPL-2.0-or-later verified at the pinned commit; snes9x2005 licence recorded in `LICENSING.md`.

## Tests
| ID | File | Asserts |
|---|---|---|
| (none) | | No T-id. Both cores are booted by T31 in 20-core-picker-pairs |

No upstream test file is touched.

## Edge cases
| Case | Expected handling |
|---|---|
| snes9x2005_plus output name is not `snes9x2005_plus_libretro.*` | build.sh copies the produced file to the `dylib_name` form; T31 opens it via `Core::Snes9x2005Plus` |

## Acceptance
- [x] Both dylibs (Mach-O) and both `.so` (aarch64 ELF) exist with `.meta`.
- [x] `LICENSING.md` nestopia and snes9x2005 sections filled.
- [x] `task check` builds all 6 host cores before testing.

## Device check (RG34XXSP)
None on its own. Opening all 6 cores is in the phase device check in 18-phase-3-parity.

## Review notes
- snes9x2005 carries the same non-commercial terms as snes9x; the README notice from 13-snes9x-core-build covers both.
- Never `platform=arm64`.

## References
- docs/PLAN.md: Phase 3 deliverables (core builds), Build steps 8, 9, Edge cases by layer (Core build), Critical files

## Acceptance notes
- 2026-10-13: `task core:host` built `nestopia_libretro.dylib` and `snes9x2005_plus_libretro.dylib` (arm64 Mach-O) with `.meta` and source tarballs. `task core:device` built both aarch64 `.so`; nestopia needs only libm and libc (static libstdc++ and libgcc), snes9x2005_plus only libc. The upstream Makefile already names the output `snes9x2005_plus_libretro.*` when `USE_BLARGG_APU=1`, so no copy was needed.
- `task check` exit 0 (builds all 6 host cores first; harness 0 diffs). `task zip` plus `scripts/zip-check.sh` ok on `slot-nes-snes-v1.6.0-ns.0-h700.zip`.
- Pins: nestopia `135dfa6dfda5e7603d61e751b9ddd0cc42546bc3`, snes9x2005 `a79dfe9047e7fec58808aefe48ad2bf499c7af11` (tarball sha256 in `SLOT_PIN`).
- `task bench:device` accepts `CORE=nestopia` and `CORE=snes9x2005_plus`.
