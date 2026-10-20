---
title: "Atari 7800 device gate on the RG34XXSP"
phase: 14
area: device
type: chore
size: S
depends_on: [165-a7800-bios, 166-a7800-canvas-screen, 167-a7800-input-switches, 168-a7800-pal-pacing]
---

## Why
Prove the 7800 shelf on the device before it ships.

## Scope
- [ ] Asteroids, Ms. Pac-Man, Food Fight, Ninja Golf and one PAL dump, 10 minutes each, BIOS Off and On: full speed, zero underruns, ms a frame.
- [ ] Difficulty rows, Pause, Reset row; eject and GBA.

## Tests
| ID | File | Asserts |
|---|---|---|
| (device) | `scripts/bench-device.sh` | ms a frame per game |

## Edge cases
| Case | Expected handling |
|---|---|
| BIOS On with a PAL game and only the (U) file | Toast, boots Off |

## Acceptance
- [ ] DEVICE-GATE.md row.

## Device check (RG34XXSP)
This issue.

## References
- ADR 0095; docs/research/atari-plan.md
