# Rebasing onto a new slot release

Goal: one session per upstream release, conflicts only in `app.rs` and `frontend.rs`.
`patches/` is rendered from `work/slot`; never edit a `.patch` by hand.

## Procedure

1. **Dry run.** `sh scripts/rebase.sh vNEW --dry-run` works in a temp clone and prints
   "all patches apply" or the first failing patch and its conflicting files (exit 1).
   `main` is accepted here to see trouble coming before a release.
2. **Re-apply.** `sh scripts/rebase.sh vNEW` fetches the tarball (the new commit is checked
   against the tag, its sha256 is printed), runs `git rebase --onto` in `work/slot`,
   re-exports `patches/`, rewrites `tag`, `commit` and `tarball_sha256` in `SLOT_PIN`
   (it prints the diff) and runs `task check`. On a conflict it stops in `work/slot`:
   resolve, `git rebase --continue`, `sh scripts/export-patches.sh`, edit `SLOT_PIN`
   as printed, then `task check`.
   If `task check` fails at the end of a real rebase, `SLOT_PIN` and `patches/` are already
   updated. Inspect with `git diff SLOT_PIN patches/`; to revert, `git checkout SLOT_PIN patches/`
   (`work/slot` stays rebased; `git -C work/slot reflog` has its previous tip).
3. **Full suite.** `task check` must be green: upstream plus ours under
   `SLOT_REQUIRE_CORES=1`, `check-upstream-tests.sh`, fmt, both clippy passes.
   Also `task patches:check` and `task diffsurface` (`app.rs` at 25 or fewer).
4. **Harness against the new upstream.** `task harness:control`, then `task harness:compare`
   (0 differing frames; `task check` runs both on an idle machine). `task bench:compare`
   within 2%.
5. **Pins that follow upstream.** Compare upstream's `MGBA_COMMIT` and `GPSP_COMMIT`
   (`build/slot/taskfile.yml`) with the old ones; if they moved, update `gpsp_*` in `SLOT_PIN`
   and see `docs/SUPPLY-CHAIN.md`.
6. **Device smoke on the RG34XXSP.** `task deploy:device`, then boot a GBA, NES and SNES
   game, pick a core, fast-forward and rewind; `task readout:device` for starve lines.
   Walk `docs/DEVICE-GATE.md` for anything the rebase touched.
7. **Release.** Set `VERSION` to `ns.1`, commit `patches/`, `SLOT_PIN` and `VERSION`,
   tag `vNEW-ns.1`, add a row to the log below.

## Log

One row per rebase. Time taken is wall clock from step 1 to the tag.

| Date | From | To | Time taken | Conflicting files |
|---|---|---|---|---|
