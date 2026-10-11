---
title: "Phase 3: full NES/SNES parity"
phase: 3
area: device
type: tracking
size: L
depends_on: [11-phase-2-snes]
---

## Why
Every parity row (carousel, letter jump, cart art and labels, core picker, insert and eject, resume on boot, saves and autosave, save states and polaroids, rewind, fast-forward, turbo, shaders, video mode, quick menu, settings, volume, sleep and lid-close save) must work on NES and SNES (docs/PLAN.md Spec success 2, Phased rollout Phase 3). Blocking.

## Scope
Child issues, in merge order:
- [ ] 19-alt-cores-build
- [ ] 20-core-picker-pairs
- [ ] 21-shaders
- [ ] 22-ff-and-rewind
- [ ] 23-states-quickmenu-resume

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | T23 to T33 are owned by the child issues above |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Each edge case is owned by the child issue that touches that layer |

## Acceptance
Phase 3 ships when:
- [ ] T1 to T33 green (real-core tests under `SLOT_REQUIRE_CORES=1`).
- [ ] Every row of the AC-to-code coverage table in docs/PLAN.md is ticked with a passing test.
- [ ] Harness 0 diffs; H3 equals H1.
- [ ] nestopia licence gate recorded in `LICENSING.md`.
- [ ] All 6 cores open on the device.
- [ ] Gate numbers recorded in `docs/DEVICE-GATE.md`.
- [ ] Host smoke: `task run:4x3` on NES and SNES.

## Device check (RG35XXSP)
1. The picker swaps fceumm and nestopia, and snes9x and snes9x2005_plus, with the correct socket names; the choice survives a reboot.
2. Rewind (L2) and FF (R2) on Super Mario RPG with zero underruns in `SLOT_TRACE`.
3. Shaders cycle with SELECT+B/A on NES and SNES.
4. Lid close saves; sleep and wake; volume; brightness.
5. All 11 titles recorded in `docs/DEVICE-GATE.md`.

## Review notes
- "Settings, volume, sleep" are platform-agnostic upstream code; they are verified by T26 plus this device check.

## References
- docs/PLAN.md: Phased rollout (Phase 3), AC-to-code coverage stub, Evaluation criteria (Acceptance gates), Manual smoke tests
