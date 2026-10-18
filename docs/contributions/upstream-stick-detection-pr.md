# Stick detection: design and upstream PR text (not sent)

Fork review 2026-10-18, item 21 (cloudwithax/unslot 3a8cfd0). Target: upstream main after
[bfb8bb2](https://github.com/BrandonKowalski/slot/commit/bfb8bb2) ("Steer with the left stick on
Anbernics that have one, #106 #107").

## Why design only, not code on our patch 0040

- bfb8bb2 rewrites `crates/slot/src/input/evdev.rs` and `input/device.rs`, the two files our patch
  0040 (ps1-analog) changes, and the 1.8.0 port is resolving 0040 against it now. Code written
  against 0040 today would be rewritten on that rebase.
- Reading the kernel range needs an `EVIOCGABS` ioctl on the event node. Our CONTRIBUTING allows
  `unsafe` only at listed sites, and `slot/src/input` has none, so adding one is a "stop and ask"
  item (section 9), not a small patch.
- The right home is upstream: bfb8bb2 hard-codes `ABS_LSX`/`ABS_LSY` and a list of six SKUs;
  detection replaces both, and our analog-to-core part (0040's `sticks.rs`) then rebases on it.

## Design

1. **Which axes, from capabilities.** For each picked node, read
   `/sys/class/input/eventN/device/capabilities/abs` with upstream's existing `has_bit`
   (`slot_power::has_bit`, already used by `wanted_node`). Layouts, as unslot found them:
   - `ABS_X`, `ABS_Y`, `ABS_RX`, `ABS_RY` (0x00, 0x01, 0x03, 0x04): a standard gamepad; left stick
     X/Y, right stick RX/RY.
   - `ABS_Z`, `ABS_RX`, `ABS_RY`, `ABS_RZ` (0x02, 0x03, 0x04, 0x05) without `ABS_X`: Anbernic
     stock firmware (the RG34XXSP); left stick Z/RX, right stick RY/RZ. This is bfb8bb2's fixed
     0x02/0x03 and our 0040 default.
   - `ABS_Y`, `ABS_Z`, `ABS_RY`, `ABS_RZ` without `ABS_X` or `ABS_RX`: muOS kernels.
   - Anything else: no sticks on that node. The hat (`ABS_HAT0X`/`ABS_HAT0Y`) is never a stick.
2. **Range, from the kernel.** `EVIOCGABS(code)` (`_IOR('E', 0x40 + code, struct input_absinfo)`,
   six `i32`: value, minimum, maximum, fuzz, flat, resolution) on the open node gives min and max.
   The ioctl sits next to the existing ones in `slot-power/src/device.rs` style, one `// SAFETY:`
   line.
3. **Centre, from the resting value.** The `value` read at open is the centre, unless it is more
   than 1/8 of the throw from the middle (the stick is held at boot), then the middle of min and
   max. Deadzone: 7% of the half throw (unslot), never below the kernel's `flat`.
4. **Menu steering.** `has_left_stick(target)` becomes "the node has a left stick layout", so the
   Left Stick row and `set_left_stick` follow the hardware, including a Bluetooth pad, and the SKU
   list goes away. `STICK_DEADZONE = 2048` becomes half of the detected half throw, the same 50%
   tilt bfb8bb2 picks on a 4096 throw.
5. **The user's override stays.** Our `Config/sticks.txt` (0040) is read after detection and wins
   key by key: an axis line replaces the detected code, `range` and `deadzone` replace the detected
   values. No file means detection only. Upstream has no such file; the PR does not add one.
6. **No silent fallback.** A node that reports none of the layouts logs
   `slot: input eventN: no stick layout in capabilities` once; a failed ioctl logs and falls back
   to bfb8bb2's fixed codes and a 4096 throw, so today's behaviour is the floor.

## Tests the PR would add (new file `crates/slot/tests/stick_layout.rs`)

- Each capability bitmap above maps to its axes; a bitmap with only the hat gives no sticks.
- A resting value inside 1/8 of the throw is the centre; one outside it gives the middle.
- Full throw from a detected, off-centre centre reaches the libretro limits on both sides.
- Menu steering presses the d-pad past half tilt on a detected 0..255 range as well as on
  -4096..4096 (bfb8bb2's own test, parameterised).
- A node with no stick layout leaves `left_stick_dpad()` false.

Device side (our plan D in fork-unslot.md): `sh scripts/stick-check.sh live` on the RG34XXSP shows
Z/RX/RY/RZ; the centre read at open sits inside the deadzone at rest; with `Config/sticks.txt`
deleted, a PS1 analog game still steers.

# PR title

Find the sticks from the input node's capabilities instead of a device list

# PR body

## Problem

bfb8bb2 steers menus with the left stick on six listed SKUs, on fixed codes `ABS_Z`/`ABS_RX`
(0x02/0x03) with a 2048 deadzone. A device with the same sticks under a different `BASEOS_TARGET`,
a muOS kernel that reports Y/Z/RY/RZ, or a Bluetooth pad (X/Y/RX/RY) gets no steering, and a unit
whose stick rests off zero needs a bigger deadzone than the list assumes.

## Change

- `input/evdev.rs`: `stick_layout(device: &Path) -> Option<StickLayout>` reads
  `capabilities/abs` with `has_bit` and returns the left and right axis codes for the three known
  layouts (gamepad X/Y/RX/RY, Anbernic Z/RX/RY/RZ, muOS Y/Z/RY/RZ), or `None`.
- `input/device.rs`: on open, each node with a layout reads `EVIOCGABS` per axis for min, max and
  the resting value. The centre is the resting value unless it is more than 1/8 of the throw off,
  then the middle. The hat's stick half compares against half the detected half throw.
- `has_left_stick(target)` and `LEFT_STICK_TARGETS` are removed; `set_left_stick` gets whether any
  node has a left stick layout.
- A node with no layout logs once. A failed ioctl logs and keeps bfb8bb2's codes and throw.

## Tests

New `crates/slot/tests/stick_layout.rs` (listed above). bfb8bb2's `evdev.rs` tests keep passing
unchanged except `only_the_skus_nextui_lists_with_a_left_stick_have_one`, which this replaces with
the capability cases.

## Device check

RG34XXSP: capabilities report Z/RX/RY/RZ, the menu steers as before, and the centre read at rest
sits inside the deadzone.

## Credit

The capability layouts and the rest-centre rule follow cloudwithax/unslot 3a8cfd0 (GPL-3.0).
