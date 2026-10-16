# 0047. Upstream-first fixes

- Status: Accepted
- Date: 2026-10-15
- Deciders: maintainer (Felipe Paiva)
- Related: CONTRIBUTING.md section 3, [REBASE.md](../REBASE.md), [ADR 0049](0049-per-shelf-cart-memory.md)

## Context

Three patches were dropped in v1.7.0 because upstream shipped the same job (ADRs 0039 to 0041).
Some of our fixes are not about NES or SNES at all: they fix or extend slot itself, and every
rebase pays for them again until upstream has them.

## Decision

If we find a problem and the right fix belongs in upstream BrandonKowalski/slot, we also open a
PR there. We carry our patch only until upstream ships it, then drop it on the next rebase.

The upstream PR holds the same change without any NES or SNES code, in slot's own style, with its
own tests and upstream's CI commands green. Our patch keeps the same behaviour and the same
on-disk format, so dropping it changes nothing for a player. The patch's ADR and its touch-point
rows say "drop when the upstream PR lands".

## Consequences

- Each such patch has a twin branch in `~/contrib/slot` and a row in the workspace's open
  contributions list.
- On each rebase, check the release notes for every upstream-first patch before resolving a
  conflict, as REBASE.md already asks.
- If upstream declines or reshapes the PR, the patch stays and its ADR records why.
