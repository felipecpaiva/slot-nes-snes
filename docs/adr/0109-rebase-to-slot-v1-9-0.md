# 0109. Rebase the patch set onto slot v1.9.0, give SELECT+X to upstream's Screenshot and let upstream's loading mark carry the crash guard

- Status: Accepted. Amends [0084](0084-keep-a-crashed-start-on-the-shelf.md) (the guard's detection is upstream's now) and [0106](0106-rebase-to-slot-v1-8-0.md) (Picture Next moves to SELECT+Y)
- Date: 2026-10-25
- Deciders: maintainer (Felipe Paiva)
- Related: [REBASE.md](../REBASE.md), [ADR 0030](0030-keep-alsa-open-while-fed.md), [ADR 0047](0047-upstream-first-fixes.md), [ADR 0072](0072-write-sav-when-the-core-gives-no-state.md), [ADR 0098](0098-expansion-card.md), [ADR 0108](0108-console-buttons-on-the-in-game-controls-page.md), patches 0155 and 0156, `SLOT_PIN`

## Context

Upstream tagged v1.8.1 on 2026-10-22 and v1.9.0 on 2026-10-23 (commit 20703ed, tarball sha256
bf179847...6e0a). Together they are 29 commits and 175 files past our v1.8.0 pin (0ceac65). `MGBA_COMMIT` and
`GPSP_COMMIT` did not move, so the `gpsp_*` pins stay; mGBA gains `543a19758-mbc2-sram-bank.patch`
(MBC2 saves), which applies before our own mGBA patches in glob order and leaves them untouched. What
mattered to us:

