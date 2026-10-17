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
   **Heavy conflicts** (a release that rewrites a subsystem, as v1.7.0 did with carts and menus):
   tag the old tip, reset `nes-snes` to the new base and `git cherry-pick` the old commits one
   by one, skipping the ones the release makes redundant. Resolve each by intent (its issue file
   and ADRs), run `cargo check --workspace --all-targets` after every pick, and fold fixes into
   the patch that owns the file with `git commit --fixup` and `git rebase --autosquash` (works
   without `-i` on git 2.44 and later). Write an ADR for every dropped or reshaped patch.
3. **Full suite.** `task check` must be green: upstream plus ours under
   `SLOT_REQUIRE_CORES=1`, `check-upstream-tests.sh`, fmt, both clippy passes.
   Also `task patches:check`.
   **Touch points:** run `task diffsurface`. It rewrites `docs/UPSTREAM-TOUCHPOINTS.md` for the new
   upstream and keeps each reason whose hunk still exists. Review every row against the new
   upstream code (did upstream change the code around it? is the reason still true?), give new
   rows a reason, delete nothing by hand, and commit the map. `task check` fails until it is
   current and complete.
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
| 2026-10-15 | v1.6.0 | v1.7.0 | one session, device steps pending (no tag yet) | cart.rs, app.rs, quick_menu.rs, shelf.rs, board.rs, silhouette.rs, art.rs, lib.rs (slot-ui), slot_state.rs, durability.rs, platform_policy.rs, pipeline.rs, emu.rs, frontend.rs, video_mode.rs, gesture.rs, root.rs, alsa.rs, render_shelves.rs, retro_pipeline.rs, retro_cart.rs |

## Lessons

- v1.7.0 (ADR 0038): 3 patches dropped because upstream now does the job (shelf memory, lazy
  shells, released-device pacing). Check the release notes against every patch before resolving
  a single conflict.
- New upstream `match` over `Platform` only shows up as a compile error; new `_ =>` wildcards
  and `!= Platform::Gba` comparisons do not, so grep for them after the platform patches.
- Our own tests call upstream APIs (`begin_frame(Layout)`, `apply_core_options(.., platform, ..)`,
  `draw_row(canvas, ..)`); fix them in the patch that adds the test.
- Run the bare upstream suite once first. v1.7.0 fails two frame-hash tests in
  `slot-gfx/tests/layout.rs` on the M5 Max with no patch applied (ADR 0045).
- `task diffsurface` keys reasons by file, context, first upstream line and a hash of the hunk's
  changed lines. After a rebase moves the lines, a reason follows its hunk by that hash when the
  hunk did not change, or by one offset shared by at least two hunks of its context; anything else
  comes back as `TODO: explain (ambiguous, one of: ...)`. Pick the right reason for each such row,
  and still reread every row of a file whose hunk count changed.
- New upstream tests can pin our behaviour: `runahead.rs` compares the sound in the ring of two
  runs and caught that the audio prefill depended on when the worker first saw Normal.
- The harness script drives upstream's UI, so a release that moves menus breaks it in both
  trees. v1.7.0 needed three `frame_dump.rs` changes: the quick menu now opens on General and
  Screen lists the platforms, a MENU tap opens the in-game menu (the emulator is held, so it is
  not "running"), and the worker locks later after an insert (the composite rig, which cannot
  see the lock, retries its first tick until it lands).
