---
title: "Add rebase.sh, docs/REBASE.md and task diffsurface"
phase: 5
area: infra
type: chore
size: M
depends_on: [02-patch-pipeline, 03-task-check-and-upstream-guard]
---

## Why
Each new slot release should be rebased in one session with conflicts only in `app.rs`/`frontend.rs`, and the `app.rs` diff must stay small enough to keep that true (docs/PLAN.md Approach, Phase 5 deliverables, Outcome verification mechanisms).

## Scope
- [ ] `scripts/rebase.sh NEW_TAG`: fetch the new tarball, `git rebase --onto <new-tag>` in `work/slot`, re-export patches, `task check`, update `SLOT_PIN`. `--dry-run` reports whether all patches apply.
- [ ] `docs/REBASE.md`: re-apply, full suite, harness against the new upstream, device smoke, bump the pin, tag `vNEW-ns.1`; plus a log table (one row per rebase, time taken, conflicting files).
- [ ] `task diffsurface`: per-file changed lines over upstream files. Target: `app.rs` at 25 lines or fewer, pair loop included.

## Tests
| ID | File | Asserts |
|---|---|---|
| T42 | `scripts/rebase.sh --dry-run main` | Against slot main: "all patches apply", or the first failing patch named with a non-zero exit |

No upstream test file is touched.

## Edge cases
| Case | Expected handling |
|---|---|
| (none specific) | Patch-apply failure behaviour is owned by 02-patch-pipeline; rebase.sh relies on it |

## Acceptance
- [ ] `rebase.sh --dry-run main` runs and reports correctly.
- [ ] `task diffsurface` prints per-file counts; `app.rs` at 25 lines or fewer.
- [ ] `docs/REBASE.md` has the procedure and an empty log table.

## Device check (RG34XXSP)
None, tooling only. Device smoke after a real rebase is a step in `docs/REBASE.md`.

## Review notes
- Rebase must never hand-edit `.patch` files; it always re-exports from `work/slot`.
- If `app.rs` exceeds 25 lines, move policy into `platform_policy.rs`/`core_policy.rs` rather than raising the target.

## References
- docs/PLAN.md: Approach (Patch set rendered from a working branch), Phase 5 deliverables (rebase, diffsurface), Outcome verification mechanisms
