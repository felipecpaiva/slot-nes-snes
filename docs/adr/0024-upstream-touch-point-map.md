# 0024. Track every upstream touch point instead of an app.rs line limit

- Status: Accepted. Replaces the 25-line `app.rs` target in issue 31 and PLAN.md
- Date: 2026-10-13
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 31](../../.github/issues/31-rebase-and-diffsurface.md), [UPSTREAM-TOUCHPOINTS.md](../UPSTREAM-TOUCHPOINTS.md), [REBASE.md](../REBASE.md), `scripts/diffsurface.sh`

## Context

Issue 31 set a target of 25 changed lines or fewer in `app.rs`. The maintainer: what matters is
knowing every point of contact with upstream so an update can be checked point by point, not a
number.

## Decision

No fixed line limit on `app.rs`. Every upstream touch point is listed in
`docs/UPSTREAM-TOUCHPOINTS.md` with a reason. `task check` fails on a stale or incomplete map.

## Consequences

- `task diffsurface` regenerates the map and keeps existing reasons; `task diffsurface:check`
  fails on a stale map or a row without a reason.
- Upstream edits are still kept small, with logic in new files where possible.
- On each rebase: review every row against the new upstream (REBASE.md step 3).
