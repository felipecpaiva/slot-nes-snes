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
- [ ] `cores/nestopia/build.sh`: build in `libretro/`; device `platform=unix` with `-mcpu=cortex-a53`; host `platform=osx`; binary-type assertion; `.meta`; source tarball.
- [ ] `cores/snes9x2005_plus/build.sh`: same, with `USE_BLARGG_APU=1`; copy the produced file to the `snes9x2005_plus_libretro.*` name.
- [ ] `task core:host`, `task core:device` and `task dist:device` cover all 6 cores.
- [ ] `licenses/nestopia-GPL-2.0.txt` and `licenses/snes9x2005-LICENSE.txt` verbatim from the pinned sources.
- [ ] **Licence gate:** nestopia GPL-2.0-or-later verified at the pinned commit; snes9x2005 licence recorded in `LICENSING.md`.

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
- [ ] Both dylibs (Mach-O) and both `.so` (aarch64 ELF) exist with `.meta`.
- [ ] `LICENSING.md` nestopia and snes9x2005 sections filled.
- [ ] `task check` builds all 6 host cores before testing.

## Device check (RG34XXSP)
None on its own. Opening all 6 cores is in the phase device check in 18-phase-3-parity.

## Review notes
- snes9x2005 carries the same non-commercial terms as snes9x; the README notice from 13-snes9x-core-build covers both.
- Never `platform=arm64`.

## References
- docs/PLAN.md: Phase 3 deliverables (core builds), Build steps 8, 9, Edge cases by layer (Core build), Critical files
