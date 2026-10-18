# 0081. START closes the core picker it opened

- Status: Accepted. Drop when the upstream PR lands (0047)
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0047](0047-upstream-first-fixes.md), patch `patches/0052-start-closes-picker.patch`, patch `0009-core-picker-pairs`, [fork review](../research/fork-review-2026-10-18.md), jgraving/slot [e047d17](https://github.com/jgraving/slot/commit/e047d17), upstream PR text in [docs/contributions/upstream-start-closes-picker-pr.md](../contributions/upstream-start-closes-picker-pr.md)

## Context

START opens the core picker on the shelf, and only B closes it without a change. jgraving/slot
e047d17 (GPL-3.0) maps START to Back too, so START toggles the picker.

## Decision

One token in `core_picker_input`: `Action::GbaDown(Btn::B | Btn::Start) => Press::Back`.

## Consequences

- `crates/slot/tests/start_closes_picker.rs`: START closes the picker; START after moving the
  chip closes it and keeps the core.
- Upstream `crates/slot/tests/app.rs` passes unchanged, but one test loses part of its reach:
  `presses_during_the_close_and_keys_the_picker_does_not_use_do_nothing` lists START among the
  keys the picker does not use (`[Up, Down, Start, Select]`). It still passes because
  `core_picker()` keeps the seated core during the close animation, but after this change its
  START press starts the close, so the Select press after it is checked during the close rather
  than on an open picker.
  The upstream PR text asks Brandon to drop START from that list (his test, his call); we do not
  edit it.
- The device sends no key repeats (`evdev::to_raw` drops value 2), so a held START cannot open
  and close the picker at once.
- **Drop the patch when the upstream PR lands.**
