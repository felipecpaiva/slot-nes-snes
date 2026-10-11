---
title: "Phase 1: NES boots on the RG35XXSP from a release-shaped zip"
phase: 1
area: device
type: tracking
size: L
depends_on: []
---

## Why
Smallest end-to-end slice: patch infra, `Platform::Nes`, fceumm, the 2x canvas, the Step-0 fixes and the GBA-unchanged harness (docs/PLAN.md "Phased rollout", Phase 1). `Platform::Snes` does not exist until Phase 2. Blocking for every later phase.

## Scope
Child issues, in merge order:
- [ ] 02-patch-pipeline
- [ ] 03-task-check-and-upstream-guard
- [ ] 04-fceumm-core-build
- [ ] 05-gba-harness-and-bench
- [ ] 06-step0-exhaustive-matches
- [ ] 07-platform-nes
- [ ] 08-core-fceumm
- [ ] 09-canvas
- [ ] 10-dist-zip-deploy
- [ ] 38-dev-tools-mise

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | T1 to T14 and T45 are owned by the child issues above |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Each edge case is owned by the child issue that touches that layer |

## Acceptance
Phase 1 ships when:
- [ ] T1 to T14 and T45 green under `SLOT_REQUIRE_CORES=1` on macOS.
- [ ] `scripts/check-upstream-tests.sh` reports 0 changed test blocks (upstream test code unmodified).
- [ ] `task harness:control` 0 diffs; `task harness:compare` 0 diffs on H1/H2; H3 equals H1.
- [ ] `task bench:compare` within 2% for mgba and gpsp.
- [ ] fceumm licence gate recorded in `LICENSING.md`.
- [ ] Host smoke: `task run:4x3` (`SLOT_WINDOW=1280x960`) exercises the RG35XXSP bezel path with a NES cart.
- [ ] Device check below passes.

## Device check (RG35XXSP)
1. Unzip `slot-nes-snes-v1.6.0-ns.0-h700.zip`, copy the top folder's contents to the SD root, boot.
2. The NES shelf appears after GBC.
3. Super Mario Bros. 3 and Mega Man 2 (user-owned dumps, never committed) are playable at full speed, save on eject and resume on reboot.
4. A GBA cart still plays.
5. `task log:device`: `slot.log` shows `slot: core /mnt/sdcard/System/fceumm_libretro.so` and no `running the mock test pattern` line.

## Review notes
- Open question 1 (can "unmodified" hold for every upstream test) proceeds with the default: yes. If a child PR cannot hold it, stop and raise it here rather than amending upstream asserts.
- Every child PR changes code only in `work/slot` on branch `nes-snes` and ships the re-exported `patches/*.patch`; `.patch` files are never hand-edited.

## References
- docs/PLAN.md: Phased rollout (Phase 1), Evaluation criteria (Acceptance gates), Manual smoke tests, Open questions
- docs/QUALITY-BAR.md
