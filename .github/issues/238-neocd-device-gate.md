---
title: "Neo Geo CD device gate on the RG34XXSP"
phase: 23
area: device
type: chore
size: S
depends_on: [235-platform-neocd, 236-neocd-bios, 237-neocd-cases]
---

## Why
No host number is a device number. NeoCD's 68000 is the C Musashi core, and the CHD reader and the load skip run in the emulation thread.

## Scope
- [ ] Copy the staged discs to the Expansion Card (`Games/NEOCD`, the `NEOCD` line in `Config/expansion.txt`) and the BIOS files to `BIOS/neocd/`.
- [ ] bench:device on both discs; real play, 10 minutes each, during CD audio and loads.
- [ ] Record the rows in docs/DEVICE-GATE.md (Neo Geo CD section).

## Tests
| ID | File | Asserts |
|---|---|---|
| (device) |  | `slot.log` under `SLOT_TRACE`: no missed frames past the first window, `starved` 0, `dropped` 0 |

## Edge cases
| Case | Expected handling |
|---|---|
| A frame budget miss in play | try the Front or Top Loader, then a CPU governor note; amend ADR 0107 |

## Acceptance
- [ ] Both titles pass or have a recorded row.

## Device check (RG34XXSP)
This issue is the device check.

## References
- ADR 0107
