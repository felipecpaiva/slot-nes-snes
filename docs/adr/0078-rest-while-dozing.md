# 0078. Stop drawing while dozing

- Status: Accepted. Drop when the upstream PR lands (0047). Amends [0033](0033-keep-upstream-lid-timeout.md) (the doze loop only)
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0033](0033-keep-upstream-lid-timeout.md), [ADR 0047](0047-upstream-first-fixes.md), patch `patches/0051-doze-rest.patch`, patch `0015-frame-trace`, [fork review](../research/fork-review-2026-10-18.md), marghost/slot_modded [b1f9e24](https://github.com/marghost/slot_modded/commit/b1f9e24), suprsomething/slot.advance [bf810b6](https://github.com/suprsomething/slot.advance/commit/bf810b6), upstream PR text in [docs/contributions/upstream-doze-rest-pr.md](../contributions/upstream-doze-rest-pr.md)

## Context

With the lid shut or after a POWER tap, `Phase::Doze` turns the backlight off and pauses the core
(`sync_speed` sets `Speed::Paused` while dozing), but the device loop in `device_app.rs` keeps
stepping, composing and presenting a black frame at about 60 Hz for the whole doze, 3 minutes by
default (ADR 0033), longer once upstream's Lid Off row (2c82294) lands. Both forks stop
presenting after two dark frames (one per swap buffer) and sleep 50 ms per turn. The battery
current cannot be read over USB (USB charges the device), so the change has to be visible in the
log.

## Decision

- New `crates/slot/src/doze_rest.rs`: `rests(app)` is true when the phase is `Doze`, the doze
  fade has reached black (`screen_power()` is 0, about 0.16 s after the lid shuts, `POWER_OFF_S`),
  no shutdown or restart is pending, and no link is active. Without the fade check the two dark
  frames would be partly faded game frames left in both swap buffers, and the wake would flash one
  for a vsync when the backlight comes back. `DozeRest::step` lets two dark frames through
  (`DARK_FRAMES`), then rests. The device loop also requires `!frontend.rebuilding_labels()`,
  because a label rebuild ignores input and finishes only from `render`.
- While resting the loop sleeps `DOZE_POLL` (50 ms) instead of `Pacer::wait`, still calls
  `frontend.advance` (input, lid, timers, the doze power-off, restart), and skips
  `step_emulator`, `render` and the present. A doze timeout sets `powering_off`, so `rests` turns
  false and the shutdown screen is drawn as before.
- On every rest turn the pacer forgets its last present (`last_return`, `seen`), so the first
  frame after a wake is not counted as a missed latch by upstream's pace counter, nor as a long
  frame by patch 0015's frame trace. Those counters are not touched while resting.
- Log lines, always on (not gated on latency tracing):
  - entering: `slot: doze: resting after 2 dark frames, polling every 50 ms`
  - leaving: `slot: doze: awake after 34.2 s, 2 presents (0.06 per second), 640 polls, 30 ms of cpu`.
    The CPU part is this process's user plus system time over the doze, from `/proc/self/stat`
    (10 ms ticks); it is left out where that file does not exist.
- Link case, checked: `doze()` ends the link first (`end_link`, app.rs) and the core is paused
  while dozing, so resting cannot stall a peer. If a link handshake still completes during a
  doze, `link_active()` makes `rests` false and the loop draws as it did before.
- No setting: nothing is shown while resting, and wake cost is at most one poll.

## Consequences

- Wake: the poll adds at most 50 ms plus one frame after the wake event is seen. The lid is read
  from evdev `SW_LID` or, where the device exposes a hall file, polled every 150 ms
  (`LID_POLL_MS`, upstream, unchanged), so the worst case from lid open to a picture is about
  150 + 50 + 17 ms on the hall path, and 50 + 17 ms on the POWER button or evdev lid.
- The emu thread is unchanged: while paused and unlocked it already sleeps one period per turn.
- `crates/slot/tests/doze_rest.rs`: the rest state machine, both log lines, the `/proc/self/stat`
  parser, and `rests` for a shut lid, a fade still in progress, a doze power-off and a link begun
  behind a shut lid.
- `device_app.rs` has no host test; it is compiled and linted by `task lint`
  (`--features device`). The device check is in the patch report.
- **Drop the patch when the upstream PR lands.**