| Upstream | What it touches in ours |
|---|---|
| 412f694 Load State on Insert, Save State on Eject | `insert(clean)` now takes `!auto_load`; our boot and our PS1 disc resume go through it; two renamed rows in tests |
| 07183c8 audio device closed at boot (#135) | our audio-reopen patch (0018) did the same hunk in `play()`; its `Hold` started claimed |
| 91499a9 Fast Forward Off | `FF_SPEEDS` starts at 0; our PS1 SELECT+R2 latch starts fast forward too |
| 9e545a3 letter jump outruns the scroll | our fast shelf scroll (0054) covers Left/Right holds, this covers Up/Down; both stay |
| 0d36d9d state size asked again once the save chip is known | `LibretroCore::state_size` is a pair now; our disc trailer sits after it |
| 4e74bdd refuse an empty state | one guard in `unserialize`; our trailer strip runs after it |
| 1edb9ed, f66497e sync after each save, game save every minute, resume every five | `autosave()` split in two; our save-ram-alone path sat in the branch that is now every five minutes |
| 55cf31b start on the shelf when a cart took slot down | overlaps our crash guard (0052) |
| 25315de stop waiting on a core that does not answer | `Snapshot::state` and `save_ram` give up after 2 s, an eject after 10 s (then `_exit(75)` on the device) |
| 79bc012 label caching stalls | `rebuild.stalled()` in the frontend, after 20 s without progress |
| 47bd0e6 repair steps time-limited | `repair.sh` `bounded`; our submount unmount in 0098 now runs through it |
| 64c4147 Undo Save / Undo Load | three new rows at the end of `QuickRow::ALL` |
| 22f1ec2 GBA bezels from the card on 4:3 panels | `bezel_files` for GBA depends on the panel |
| Screenshots (76237f2, `Shortcut::Screenshot`, default SELECT+X) | takes the chord our Picture Next had; upstream's `screenshot_defaults_to_select_x` pins that no other shortcut starts on it |
| `Platform::ALL` is `[Gba, Gbc, Gb]` now | upstream's `app.rs` tests walk R1 through the shelves in that order |

The bare v1.9.0 suite and our series share the same results on the M5 Max except where noted below.

## Decision

Re-apply all 154 patches by intent onto v1.9.0 (conflict by conflict, `git rebase --onto` with
hand resolutions, then one adaptation patch and one test patch; numbers 0001 to 0154 are unchanged,
0155 and 0156 are new).

### Behaviour that changes

1. **Picture Next moves from SELECT+X to SELECT+Y.** Upstream's Screenshot owns SELECT+X on every
   system and a unit test (`screenshot_defaults_to_select_x`) fails if any other shortcut starts on
   it, so our row cannot keep that default. All SELECT chords with a face, shoulder or d-pad button
   are taken upstream; SELECT+Y is Color Correction, which only the Game Boy family uses. On the
   systems that flip the picture `keep_applicable` drops the colour entry, so the gesture table
   holds one entry on the chord, and `Table::clash` does not flag the pair (they never play
   together, and a fresh card must show no triangle). SELECT+X on the Game Boy family and NES is the
   screenshot, as upstream ships it, and no longer reaches the game as Turbo A in the chord window.
2. **A game that took slot down while it loaded: upstream's guard, our banner.** Upstream marks the
   cart in `$SLOT_RUN/slot-loading` when it goes in, clears it after 10 s of play, on the shelf or on
   a clean stop, and on the next boot starts on the shelf, unseats the cart and moves its resume
   state aside (`resume-refused-<stamp>.state`). Our 0052 wrote `Config/starting.txt` on the card,
   kept the cart seated on the shelf and left the resume state. The card file is gone (the run dir is
   tmpfs: a power cycle retries the load, which upstream chose on purpose), the detection is upstream's,
   and our patch shrinks to what the player sees: the crashed cart is selected on the shelf and the
   "Last start failed" banner shows. The resume state is moved aside, no longer kept: the state may
   be what crashed the core (1.9.0 itself fixes an empty one), and the next start is clean.
3. **The game save is written every minute, the resume state every five.** Ours wrote both every
   minute. Our cores with no state (PICO-8) still get their save written at the five
   minute tick, at eject and at doze (0044 stays; upstream's eject drops the save when the core gives
   no state, issue draft [save-ram-without-state-issue.md](../upstream/save-ram-without-state-issue.md)).
4. **The classic shelf order is GBA, GBC, GB, then ours**, following upstream's `Platform::ALL`.
5. **The audio device is released at boot** (BaseOS startup sound). Ours started claimed for 3 s; it
   starts released now, like `Silence::quiet`. A cart starting to load, or the first feed, claims it,
   so a game that feeds silence still keeps the device (ADR 0030).

### Dropped as covered upstream, and the test that keeps it covered

| Our piece | Behaviour it guaranteed | Upstream's version | Test in our files (fails when the behaviour breaks) |
|---|---|---|---|
| 0052 crash-guard, the mark (`Config/starting.txt`, `mark_start`, `settle_start`) | a crashed load never loops the boot; a single cart still shows the shelf | `loading_mark.rs`, `App::start_after_a_crash` | `crash_guard.rs`: `a_start_that_never_got_through_leaves_the_cart_on_the_shelf`, `a_single_cart_that_never_got_through_still_shows_the_shelf`, `a_cart_kept_on_the_shelf_stays_there_until_a_start_gets_through`, `ten_seconds_of_play_lets_the_next_boot_resume_without_a_banner`, `a_clean_stop_lets_the_next_boot_resume` |
| 0052, the banner and the selected cart | the shelf shows why it came up and which cart it was | kept, hooked into `start_after_a_crash` | `crash_guard.rs` asserts `Toast::StartFailed` and `selected_stem()`; `the_start_failed_banner_uploads_in_its_own_place` |
| 0052, resume state kept | the state is not lost | moved aside instead (behaviour change 2) | `a_start_that_never_got_through_moves_its_resume_state_aside` pins the new rule: none left, one `resume-refused-*` kept |
| 0018 audio-reopen, the claimed start | the speaker is free at boot | `Silence::quiet`, closed `play()` | `audio::hold::tests::a_quiet_boot_holds_no_device_until_something_is_fed`, `a_wake_after_a_quiet_boot_claims_the_device` |
| 0044 flush-sav-without-state, the every-minute write (upstream does it now) | the game save reaches the card within a minute; a core with no state keeps its save | `autosave()` writes `trusted_sav` every minute | `save_cadence.rs`: `the_game_save_reaches_the_card_within_a_minute_and_the_resume_waits_for_five`, `a_core_with_no_state_still_gets_its_save_written_every_minute_and_at_five` |
| 0098 expansion-card, an unbounded unmount | the repair unmounts the bind mounts before fsck | the same unmount through `bounded`; a hung step is given up on | `card/test-expansion.sh`: a hung bind unmount is given up on, the next folder and the card are still tried, the device reboots with `-n` |
| Fast Forward chords (the plain hold and the PS1 SELECT+R2 latch, 0038) | holding fast forward does what the row says | `may_fast_forward` refuses with Off | `ff_off.rs`: `with_fast_forward_off_the_latch_and_the_plain_hold_both_start_nothing`, `a_fast_forward_start_runs_at_a_set_speed` |
| Picture and GBA input on SELECT+X | GBA, GB and GBC send what upstream sends | upstream's Screenshot on SELECT+X | `select_x_gba.rs` re-derived from the unpatched v1.9.0 tree (masks 0 in the chord window, `auto_load` in the state); `snes_then_gba.rs`, `sega_then_gba.rs` assert SELECT+X never reaches a GBA game |

Mutation checks run for this ADR: the crash guard (`LoadingMark::left` returning `None` fails 5 of 7;
removing the `show_start_failed` call fails 2), the audio hold (`Silence::new` back in `Hold::new`
fails the quiet-boot test), the resume-tick save (`save_ram_alone` replaced by `(None, None)` fails
`a_core_with_no_state...`).

### Kept, not redundant

- Fast shelf scroll (0054): upstream's letter-jump clamp covers Up and Down holds, ours Left and Right on
  60 or more carts; both live in `Shelf` without touching each other.
- Resume, crash guard and PS1 multi-disc: `insert(!auto_load)` is upstream's, our disc state is read by the
  core after it, so Load State on Insert Off starts a disc game clean like any other.
- mGBA patches (link mode, gb audio, flash bank): they apply after the MBC2 patch unchanged.

### Named upstream test sites

- (h) moves: v1.9.0 appended `QuickRow::UndoSave` and `QuickRow::UndoLoad` after `ScreenGeneral`, so our
  tokens go on the `QuickRow::UndoLoad` line. `check-upstream-tests.sh` and CONTRIBUTING follow.
- (a) to (g), (j), (k) hold; `durability.rs` gained `auto_load` lines upstream (sites (d) and (f) still
  match), and `gpsp.rs` now ticks 300 s for a resume (site (e) unaffected).
- Upstream's `render_screenshot.rs` and `render_gallery_stress.rs` join the pinned in-process lists in
  upstream's `taskfile.yml`; ours does not list them.

## Consequences

- Behaviour the player sees: Picture Next on SELECT+Y, Screenshot on SELECT+X everywhere; a banner on a
  crashed start with its resume state moved aside; the game save on the card within a minute; Undo Save
  and Undo Load for 30 s; Load State on Insert and Save State on Eject rows; Fast Forward Off; a closed
  audio device at boot; upstream's screenshot gallery on every system.
- A user eject during a core load longer than 10 s makes slot restart (`_exit(75)`, upstream) and the
  next boot shows "Last start failed": the mark was set at insert. Known cost of upstream's design.
- The 2 s answer limit on `state()` and `save_ram()` can skip one autosave of a very slow frame. Device
  check: PS1, PC Engine CD, Sega CD and Neo Geo CD loads and saves (`docs/DEVICE-GATE.md`).
- Rule added to CONTRIBUTING (section 3): dropping a patch because upstream covers it needs a test in
  our files, named after the patch, that fails when the behaviour breaks.
