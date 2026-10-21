---
title: "PICO-8 device gate on the RG34XXSP"
phase: 18
area: device
type: chore
size: S
depends_on: [196-platform-pico8, 197-pico8-carts]
---

## Why
Host numbers are a direction; the H700 sets the bar.

## Scope
- [ ] docs/DEVICE-GATE.md "PICO-8" steps 1 to 8 on Cave Runners!, UFO Swamp Odyssey, Celeste and Pico de Pon.

## Tests
| ID | File | Asserts |
|---|---|---|
| D1 | docs/DEVICE-GATE.md | speed, picture, controls, audio, cartdata across a power cut, no states, errors, logs |

## Edge cases
| Case | Expected handling |
|---|---|
| A cart misses frames | record it; FAKE-08 has no frameskip option, so it is a known gap |

## Acceptance
- [ ] D1 filled in.

## Device check (RG34XXSP)
This issue.

## References
- ADR 0101
