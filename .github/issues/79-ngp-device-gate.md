---
title: "NGP device gate on the RG34XXSP"
phase: 9
area: device
type: chore
size: S
depends_on: [74-ngp-canvas-screen, 75-ngp-flash-saves, 76-ngp-input]
---

## Why
Step 10. The host tests cover no frame pacing, audio or real flash on the H700. NeoPop's cost is an estimate (1 to 2 ms a frame, unmeasured).

## Scope
- [ ] Measure ms a frame with `bench:device` on a generated cart and a real one.
- [ ] Real play, 10 minutes each under `SLOT_TRACE`: SNK vs. Capcom: Match of the Millennium, Metal Slug 2nd Mission, Sonic the Hedgehog Pocket Adventure.
- [ ] Flash: save in-game, close the lid, pull the battery, boot. The save is there resuming and starting fresh.
- [ ] Record the rows in docs/DEVICE-GATE.md (a NeoGeo Pocket section).

## Tests
| ID | File | Asserts |
|---|---|---|
| (device) | `scripts/auto-play.sh` with an NGP pair | per title: 0 presents above 1.5x the period after the first window, `starved` 0, `dropped` 0, no panic |

## Edge cases
| Case | Expected handling |
|---|---|
| Lid closed while the core is writing flash | The atomic publish (issue 75) leaves the previous file whole |

## Acceptance
- [ ] Every title passes; the flash survives the battery pull.

## Device check (RG34XXSP)
This issue is the device check.

## References
- ADR 0090; issue 63 for the auto-play recipe; docs/research/ngp-plan.md section 8
