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

- **v1:** port 0 is JOYPAD. `owns_shoulders` is false for PS1, as for SNES and Mega Drive, so L1
  and R1 go to the game (the policy answers whether slot owns the buttons; false hands them to the
  game). A new `owns_triggers` platform policy with the same polarity is true everywhere except
  PS1, so L2 and R2 go to the game on PS1 only (gmaster1998's toggle shape). With L1 and R1 taken, the in-game picture toggle is
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

## Amendment (2026-10-17, issue 62 build)

- The first draft said `owns_shoulders` is true for PS1. In code it answers whether slot owns L1
  and R1, so PS1, SNES and Mega Drive answer false. The decision above now says so.
- `owns_triggers` is checked once, when the session starts, and turns `Gestures` into its
  triggers-to-the-game mode: L2 and R2 then go to the game like any other button, never to rewind
  or fast-forward.
- **SELECT+R2 toggles fast-forward:** one press turns it on, the next turns it off. It is latched,
  so ejecting the game stops it, and R2 never reaches the game, whichever of SELECT and R2 is let
  go first. SELECT+L2 swaps the disc (ADR 0067). SELECT alone still reaches the game once the
  chord window closes, as on SNES.
- `ButtonMask` gains `L2` (bit 12) and `R2` (bit 13), the libretro ids. Only PS1 ever sets them.
- An L2 or R2 still held when the game is ejected is let go to the core first, so the eject save
  does not record a held trigger.


## Amendment (2026-10-17, issue 65 build: v2 done)

- **Sticks:** `input/sticks.rs` maps the four ABS codes to left X, left Y, right X and right Y,
  drops the deadzone (32) and scales -4096..4096 to -32767..32767. Each stick event publishes all
  four axes to one `AtomicU64` in slot-retro (`analog.rs`), not the button `AtomicU16`. The core
  latches it once per frame. The hat and the button word are unchanged.
- **Map:** the default is left 0x02/0x03, right 0x04/0x05, first two axes left as Linux orders
  them. It is unverified: the spike's pairs 0x03/0x04 and 0x02/0x05 were what its tool assumed,
  not what it measured. `Config/sticks.txt` overrides it (`left_x=0x03`, a leading minus inverts,
  `deadzone=`, `range=`), and `scripts/stick-check.sh` prints the right file from the device.
  Runtime detection cannot work: nothing in the events says which stick moved.
- **Only a plugged core sees the sticks.** mGBA asks for `RETRO_DEVICE_ANALOG` too, so answering it
  for every core would change GBA. `analog_pad(Core)` plugs a pad for pcsx only; every other core
  gets centre, and a test runs mGBA and gpSP byte-identical with the sticks pushed.
- **DualShock always, no per-game toggle.** pcsx's DualShock starts in digital mode (id 0x41), so
  digital games see a standard pad. Games that switch it (Ape Escape) or pcsx's
  `dualshock_init_analog` list get analog. Others switch with L1+R1+SELECT, pcsx's declared default
  combo, answered under ADR 0064. ADR 0008 rules out the quick-menu row a toggle would need.
- **L3 and R3 wait.** The key bitmap has no BTN_THUMBL or BTN_THUMBR. 0x139 and 0x13c are
  reported and unmapped, and may be the stick clicks. The check script prints the codes; they are
  mapped once the device confirms them.
- **Rumble:** event1 reports FF_RUMBLE. pcsx's DualShock rumble (`pcsx_rearmed_vibration`, enabled)
  reaches slot's existing `Rumble` path, so it buzzes when the Rumble row is on. Needs a device check.
