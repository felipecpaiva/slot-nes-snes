---
title: "Flip and swap disks with SELECT+L2 through fceumm's own drive buttons"
phase: 18
area: input
type: feature
size: M
depends_on: [195-platform-fds]
---

## Why
fceumm registers no disk-control interface at its pin; it ejects and inserts on R and selects the next side on L. Players need one clear control.

## Scope
- [x] SELECT+L2 on this shelf: R, then L, then R one second later, pressed by slot in the emu thread; L1 and R1 never reach the core.
- [x] The side is read back from the core's state (SELD) and shown: "Disk 1 Side B", "Disk 2 Side A".
- [x] A one-sided disk is not flipped; the PS1 disc path is not used.

## Tests
| ID | File | Asserts |
|---|---|---|
| D1 | `fds_core.rs` | no BIOS no load, save RAM is the disk, eject held a second, every side walked, state keeps the side |
| D2 | `fds_saves.rs` | SELECT+L2 in a seated game shows Disk 1 Side B |

## Edge cases
| Case | Expected handling |
|---|---|
| a state loaded on another side | the next banner reads the core's side |
| rewound into the second the disk is out | documented gap, SELECT+L2 again |

## Acceptance
- [x] D1 and D2 pass.

## Device check (RG34XXSP)
Issue 202, step 4.

## References
- ADR 0101, ADR 0067
