# 0079. Confirm favourite removal with a second Y: upstream only

- Status: Accepted (not carried)
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0047](0047-upstream-first-fixes.md), [ADR 0074](0074-switcher-up-down.md) (the same rule for the delete question), [fork review](../research/fork-review-2026-10-18.md), jgraving/slot [e2dc0cb](https://github.com/jgraving/slot/commit/e2dc0cb), upstream PR text in [docs/contributions/upstream-favourite-confirm-pr.md](../contributions/upstream-favourite-confirm-pr.md)

## Context

jgraving/slot e2dc0cb (GPL-3.0) makes Y on a starred cart show "Y Again to remove" for 3 s, and
only a distinct second Y (after a key-up) removes it. Upstream `crates/slot/tests/favorites.rs`
presses Y once and expects the cart gone in
`unstarring_on_the_favorites_shelf_takes_the_cart_off_it` and
`unstarring_the_last_favorite_leaves_the_empty_shelf`; the fork edits both.

## Decision

Not carried. Changing those two tests is a behaviour change to an upstream-tested flow, which
CONTRIBUTING section 1 sends to the maintainer, and the maintainer's rule from ADR 0074 applies:
it goes upstream only. The PR text is prepared, without the departure animation.

## Consequences

- One Y still removes a favourite, as in v1.7.0, until upstream ships the confirm.
- The upstream PR needs upstream main's `assets/buttonlegend_round_y.png` (not in v1.7.0).
