---
title: "Virtual Boy device gate on the RG34XXSP"
phase: 16
area: device
type: chore
size: S
depends_on: [177-vb-screen, 179-vb-input]
---

## Why
No host number is a device number; the stick map and the palette need eyes on the panel.

## Scope
- [ ] bench:device with CORE=mednafen_vb on Wario Land and Red Alarm.
- [ ] Real play: Virtual Boy Wario Land, Jack Bros., Red Alarm or Teleroboxer, 10 minutes each.
- [ ] Record the rows in docs/DEVICE-GATE.md (Virtual Boy section).

## Tests
| ID | File | Asserts |
|---|---|---|
| (device) |  | `slot.log` under `SLOT_TRACE`: no missed frames past the first window, `starved` 0, `dropped` 0 |

## Edge cases
| Case | Expected handling |
|---|---|
| A game reads the right stick backwards | the stick axes in Config/sticks.txt (ADR 0068), the row recorded |

## Acceptance
- [ ] Every title passes or has a recorded row.

## Device check (RG34XXSP)
This issue is the device check.

## References
- ADR 0097; docs/cart-art/VB.md
