---
title: "Read the RG34XXSP analog sticks and offer the DualShock on PS1 (v2)"
phase: 8
area: input
type: feature
size: L
depends_on: [62-ps1-input]
---

## Why
Step 12. Analog-only PS1 games need the sticks (ADR 0068, v2). No fork has done it. The spike proved the sticks are analog.

## Findings (spike, 2026-10-16)
- Node event1 "ANBERNIC-keys": ABS codes 0x02, 0x03, 0x04, 0x05 (ABS_Z, ABS_RX, ABS_RY, ABS_RZ), -4096 to 4096, flat 32, fuzz 32. Not ABS_X and ABS_Y.
- Diagonal pairs: 0x03/0x04 and 0x02/0x05. Which is the left stick is unknown.
- Correction (build, 2026-10-17): the spike's `stickread` only counted the pairs it assumed (X/Y, RX/RY, Z/RZ) while both sticks circled, so those "pairs" are not a measurement. The pairing is unknown.
- Key bitmap of event1: codes 0x130 to 0x13c. No BTN_THUMBL or BTN_THUMBR (0x13d, 0x13e). Codes 0x139 and 0x13c are reported and unmapped in slot; they may be L3 and R3, unverified.
- `FF=107030000 0` on event1: FF_RUMBLE and the periodic effects, so a rumble motor is likely.

## Scope
- [x] Read the four axes in `device.rs` (new `input/sticks.rs`) into one `AtomicU64` in slot-retro, apart from the button `AtomicU16`, so GBA input timing does not change. The core latches it once per frame.
- [x] Deadzone (flat 32) and calibration: `Config/sticks.txt` names each axis code, a leading minus inverts it, plus `deadzone` and `range` (default 4096).
- [x] Answer `RETRO_DEVICE_ANALOG` in `input_state`, only for a core slot plugged a pad into (pcsx), so mGBA, which does ask for analog, still sees centre.
- [x] `set_controller_port_device(0, DualShock)` always on PS1, not behind a per-game toggle: pcsx's DualShock starts in digital mode (pad id 0x41), so digital games see a standard pad, and ADR 0008 rules out a new quick-menu row. Analog-optional games switch with L1+R1+SELECT (`pcsx_rearmed_analog_combo`, answered by ADR 0064).
- [ ] L3 and R3: not wired. The device reports no BTN_THUMBL/THUMBR; `scripts/stick-check.sh` prints the codes the stick clicks send, then they get mapped.
- [ ] Find out the left/right pairing (`scripts/stick-check.sh`, needs device) and whether the rumble motor works (DualShock rumble already flows through slot's `Rumble` path when the Rumble row is on).

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot/tests/ps1_analog.rs` | only pcsx gets a pad (the DualShock); pcsx asks for the sticks once it is plugged and never on its standard pad; a PS1 disc still boots and draws; mGBA and gpSP run byte-identical frames and state with the sticks pushed |
| (new) | `slot/src/input/sticks.rs` (in-source) | deadzone, full travel to +-32767 and never past, even growth, default map, file parse, inversion, bad lines, hat codes ignored |
| (new) | `slot-retro/src/libretro/env_tests.rs` | a plugged pad answers the latched sticks per index and id; port 1 and other ids are centre; an unplugged core gets centre; JOYPAD is the default port device |
| (new) | `slot-retro/src/analog.rs` (in-source) | pack round trip; DUALSHOCK is 0x205 |

## Edge cases
| Case | Expected handling |
|---|---|
| Device with no stick node | No toggle exists; the DualShock stays centred and digital games play on the d-pad as before |
| Stick map file missing or a line bad | Default map, a `slot: sticks:` line names what was ignored |

## Acceptance
- [x] Tests green; GBA harness compare at 0 diffs.

## Device check (RG34XXSP)
Run `sh scripts/stick-check.sh` with the device on adb and write the `Config/sticks.txt` it prints (none needed if it matches the default). Then Ape Escape plays with both sticks, a digital game (Symphony of the Night) still plays on the d-pad, and a rumble-capable game buzzes with the Rumble row on.

## References
- ADR 0068; docs/research/ps1-spike.md Results "Sticks"; issue 48 (N64 shares the stick work)
