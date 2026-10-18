# 0074. Move through the save state switcher with Up and Down too

- Status: Accepted. Drop when the upstream PR lands (0047)
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0047](0047-upstream-first-fixes.md), patch `patches/0046-switcher-up-down.patch`, [fork review](../research/fork-review-2026-10-18.md), suprsomething/slot.advance [2fe9876](https://github.com/suprsomething/slot.advance/commit/2fe9876), upstream PR text in [docs/contributions/upstream-switcher-delete-pr.md](../contributions/upstream-switcher-delete-pr.md)

## Context

suprsomething/slot.advance (GPL-3.0) 2fe9876 does three things in the save state switcher: Up
(newer) and Down (older) beside Left and Right, a question before Y deletes a state, and a ring of
five states instead of ten.

## Decision

We carry only Up and Down, two tokens on the switcher's arms in `App::apply`. The ring of five is
not taken: it retunes a factory default (keep options, the user's choice is the default). The
delete question is not carried: upstream `crates/slot/tests/delete.rs` presses Y once and expects
the state gone in five tests (lines 18, 34, 47, 63 and 85), so it would need a new named test site
(each single `GbaDown(Btn::Y)` becoming a Y, Y pair), which is a behaviour change CONTRIBUTING
section 1 sends to the maintainer. The maintainer decided on 2026-10-18 that the delete question
stays upstream-only: it is offered in the PR text
([docs/contributions/upstream-switcher-delete-pr.md](../contributions/upstream-switcher-delete-pr.md))
and is never carried as our patch.

## Consequences

- `crates/slot/tests/switcher_up_down.rs`: Down moves to the next older state, Up back to the
  next newer one. Red without the change. No upstream test presses Up or Down in the switcher.
- A PS1 state needs nothing special: `StateRing::remove` deletes the state file, which holds the
  `SLOTPSX1` disc trailer (ADR 0067), and its thumbnail.
- Until upstream ships it, one Y still deletes a state with no question, as in v1.7.0.
- **Drop the patch when the upstream PR lands.** The delete question arrives only with upstream.
