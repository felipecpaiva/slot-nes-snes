---
title: "Famicom Disk System device gate on the RG34XXSP"
phase: 18
area: device
type: chore
size: S
depends_on: [197-fds-bios, 198-fds-disk, 199-fds-saves]
---

## Why
The disk flip and a game writing its disk need a real BIOS and a real game, which CI does not have.

## Scope
- [ ] The steps in docs/DEVICE-GATE.md (Famicom Disk System) on the maintainer's own BIOS and disks.
- [ ] Record the rows.

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
- ADR 0101
