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
   tag `<SLOT_PIN tag>-ns.1` (`vNEW-ns.1` on an upstream release; `main-<short sha>-ns.1` when the
   base is an untagged upstream commit, ADR 0083), add a row to the log below. `release.yml` takes
   both forms and refuses a tag that is not SLOT_PIN's tag plus `VERSION`.

## Log

One row per rebase. Time taken is wall clock from step 1 to the tag.

| Date | From | To | Time taken | Conflicting files |
|---|---|---|---|---|
| 2026-10-15 | v1.6.0 | v1.7.0 | one session, device steps pending (no tag yet) | cart.rs, app.rs, quick_menu.rs, shelf.rs, board.rs, silhouette.rs, art.rs, lib.rs (slot-ui), slot_state.rs, durability.rs, platform_policy.rs, pipeline.rs, emu.rs, frontend.rs, video_mode.rs, gesture.rs, root.rs, alsa.rs, render_shelves.rs, retro_pipeline.rs, retro_cart.rs |
| 2026-10-18 | v1.7.0 | main 1b20432 (no 1.8.0 tag yet) | one session, device steps pending (no tag) | libretro.rs, emu.rs, lib.rs (slot), gesture.rs, gesture/ps1.rs, snes_select.rs, frontend.rs, quick_menu.rs (slot-ui src and tests), app.rs, pipeline.rs, retro_quick.rs, sega_quick_shader.rs, session.rs, mask.rs, lib.rs (slot-ui), device.rs, input/mod.rs |
| 2026-10-21 | main 1b20432 | v1.8.0 | one session, device steps pending | bindings.rs, gesture.rs, input/mod.rs, session.rs, quick_menu.rs (slot-ui src and tests), toast.rs, app.rs, frontend.rs, lib.rs (slot-retro, slot-store, slot-ui), device_app.rs, launch_frontend.sh, snes_select.rs, retro_pipeline.rs |
| 2026-10-25 | v1.8.0 | v1.9.0 (v1.8.1 on the way) | one session, device steps pending (no tag) | app.rs, root.rs, quick_menu.rs (slot-ui src and tests), lib.rs (slot, slot-store), alsa.rs, libretro.rs, repair.sh, console rows in app.rs |
| 2026-11-06 | v1.9.0 | v1.14.0 (v1.10 to v1.14, one jump) | one long session, device steps pending (no tag yet) | 39 of 156 patches conflict: platform-nes and each platform patch (Platform::Gbav and Core::Gambatte arms), canvas, core-picker-pairs, cart-art, shaders, crop-overscan, lynx-screen, label-top and others; app.rs, video_mode.rs, quick_menu.rs, core.rs, root.rs, cart.rs, lib.rs files |
| 2026-11-10 | v1.14.0 | v1.15.2 (v1.15.0 to v1.15.2, one jump) | one long session, device steps pending (no tag yet) | cherry-picked 163 of 164 patches (the old rustfmt patch is dropped); conflicts in core.rs, platform.rs, platform_policy.rs, bindings.rs, cart.rs, root.rs, app.rs (62 hunks over the series), emu.rs, frontend.rs, quick_menu.rs, input/device.rs, audio/alsa.rs, server/games.rs |

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
- main 1b20432 (ADR 0083): upstream's remapping builds the game mask only from its 10 `GameButton`s,
  so buttons our systems need beyond them (X, Y, L2, R2) went dead without a compile error. After a
  release that touches input, run every system's input tests before resolving the next conflict.
- v1.8.0 (ADR 0106): new upstream `GameButton`s (Turbo A and B) set `ButtonMask::X` and `Y`, which
  our X/Y pass-through systems read as the console's X and Y, so check every mask path after a
  release that adds game buttons. Per-system chords now go through the control table as entries
  (`snes_input::keep_applicable`); a release that reshapes `Gestures::down` needs no chord port.
- Upstream now returns `Vec<QuickRow>` from `hidden_rows` and `in_game_hidden`; our tests call
  `position(&...)` and `shown(&...)`, and our hidden-row helpers return the rows to add, not a list.
- main 1b20432: the harness drives ticks far faster than real time, and upstream's sinc resampler
  panics when the measured tick rate makes the sound ratio tiny; `frame_dump.rs` spaces ticks 2 ms
  apart. The core now opens on its own thread, joined by an update, so any harness wait for a
  loading core must keep updating.
- v1.9.0 (ADR 0109): a new upstream shortcut can take the chord one of our rows had, and upstream tests that
  pin a default fail in our tree with no compile error (`screenshot_defaults_to_select_x`). After a release that adds a
  shortcut, list every default chord against ours. A clean merge can also leave array lengths wrong
  (`Shortcut::ALL`, `QuickRow::ALL`, `DIRS`): run `cargo check --all-targets` before the first test run.
- v1.9.0: our own tests that press a chord on a GBA cart and expect X as Turbo A in the window (and
  `select_x_gba.rs`, which says "as upstream") must be re-derived from the unpatched tree, not edited by hand.
- v1.9.0: upstream reordered `Platform::ALL` (GBC before GB); our `Platform::SHELVES` follows it.
- When a release lands a feature we already carry in another shape (crash guard, quiet audio start),
  keep upstream's, shrink ours to the part it lacks, and add the ADR 0109 style test table.
- v1.14.0: five releases in one jump is workable (39 of 156 patches conflict), but do the real work in
  `work/slot`, one cherry-pick per patch, and never let a word level merge helper join tokens without
  a compile or `git grep` for glued names after it (ADR 0110 lists the ones it left, patch 0157 repairs them).
  Upstream test files may not be edited beyond a named exception in `check-upstream-tests.sh`: add the
  exception in the same pull request. `step_emulator` returned true for a frame in 1.9 and returns
  late in 1.14. Upstream's own timing tests flake on a loaded macOS host: `scripts/run-tests.sh` has the
  both trees, serial and runner sensitive lists for them.
- v1.15.2 (ADR 0112): a structural merge helper (by item, `fn` level) plus a splice for "upstream only inserted arms" resolved
  most of 62 `app.rs` hunks, but a function that upstream moved took our edits to its old body with it: diff the lines our series added against the new
  tree before testing. Upstream's tests changed with the code (`write_selected_core` takes the platform, `foot_y` takes the canvas), and
  upstream 1.15.2's own `durability.rs` does not compile. After the host cores rebuild, a dylib can fail macOS's signature check (SIGKILL
  "Code Signature Invalid"): copy it to a new file and `codesign --force -s -` it.
