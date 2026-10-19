---
title: "Lynx device gate on the RG34XXSP"
phase: 12
area: device
type: chore
size: S
depends_on: [104-lynx-bios-check, 107-lynx-pacing, 109-lynx-input-rotation]
---

## Why
The last step: real games on the device with the maintainer's own BIOS (`/mnt/sdcard/BIOS/lynxboot.img`, md5 `fcd403db69f54290b51035d82f835e7b`).

## Scope
- [ ] California Games, Chip's Challenge, Blue Lightning, Klax (right-turned) and Lexis (left-turned), 10 minutes each under `SLOT_TRACE`: full speed at Native, zero audio underruns, the measured rate of each (59.9 or 75), and ms a frame (estimate 1 to 2.5 ms, x1.25 at 75 Hz).
- [ ] Missing BIOS: the toast, no dark screen.
- [ ] Turned carts: the flip direction feels right on the clamshell; the d-pad matches.
- [ ] Eject and GBA: the GBA leg equals a GBA-only run.
- [ ] If Handy is picked: the same list without a BIOS, to see whether its HLE boot runs real carts.

## Tests
| ID | File | Asserts |
|---|---|---|
| (device) | docs/DEVICE-GATE.md "Lynx" | the table above |

## Edge cases
| Case | Expected handling |
|---|---|
| A game at neither 60 nor 75 Hz | Native follows it; record it |

## Acceptance
- [ ] Results recorded in docs/DEVICE-GATE.md.

## Device check (RG34XXSP)
This issue.

## References
- ADR 0093; docs/research/lynx-plan.md section 8
