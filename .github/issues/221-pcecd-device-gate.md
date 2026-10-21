---
title: "PC Engine CD device gate on the RG34XXSP"
phase: 21
area: device
type: chore
size: S
depends_on: [218-platform-pcecd, 219-pcecd-bios, 220-pcecd-cases]
---

## Why
No host number is a device number, and the CHD reader decodes in the emulation thread.

## Scope
- [ ] Copy the staged discs to the Expansion Card (`Games/PCECD`, the `PCECD` line in `Config/expansion.txt`) and `syscard3.pce` to `BIOS/`.
- [ ] bench:device on Rondo of Blood and Ys Book I and II; real play, 10 minutes each; listen for a tick every few seconds in CD audio.
- [ ] Record the rows in docs/DEVICE-GATE.md (PC Engine CD section).

## Tests
| ID | File | Asserts |
|---|---|---|
| (device) |  | `slot.log` under `SLOT_TRACE`: no missed frames past the first window, `starved` 0, `dropped` 0 |

## Edge cases
| Case | Expected handling |
|---|---|
| CD audio ticks at the hunk size | restage that disc at chdman's default hunk and compare |

## Acceptance
- [ ] Every title passes or has a recorded row.

## Device check (RG34XXSP)
This issue is the device check.

## References
- ADR 0104
