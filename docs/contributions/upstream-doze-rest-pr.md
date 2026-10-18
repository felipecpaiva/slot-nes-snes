# PR title

Stop drawing while the lid is shut or POWER has dozed the game

# PR body

## Problem

In `Phase::Doze` the backlight is off and the core is paused, but the device loop still steps,
composes and presents a black frame at about 60 Hz for the whole doze. With Lid Off reaching
30 minutes that is a lot of GPU and CPU work behind a dark panel.

## Change

- After two dark frames (one per swap buffer), the loop in `device_app.rs` stops calling
  `step_emulator`, `render` and the swap, and sleeps 50 ms per turn instead of `Pacer::wait`.
  It still calls `advance` every turn, so input, the lid, the timers, the doze power-off and a
  restart all work as before. A pending shutdown or restart, a live link, or a label rebuild keeps
  the loop drawing.
- On each resting turn the pacer forgets its last present, so the first frame after a wake is not
  counted as a missed latch.
- Two log lines: `slot: doze: resting after 2 dark frames, polling every 50 ms` on entering, and
  on waking `slot: doze: awake after 34.2 s, 2 presents (0.06 per second), 640 polls, 30 ms of cpu`
  (process CPU time from `/proc/self/stat`), so the change can be checked from `slot.log` alone.
- Waking costs at most one 50 ms poll after the wake event is read.

## Tests

New `crates/slot/tests/standby.rs`: the rest state machine (dark frames, then rest; a wake draws at
once; the next doze starts dark again), both log lines, the `/proc/self/stat` parser, and the rest
condition for a shut lid, a doze power-off and a link. `device_app.rs` has no host test; it builds
and lints with `--features device`.

Device: lid shut for 30 s with a game running, then open: `slot.log` shows the two lines, 2
presents, about 20 polls per second, and the picture is back at once.

## Credit

From marghost/slot_modded b1f9e24, which adapts suprsomething/slot.advance bf810b6 (both GPL-3.0).
