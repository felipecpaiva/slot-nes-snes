---
title: "Atari 2600 device gate on the RG34XXSP"
phase: 14
area: device
type: chore
size: S
depends_on: [158-a2600-canvas-screen, 159-a2600-input-switches, 160-a2600-pal-pacing]
---

## Why
Prove the 2600 shelf on the device before it ships.

## Scope
- [ ] Pitfall!, River Raid, Space Invaders, Yars' Revenge, Solaris and one PAL dump, 10 minutes each: full speed, zero underruns, ms a frame (PERFORMANCE.md row).
- [ ] Difficulty and TV rows take effect; Reset and Select work; eject and GBA.

## Tests
| ID | File | Asserts |
|---|---|---|
| (device) | `scripts/bench-device.sh` | ms a frame per game |

## Edge cases
| Case | Expected handling |
|---|---|
| A game draws past 240 rows | Crop visible in Actual, Stretch shows all |

## Acceptance
- [ ] DEVICE-GATE.md row.

## Device check (RG34XXSP)
This issue.

## References
- ADR 0095; docs/research/atari-plan.md
