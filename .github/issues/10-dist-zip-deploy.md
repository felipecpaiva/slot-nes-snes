---
title: "Package the h700 release zip, GPL source tarball and device deploy tasks"
phase: 1
area: release
type: feature
size: M
depends_on: [09-canvas, 04-fceumm-core-build]
---

## Why
Install and update must work exactly like slot: unzip, copy to the SD root, boot; an update replaces `System/` and keeps `Config/` (docs/PLAN.md Spec success 5, Build steps 27, 28). A GPL-3 corresponding-source tarball goes with every release.

## Scope
- [ ] `task dist:device`: run `task -d build/slot dist:device` (through `scripts/device-sh.sh`), then copy `fceumm_libretro.so`, its `.meta`, its source tarball and licence into `System/` and `System/licenses/`.
- [ ] `task src-tarball`: `slot-nes-snes-src-<tag>.tar.gz` (git archive of patched `build/slot` plus this repo), also copied into `System/licenses/`.
- [ ] `task zip`: `slot-nes-snes-v1.6.0-ns.N-h700.zip` with one top folder of the same name, laid out like slot's release zip (`System/`, `BIOS/`, `Config/`, `Games/{GBA,GB,GBC,NES}/`, `Labels/`, `Saves/`, `States/`, `Wallpapers/`).
- [ ] `scripts/zip-check.sh`: one top folder; `file | grep aarch64` for `slot` and every core present; licences, `.meta` and source tarballs present.
- [ ] `task deploy:device` (adb push of the extra cores, chmod, reboot) and `task log:device`.
- [ ] `LICENSING.md`: GPL-3 source offer pointing at the tarball.

## Tests
| ID | File | Asserts |
|---|---|---|
| T13 | `scripts/zip-check.sh` | Local zip: one top folder; aarch64 ELF for slot and cores; licences and source tarball present |

No upstream test file is touched.

## Edge cases
| Case | Expected handling |
|---|---|
| (none specific) | Missing snes9x licence or source tarball is a release ship check in 30-release-workflow |

## Acceptance
- [ ] `task dist:device && task zip && task src-tarball && sh scripts/zip-check.sh slot-nes-snes-v1.6.0-ns.0-h700.zip` passes.
- [ ] Zip tree matches docs/PLAN.md "Verification" step 4 (cores present so far).
- [ ] `task deploy:device` then `task log:device` shows `slot: core /mnt/sdcard/System/fceumm_libretro.so`.

## Device check (RG35XXSP)
None separate; the zip produced here is what the phase device check in 01-phase-1-nes-boots installs.

## Review notes
- Gotcha 16 (slot's `device:sh` is internal and `dist:device` copies only mgba/gpsp): `slot: taskfile.yml:278` is `internal: true` and `slot: taskfile.yml:285-319` copies only mgba/gpsp. This repo owns the docker wrapper and the post-copy of the extra cores, `.meta`, licences and sources. Later phases extend the copy list to all 6 cores.
- Licence obligation: the GPL-3 source tarball and every core's corresponding source must be in `System/licenses/`.

## References
- docs/PLAN.md: Phase 1 deliverables (dist), Build steps 27, 28, Verification steps 4 and 5, Critical files (`zip-check.sh`)
- `slot: taskfile.yml:278,285-319`
