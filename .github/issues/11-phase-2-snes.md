---
title: "Phase 2: SNES"
phase: 2
area: device
type: tracking
size: L
depends_on: [01-phase-1-nes-boots]
---

## Why
Adds `Platform::Snes` with snes9x, the libretro env calls SNES cores need, hi-res blending and SNES input (X/Y/L/R to the game, SELECT+X for picture mode) (docs/PLAN.md "Phased rollout", Phase 2). Blocking.

## Scope
Child issues, in merge order:
- [ ] 12-platform-snes
- [ ] 13-snes9x-core-build
- [ ] 14-libretro-env-and-hires
- [ ] 15-snes-input
- [ ] 16-frontend-cost-eval
- [ ] 17-device-gate-log

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | T15 to T22b are owned by the child issues above |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Each edge case is owned by the child issue that touches that layer |

## Acceptance
Phase 2 ships when:
- [ ] T1 to T22b green (real-core tests under `SLOT_REQUIRE_CORES=1`).
- [ ] Harness control and compare still 0 diffs; H3 equals H1.
- [ ] SNES frontend cost passes `evals/eval-frontend-cost.sh`.
- [ ] Host smoke: `task run:4x3` with a SNES cart.
- [ ] SNES buttons and chords verified on device (below).

## Device check (RG34XXSP)
1. Super Mario World and Super Metroid run at full speed.
2. X, Y, L and R reach the game.
3. A SELECT tap reaches the game; SELECT+R1 saves a state without sending R; SELECT+Y sends no Y and does nothing; SELECT+X toggles Stretch/Actual.
4. First pass over the five SNES gate titles (Star Fox, Yoshi's Island, Kirby Super Star, Super Mario RPG, Seiken Densetsu 3), recorded in `docs/DEVICE-GATE.md` (see 17-device-gate-log). A gate failure here informs Phase 3 and does not block.

## Review notes
- snes9x is licensed for non-commercial use only; the licence and notice obligations are in 13-snes9x-core-build.

## References
- docs/PLAN.md: Phased rollout (Phase 2), Evaluation criteria (Acceptance gates), Manual smoke tests
