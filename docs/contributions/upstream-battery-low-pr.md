# PR title

Warn with a Battery Low banner at 15% and at 10%

# PR body

## Problem

The only low battery warning is the LED at 20% (`BATTERY_LOW`), which is hard to see while
playing, and then the device powers off at 5% (`BATTERY_CRITICAL`). The power-off comes as a
surprise in the middle of a game.

## Change

- `on_battery` shows "Battery Low: 15%" and then "Battery Low: 10%", once each per discharge, in a
  game and on the shelf. A reading past both shows only the lower one.
- Charging or Full re-arms both banners.
- Nothing shows while dozing, during a shutdown, or at or below the 5% power-off, which is
  unchanged.
- Two new `Toast` variants, `BatteryLow15` and `BatteryLow10`, at the end of `Toast::FIXED`, and
  one `battery_warned: Option<u8>` on `App`. The check runs on the existing 10 s battery poll.

## Tests

- `crates/slot-ui/tests/toast.rs`: the pinned list gains the two banners (this PR adds them on
  purpose).
- New `crates/slot/tests/battery_warnings.rs`: 15% warns once; 10% warns after 15%; a reading past
  both shows only 10%; charging never warns; plugging in brings the banners back; a shut lid holds
  the banner until it opens; 4% shows no banner and powers off; the shelf shows it too.

## Credit

From marghost/slot_modded 1706a16, which adapts suprsomething/slot.advance d495461 (both GPL-3.0).
