---
title: "WonderSwan device gate on the RG34XXSP"
phase: 11
area: device
type: chore
size: S
depends_on: [93-platform-wswan, 95-wswan-canvas-screen, 96-wswan-input]
---

## Why
Step 10. The host tests cover no frame pacing, audio or input feel on the H700. Cygne's cost is an estimate (1 to 2 ms a frame, plus 0.1 to 0.3 ms for the core's rotation copy on vertical games, unmeasured).

## Scope
- [ ] Measure ms a frame with `bench:device` on a generated cart and a real one, horizontal and vertical.
- [ ] Real play, 10 minutes each under `SLOT_TRACE`: Gunpey (vertical), Judgement Silversword (vertical shooter), Klonoa: Moonlight Museum, Final Fantasy (Color).
- [ ] Both Refresh values on one horizontal and one vertical game: Native's `owed_frames` cadence shows no worse judder than 60 Hz mode.
- [ ] Save, eject, boot: the save is there resuming and starting fresh.
- [ ] Answer issue 96's question: are the shoulder modifiers comfortable, or should L2 and R2 carry the Y pad as an option.
- [ ] Record the rows in docs/DEVICE-GATE.md (a WonderSwan section).

## Tests
| ID | File | Asserts |
|---|---|---|
| (device) | `scripts/auto-play.sh` with a WonderSwan pair | per title: 0 presents above 1.5x the period after the first window, `starved` 0, `dropped` 0, no panic |

## Edge cases
| Case | Expected handling |
|---|---|
| Native refresh on a vertical game | Same pass bar as 60 Hz mode |

## Acceptance
- [ ] Every title passes in both Refresh values.

## Device check (RG34XXSP)
This issue is the device check.

## References
- ADR 0092; issue 63 for the auto-play recipe; docs/research/wswan-plan.md section 9
