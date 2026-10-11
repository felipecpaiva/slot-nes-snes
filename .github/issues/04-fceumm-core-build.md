---
title: "Build fceumm for host and device from a pinned commit and record its licence"
phase: 1
area: cores
type: feature
size: M
depends_on: [02-patch-pipeline]
---

## Why
fceumm is the NES default core (docs/DECISIONS.md). It must be built from a pinned commit the way slot builds gpSP, with GPL corresponding source shipped (docs/PLAN.md Phase 1 deliverables, Build steps 4, 9, 10).

## Scope
- [ ] `cores/fceumm/build.sh`, mirroring `slot: cores/gpsp/build.sh`: `stamp COMMIT` and `build COMMIT SRC_TGZ WORKDIR OUT`. Device: `make -f Makefile.libretro platform=unix` with `CFLAGS/CXXFLAGS=-mcpu=cortex-a53`. Host: `platform=osx`. Ships the source tarball as GPL-2 corresponding source.
- [ ] build.sh asserts `file $out | grep -q 'ELF 64-bit.*aarch64'` on device and `Mach-O` on host before writing `.meta`.
- [ ] `task core:host` extended with `cores/fceumm/build.sh build ... vendor/fceumm_libretro.dylib`.
- [ ] `task core:device` builds `fceumm_libretro.so`.
- [ ] `scripts/device-sh.sh`: docker `rust:1-bullseye` wrapper, a copy of slot's internal `device:sh` (`slot: taskfile.yml:278`, `internal: true`, not callable from outside); runs natively when already on Linux aarch64.
- [ ] `licenses/fceumm-GPL-2.0.txt` verbatim from the pinned source.
- [ ] **Licence gate:** fceumm GPL-2.0-or-later verified from `COPYING` and source headers at the pinned commit.
- [ ] `LICENSING.md`: slot GPL-3.0-or-later and this patch set, fceumm (verified), placeholder sections for snes9x and nestopia filled in later phases.

## Tests
| ID | File | Asserts |
|---|---|---|
| (none) | | No T-id. The core is exercised by later issues |

No upstream test file is touched.

## Edge cases
| Case | Expected handling |
|---|---|
| `platform=arm64` yields `.dll`, so no `.so` exists | Never use `platform=arm64`; build.sh asserts the binary type and fails before writing `.meta` |

## Acceptance
- [ ] `vendor/fceumm_libretro.dylib` is Mach-O arm64 and has a `.meta` with the pinned commit.
- [ ] `fceumm_libretro.so` built through `device-sh.sh` is `ELF 64-bit ... aarch64`.
- [ ] `LICENSING.md` records the verified fceumm licence and which files were checked.

## Device check (RG35XXSP)
None, the core is loaded on device by the phase check in 01-phase-1-nes-boots.

## Review notes
- Gotcha 2 (the `platform=arm64` `.dll` trap): check the make line and the `file` assertion.
- Licence obligation: the GPL-2 source tarball is produced by the build, not fetched later.
- If the pinned commit will not build on macOS, the plan allows a buildbot fallback for host only, with date and sha256 recorded in `.meta`.

## References
- docs/PLAN.md: Build steps 4, 9, 10; Phase 1 deliverables; Critical files (New files)
- `slot: cores/gpsp/build.sh`; `slot: taskfile.yml:278`
