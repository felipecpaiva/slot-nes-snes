---
title: "Build snes9x from a pinned commit and record its non-commercial licence stance"
phase: 2
area: cores
type: feature
size: M
depends_on: [04-fceumm-core-build]
---

## Why
snes9x is the SNES default core (docs/DECISIONS.md). It is licensed for non-commercial use only and is not GPL-compatible, so the licence stance must be written down and shipped (docs/PLAN.md Phase 2 deliverables, Spec "Who it's NOT for", docs/RESEARCH.md "Licence").

## Scope
- [ ] `cores/snes9x/build.sh` (same shape as `cores/fceumm/build.sh`): build in `libretro/`; device `platform=unix` with `-mcpu=cortex-a53`; host `platform=osx`; binary-type assertion; `.meta` stamp; source tarball.
- [ ] `task core:host` and `task core:device` extended with snes9x; `task dist:device` copies `snes9x_libretro.so`, `.meta`, source and licence.
- [ ] `licenses/snes9x-LICENSE.txt` verbatim from the pinned source.
- [ ] `LICENSING.md`: the libretro plugin-boundary stance (a separately loaded `.so` across the libretro C ABI, as shipped by RetroArch, ROCKNIX and Knulli) and the non-commercial terms.
- [ ] README and release notes carry the non-commercial notice.

## Tests
| ID | File | Asserts |
|---|---|---|
| (none) | | No T-id. snes9x is exercised by 14-libretro-env-and-hires |

No upstream test file is touched.

## Edge cases
| Case | Expected handling |
|---|---|
| (none specific) | The binary-type assertion from 04-fceumm-core-build applies unchanged |

## Acceptance
- [ ] `vendor/snes9x_libretro.dylib` is Mach-O; `snes9x_libretro.so` is aarch64 ELF; both have `.meta`.
- [ ] `LICENSING.md` snes9x section filled; README notice present.
- [ ] `zip-check.sh` sees the snes9x licence in `System/licenses/`.

## Device check (RG35XXSP)
None on its own. The phase device check is in 11-phase-2-snes.

## Review notes
- Licence obligation: snes9x is non-commercial. The README and release notes must say so; commercial redistribution is explicitly unsupported.
- Do not paraphrase the licence file; it must be verbatim from the pinned commit.

## References
- docs/PLAN.md: Phase 2 deliverables (snes9x build and licence), Spec, Critical files
- docs/RESEARCH.md: Cores, Licence
