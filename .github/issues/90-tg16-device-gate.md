---
title: "TG16 device gate on the RG34XXSP"
phase: 10
area: device
type: chore
size: S
depends_on: [85-tg16-canvas-screen, 86-tg16-saves, 87-tg16-input]
---

## Why
The phase gate: real HuCards on the real device, as for every system.

## Scope
- [ ] Bonk's Adventure, R-Type, Air Zonk and Blazing Lazers, 10 minutes each under `SLOT_TRACE`: full speed, zero audio underruns, ms a frame recorded (estimate 1.5 to 3 ms, unmeasured).
- [ ] A game that switches to a wider dot clock (found from the trace's frame width first) and a 512-wide screen if one exists: the 2:1 blend looks right and Stretch follows the width.
- [ ] A BRAM save (a HuCard that saves to backup RAM, or Populous): save, close the lid, pull the battery, boot; the save is there.
- [ ] Eject and GBA: the GBA leg equals a GBA-only run.

## Tests
| ID | File | Asserts |
|---|---|---|
| (device) | log in docs/ | the numbers above |

## Edge cases
| Case | Expected handling |
|---|---|
| A game over budget | Record it; frameskip stays off unless the maintainer decides otherwise |

## Acceptance
- [ ] Every scope line checked and logged.

## Device check (RG34XXSP)
This issue.

## References
- ADR 0091; docs/research/tg16-plan.md section 8
