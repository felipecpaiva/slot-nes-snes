---
title: "32X device gate on the RG34XXSP"
phase: 15
area: device
type: chore
size: S
depends_on: [147-s32x-screen, 149-s32x-input]
---

## Why
The Mac core has no SH-2 dynarec: no host number is a device number.

## Scope
- [ ] bench:device with the dynarec on and off.
- [ ] Real play, 10 minutes each: Virtua Racing Deluxe, Star Wars Arcade, Knuckles' Chaotix.
- [ ] Record the rows in docs/DEVICE-GATE.md (Sega 32X section).

## Tests
| ID | File | Asserts |
|---|---|---|
| (device) | `slot.log` under `SLOT_TRACE` | no missed frames past the first window, `starved` 0, `dropped` 0 |

## Edge cases
| Case | Expected handling |
|---|---|
| A heavy title misses frames on Accurate and 44 kHz | played again on Fast and 22 kHz, the row recorded |

## Acceptance
- [ ] Every title passes, on the factory choice or with a recorded row.

## Device check (RG34XXSP)
This issue is the device check.

## References
- ADR 0096; docs/cart-art/S32X.md
