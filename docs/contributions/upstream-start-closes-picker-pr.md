# PR title

Let START close the core picker it opened

# PR body

## Problem

START opens the core picker on the shelf, but only B closes it. Pressing START again does nothing.

## Change

`core_picker_input`: `Action::GbaDown(Btn::B | Btn::Start) => Press::Back`. START now closes the
picker without changing the core, as B does.

## Tests

- New: START closes the picker; START after moving the chip closes it and keeps the core.
- `presses_during_the_close_and_keys_the_picker_does_not_use_do_nothing` in
  `crates/slot/tests/app.rs` still passes, but it lists START among the keys the picker does not
  use, and its START press now begins the close, so the Select press after it is checked during the
  close. Suggest dropping `Btn::Start` from that list; left as is here.

## Credit

From jgraving/slot e047d17 (GPL-3.0).
