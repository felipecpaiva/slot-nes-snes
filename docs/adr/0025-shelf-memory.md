# 0025. Remember the last shelf and each shelf's cart in Config/shelf.state

- Status: Accepted
- Date: 2026-10-13
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 45](../../.github/issues/45-shelf-memory.md), [patch 0019](../../patches/0019-shelf-memory.patch)

## Context

Users switch between five shelves and slot has no favourites or recents. After a restart slot
opened on the first non-empty shelf at index 0. A `SlotState` field would break the exhaustive
`SlotState` literal in upstream `durability.rs`, outside the named test exceptions.

## Decision

slot remembers the last shelf and the selected cart of every shelf (by stem) in
`Config/shelf.state` (`shelf=<platform>`, `shelf_<platform>=<stem>`), not in `slot.state`. It is
saved through the state writer thread once the cursor is at rest, and restored at boot unless a
seated cart resumes.

## Consequences

- `slot.state` stays byte-identical, so old and new builds read each other's cards.
- Carts are kept by stem, so adding or removing ROMs does not shift them.
- `flush` covers the new file and a failed write raises the card alarm, like `slot.state`.
- A held direction writes once when it is let go, because `persist_soon` has no time debounce.
