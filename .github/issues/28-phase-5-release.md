---
title: "Phase 5: release, CI, rebase automation and the final device gate"
phase: 5
area: release
type: tracking
size: L
depends_on: [24-phase-4-cart-art]
---

## Why
v1 ships when both CI jobs are green on the tag, the zip downloaded from GitHub installs cleanly, and the device gate passes on all 11 titles (docs/PLAN.md Phased rollout Phase 5, Spec success 4 and 5). Blocking for the v1 release.

## Scope
Child issues, in merge order:
- [ ] 29-ci-test-workflow
- [ ] 30-release-workflow
- [ ] 31-rebase-and-diffsurface

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | T41 to T44 are owned by the child issues above |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Each edge case is owned by the child issue that touches that layer |

## Acceptance
Phase 5 / v1 ships when:
- [ ] Both CI jobs green on the tag `v1.6.0-ns.N`.
- [ ] `zip-check.sh` passes on the downloaded asset.
- [ ] The zip installs on a clean SD card.
- [ ] The device gate passes on all 11 titles (0 underruns per 10 minutes, p99 frame time under 16.7 ms), recorded in `docs/DEVICE-GATE.md`.
- [ ] Host smoke: `task run:4x3`.

Post-release signals (tracked, not blocking): 0 new files in `crash/` on the SD card after a week of use; 0 issues labelled `gba-regression`. Adoption success is declared when two consecutive slot releases are each rebased in one session with zero GBA regressions reported.

## Device check (RG35XXSP)
1. Download the release zip from GitHub (not a local build).
2. Clean install: unzip, copy the top folder's contents to a freshly formatted SD root, boot.
3. Play each of the 11 gate titles for 10 minutes; record fps, underruns and governor in `docs/DEVICE-GATE.md`.
4. Update path: delete `System/`, copy the new `System/`, boot; `Config/` (core choices, shaders, cart shells) survives.

## Review notes
- Release notes must carry the snes9x non-commercial notice and "do not report to slot's tracker" (see 30-release-workflow).

## References
- docs/PLAN.md: Phased rollout (Phase 5), Outcome verification mechanisms, Evaluation criteria (Acceptance gates), Manual smoke tests
