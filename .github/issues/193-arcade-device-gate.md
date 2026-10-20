---
title: "Arcade device gate on the RG34XXSP"
phase: 17
area: device
type: chore
size: S
depends_on: [187-arcade-screen, 190-arcade-input]
---

## Why
The host proves behaviour, not speed on the H700.

## Scope
- [ ] docs/DEVICE-GATE.md arcade section: bench:device and real play of a Neo Geo, a CPS1 and a CPS2 set, a vertical game both ways, the BIOS toast, the six-button map.

## Tests
| ID | File | Asserts |
|---|---|---|
| G1 | `docs/DEVICE-GATE.md` | every arcade row passes on the device |

## Edge cases
| Case | Expected handling |
|---|---|
| A set missing frames | report it with the bench numbers before adding a speed row |

## Acceptance
- [ ] G1 done by the maintainer.

## Device check (RG34XXSP)
This issue.

## References
- ADR 0099
