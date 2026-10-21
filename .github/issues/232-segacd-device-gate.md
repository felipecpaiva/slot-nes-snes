---
title: "Sega CD device gate on the RG34XXSP"
phase: 22
area: device
type: chore
size: S
depends_on: [224-segacd-bios-check, 227-segacd-backup-ram, 228-segacd-discs, 231-segacd-cases]
---

## Why
A real game boots only through a real BIOS and a real disc, which CI does not have, and the flush by reload at lid close is accepted only if it is fast enough on the device (ADR 0105).

## Scope
- [ ] The steps in docs/DEVICE-GATE.md (Sega CD) on the maintainer's own BIOS and discs from the Expansion Card.
- [ ] Record the rows, the reload times included.
- [ ] If the warm reload at lid close is over 100 ms: amend ADR 0105 and flush only at eject, autosave and quick-menu open.

## Tests
| ID | File | Asserts |
|---|---|---|
| (device) | docs/DEVICE-GATE.md | |

## Edge cases
| Case | Expected handling |
|---|---|
| (device) | |

## Acceptance
- [ ] Every step passes or has an issue.

## Device check (RG34XXSP)
This issue.

## References
- ADR 0094, 0098, 0105; docs/research/segacd-plan.md sections 3 and 8
