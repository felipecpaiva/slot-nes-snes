# 0068. Ship PS1 with the digital pad and L2/R2 to the game, and analog DualShock in v2

- Status: Accepted
- Date: 2026-10-17
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0066](0066-ps1-rewind-and-run-ahead-off.md), [PS1 spike](../research/ps1-spike.md) Results, [issue 62](../../.github/issues/62-ps1-input.md), [issue 65](../../.github/issues/65-ps1-analog.md)

## Context

pcsx treats `RETRO_DEVICE_JOYPAD` as the standard digital pad, so most of the library plays with
it. `ButtonMask` bits 12 to 15 match the libretro ids for L2, R2, L3 and R3. Upstream uses L2
and R2 for rewind and fast-forward. Some games need analog: Ape Escape, and analog steering or
camera. The spike proved the RG34XXSP sticks are analog. They are four axes on event1
"ANBERNIC-keys": codes 0x02 to 0x05 (ABS_Z, ABS_RX, ABS_RY and ABS_RZ, not ABS_X and ABS_Y),
-4096 to 4096, flat 32, more than 100 distinct values each. The diagonals pair them 0x03/0x04
and 0x02/0x05.

## Decision

- **v1:** port 0 is JOYPAD. `owns_shoulders` is true for PS1, as for SNES and Mega Drive, so L1
  and R1 go to the game. A new `owns_triggers` platform policy hands L2 and R2 to the game on
  PS1 only (gmaster1998's toggle shape). With L1 and R1 taken, the in-game picture toggle is
  SELECT+X, the SNES and Mega Drive chord (ADR 0007). GBA, GB, GBC and the other systems keep upstream's
  rewind and fast-forward gestures. The face buttons follow position: Cross on B, Circle on A,
  Square on Y and Triangle on X.
- **v2:** a separate issue reads the four stick axes into an atomic beside the button
  `AtomicU16`, so GBA input timing does not change. It adds a deadzone and calibration, answers
  `RETRO_DEVICE_ANALOG`, sets DualShock per game, and adds L3 and R3.

## Consequences

- v1 needs no evdev change. v2 also answers the N64 spike's stick question.
- PS1 fast-forward is SELECT+R2, since R2 belongs to the game (ADR 0066).
- Analog-only games do not work until v2. The README known gaps say so.
- v2 has to find out which axis pair is the left stick, and whether the device has a rumble
  motor. Both are unknown today.
