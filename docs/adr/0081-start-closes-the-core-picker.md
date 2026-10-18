# 0081. START closes the core picker it opened: upstream only

- Status: Accepted (not carried)
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0047](0047-upstream-first-fixes.md), [ADR 0079](0079-favourite-removal-confirm-upstream-only.md) (the same call), patch `0009-core-picker-pairs`, [fork review](../research/fork-review-2026-10-18.md), jgraving/slot [e047d17](https://github.com/jgraving/slot/commit/e047d17), upstream PR text in [docs/contributions/upstream-start-closes-picker-pr.md](../contributions/upstream-start-closes-picker-pr.md)

## Context

START opens the core picker on the shelf, and only B closes it without a change. jgraving/slot
e047d17 (GPL-3.0) maps START to Back too (`Action::GbaDown(Btn::B | Btn::Start) => Press::Back` in
`core_picker_input`), so START toggles the picker.

Upstream `crates/slot/tests/app.rs` would pass unchanged, but
`presses_during_the_close_and_keys_the_picker_does_not_use_do_nothing` lists START among the keys
the picker does not use (`[Up, Down, Start, Select]`). With the change it still passes only
because `core_picker()` keeps the seated core during the close animation, and its Select press
would then be checked during the close rather than on an open picker.

## Decision

Not carried. The maintainer decided on 2026-10-18 that it goes upstream only: it touches an
upstream-tested flow, and a one-token patch is still one thing more to merge on every rebase. The
PR text is prepared and suggests dropping START from that upstream test's list.

## Consequences

- START does nothing while the picker is open, as in v1.7.0, until upstream ships the change.
- A carried version was built and tested on 2026-10-18 (two tests, both red without the token) and
  dropped before merge; the PR text describes it.
