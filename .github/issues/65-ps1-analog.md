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

## Scope
- [ ] Read the four axes in `input/evdev.rs` and `device.rs` into an atomic beside the button `AtomicU16`, so GBA input timing does not change.
- [ ] Deadzone (start from the reported flat 32) and calibration.
- [ ] Answer `RETRO_DEVICE_ANALOG` in `input_state`; `set_controller_port_device(0, DualShock)` behind a per-game toggle; L3 and R3.
- [ ] Find out the left/right pairing and whether there is a rumble motor.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot/tests/ps1_analog.rs` | axis values reach the core scaled to the libretro range; deadzone; GBA input unchanged |

## Edge cases
| Case | Expected handling |
|---|---|
| Device with no stick node | DualShock toggle hidden |

## Acceptance
- [ ] Tests green; GBA harness compare at 0 diffs.

## Device check (RG34XXSP)
Ape Escape plays with both sticks.

## References
- ADR 0068; docs/research/ps1-spike.md Results "Sticks"; issue 48 (N64 shares the stick work)
