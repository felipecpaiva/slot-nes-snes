# 0001. Ship NES and SNES as a patch set over pinned slot releases

- Status: Accepted
- Date: 2026-10-11
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 02](../../.github/issues/02-patch-pipeline.md), [issue 31](../../.github/issues/31-rebase-and-diffsurface.md), [PLAN.md](../PLAN.md) Approach, [RESEARCH.md](../RESEARCH.md), [EVAL.md](../EVAL.md)

## Context

slot's owner declined more systems on slot#30: "slot will not be adding support for more systems."
So upstreaming is closed. slot itself pins its cores (mGBA, gpSP), applies `cores/<core>/*.patch`
in glob order and writes a `.meta` stamp. The options were a long-lived fork, a dispatcher shim
core, or the same patch approach one level up.

## Decision

NES and SNES ship as `patches/NNNN-<concern>.patch` over a pinned slot release (`SLOT_PIN`).
Code is written in `work/slot`, one commit per concern, and exported with
`scripts/export-patches.sh`. The build applies the patches in name order onto the pinned tarball.

## Consequences

- Each patch has provenance in the `.meta` stamp, like slot's own cores.
- A new slot release is a `git rebase --onto` in `work/slot`, a re-export and `task check`
  ([REBASE.md](../REBASE.md)).
- Rejected: a fork (rebase cost with no stamp or provenance, per EVAL.md) and a shim core, which
  would squeeze NES and SNES into the 240x160 GBA frame and onto the GBA shelf.
- Cost: every upstream release must re-apply the patches. The patch hygiene rules in
  CONTRIBUTING.md section 3 exist to keep that cheap.
- On each rebase: `sh scripts/rebase.sh vNEW --dry-run` first.
