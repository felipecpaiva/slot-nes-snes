# 0077. Show a Battery Low banner at 15% and at 10%

- Status: Accepted. Drop when the upstream PR lands (0047)
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0047](0047-upstream-first-fixes.md), [ADR 0067](0067-ps1-disk-control-and-disc-in-states.md) (the `DiscToast` pattern), patch `patches/0050-battery-low.patch`, [fork review](../research/fork-review-2026-10-18.md), marghost/slot_modded [1706a16](https://github.com/marghost/slot_modded/commit/1706a16), suprsomething/slot.advance [d495461](https://github.com/suprsomething/slot.advance/commit/d495461), upstream PR text in [docs/contributions/upstream-battery-low-pr.md](../contributions/upstream-battery-low-pr.md)

## Context

v1.7.0 warns about a low battery only with the LED at 20% (`BATTERY_LOW`, app.rs), which the
player cannot see while holding the device, and then powers off at 5% (`BATTERY_CRITICAL`).
suprsomething/slot.advance d495461 (GPL-3.0) added a banner at 15% and at 10%, and
marghost/slot_modded 1706a16 (GPL-3.0) took it from there. Both add two `Toast` variants to
`Toast::FIXED`, which upstream `crates/slot-ui/tests/toast.rs` pins by length and order, so the
fork edits that test.

## Decision

- One banner per threshold per discharge, "Battery Low: 15%" and "Battery Low: 10%", in a game and
  on the shelf (the HUD draws in every phase). A reading past both shows only the lower one.
  Charging or Full re-arms both. Nothing shows while dozing, during a shutdown, or at or below the
  5% power-off. The check runs in `on_battery`, on the existing 10 s battery poll.
- The banners are their own list, `BatteryToast` in `crates/slot-ui/src/battery_toast.rs`, carried
  by one `Toast::Battery` variant, as `DiscToast` is (patch 0037). `Toast::FIXED` and upstream's
  toast tests are unchanged. `Toast::every()` uploads them after the retro banners and before the
  disc banners, so the disc banners stay last (`ps1_discs.rs` checks that).
- The logic lives in `crates/slot/src/app/battery_warn.rs`. `app.rs` gets a `mod` line, the
  `battery_warned` field and its initial value, and one call in `on_battery`.
- It logs `slot: battery: low at N%` when a banner shows.
- No setting: the thresholds are not a factory default that anything else depends on, and both
  forks and the fork review agree on 15 and 10.

## Consequences

- `crates/slot/tests/battery_low.rs`, ported from marghost's `battery_warnings.rs`, plus an
  upload-order test and a shelf test. Each test was shown red by breaking one line (see the patch
  report).
- In the upstream PR the banners can simply join `Toast::FIXED`, with the matching lines in
  upstream's own `crates/slot-ui/tests/toast.rs`; that is Brandon's call. Our carried version
  keeps upstream's tests byte for byte.
- **Drop the patch when the upstream PR lands.**
