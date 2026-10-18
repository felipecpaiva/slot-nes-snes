# 0083. Rebase the patch set onto slot main 1b20432 (the coming 1.8.0)

- Status: Accepted
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [REBASE.md](../REBASE.md), [ADR 0038](0038-rebase-to-slot-v1-7-0.md) (the v1.7.0 port),
  [ADR 0047](0047-upstream-first-fixes.md), [ADR 0070](0070-backport-upstream-settings-scroll.md),
  [ADR 0075](0075-carry-upstream-backlight-floor.md), [fork review](../research/fork-review-2026-10-18.md), `SLOT_PIN`

## Context

Upstream has no 1.8.0 tag yet (latest tag v1.7.0 on 2026-10-18). Main at 1b20432 (tarball sha256
381ca910...66d5) is 24 commits past v1.7.0 and changes 110 files. The commits that touch our patches:

- e1bfb2b and 2c82294: global button remapping (`slot-store/src/bindings.rs`, `input/bind.rs`),
  shortcuts and shelf keys as a chord table, `Pad::mask` built only from the 10 `GameButton`s, and the
  settings pages that scroll (`QUICK_VISIBLE`, `scrolls()`). 2c82294 adds the lid power-off timer
  (`lid_off_min`) and a carousel footer under the quick menu.
- bfb8bb2: the left stick steers the D-pad on Anbernics that have one ("Left Stick as D-Pad", on by default).
- a1c3314: the core opens on a `slot-open` thread off the frame loop.
- b0fe199: run-ahead removed; mGBA gets `flash-bank-survives-mask.patch`.
- 5dc5b83: game audio resampled to 48 kHz through a windowed sinc (was linear to 32768).
- 3b6349c: the backlight floor we carried (ADR 0075).
- 656ce7e: the state size is asked once per game (`serialize_at`, `state_size`).
- ad5ce8a: `card/System/lid.sh`, a watchdog that powers off a shut device after `lid_off_min` plus 60 s.

`MGBA_COMMIT` and `GPSP_COMMIT` did not move, so the `gpsp_*` pins stay; the mGBA build stamp now
lists the new patch, so both mGBA builds are rebuilt.

`scripts/rebase.sh` refuses a branch for a real rebase, so the pin was set by hand: `tag=main-1b20432`
(it names the dist, and must not claim v1.8.0), `commit` and `tarball_sha256` as above.

## Decision

Re-apply the 52 patches one by one onto main 1b20432 by intent, as the v1.7.0 port did. One patch is
dropped because upstream ships it, one shrinks to a token, the input patches are reshaped onto the new
bindings, and the rest port with small conflict fixes. The set is now 51 patches; 0001 to 0046 keep
their numbers, old 0048 to 0052 become 0047 to 0051.

| Old | New | Result |
|---|---|---|
| 0001 step0-exhaustive-matches | 0001 | changed: two new upstream sites made exhaustive. `in_game_hidden` hides the L and R rows with `owns_shoulders()` instead of `!= Platform::Gba`; `blank_panel`'s `_ =>` gets explicit arms |
| 0002, 0005, 0024 to 0026, 0034 (platform-*) | same | changed: each adds its token to `GameButton::of` (the full list where the game owns the shoulders, `[..8]` where slot does, the same polarity as `owns_shoulders`) and to `blank_panel` |
| 0003 core-fceumm | 0003 | ported as is |
| 0004 canvas | 0004 | ported: the `ExtraGuard` bind moves into upstream's new `serialize_at` |
| 0006 libretro-env | 0006 | ported: the av change rebuild sits before upstream's single `take_audio`; `av_rate` is unchanged (it feeds `Resampler::new(src, dst)`, whose signature the sinc kept) |
| 0007 input | 0007 | reshaped, see "Input on upstream's bindings" |
| 0008 to 0010, 0012 to 0015, 0018 to 0021, 0023, 0028, 0029, 0031, 0035, 0036, 0039, 0041, 0044 to 0046 | same | ported as is or with a trivial context fix |
| 0011 parity-proofs | 0011 | ported: its walk test skips upstream's Left Stick row when the device has no stick |
| 0016 quick-menu-retro-shaders | 0016 | changed: `retro_quick::hidden_in_game` returns the rows to add to upstream's new `Vec` (Color Correction, Palette, and Bezel when unframed) instead of a whole static list |
| 0017 retro-shaders | 0017 | ported: the retro program draws the source rect upstream crops for the footer |
| 0022 screen-platform-list | 0022 | changed: `hidden_on_shelf` returns a `Vec`; named site (h) moves, see below |
| 0027 sega-shaders | 0027 | changed: `hidden_on_shelf` keeps only the system rows, so its 64-entry `OnceLock` table is gone (upstream builds the wallpaper and bezel rows itself) |
| 0030 need-fullpath | 0030 | ported next to upstream's `state_size = None` |
| 0032 system-picture, 0033 crop-overscan | same | ported: the L1 stretch keeps upstream's `!bound_to_game` guard |
| 0037 ps1-discs | 0037 | changed: `offer_remembered_disc` runs on upstream's `slot-open` thread after `open_core`; the disc trailer is added in `serialize_at`, so the cached-size path carries it too; SELECT+L2 is now "the Palette Back shortcut swaps discs on PS1" |
| 0038 ps1-input | 0038 | reshaped, see "Input on upstream's bindings" |
| 0040 ps1-analog | 0040 | changed: the sticks are published beside upstream's left-stick steering in `read_node`; the `menu_dpad_display` argument upstream removed is gone |
| 0042 screen-scroll | 0042 | shrunk to one token, `&QuickRow::SCREEN` in upstream's `scrolls()` (ADR 0070) |
| 0043 pal-pacing | 0043 | ported: the run-ahead lines it sat between are gone; the period, frames-owed carry and audio math are unchanged and rate-independent (`device_hz` comes from the ring, 48000 now) |
| 0047 backlight-floor | none | dropped, upstream ships 3b6349c (ADR 0075) |
| 0048 sms-region to 0052 silent-start-hud | 0047 to 0051 | ported as is |

### Input on upstream's bindings

Upstream's `Pad::mask` presses only the console buttons a `GameButton` (Up to R, 10 of them) is
bound to. X, Y, L2 and R2 are not game buttons, so on main they never reach any core: SNES X and Y,
the Mega Drive and PlayStation face buttons, and PlayStation L2 and R2 would all go dead with no error.
`GameButton::ALL`, `Controls.game` and `QuickRow::CONTROLS` are all length 10, and upstream tests pin
them, so we do not make those buttons remappable.

- A new file `input/raw_buttons.rs` adds `Pad::mask_for(controls, platform)`: upstream's mask, plus
  X and Y on systems that `passes_xy_through()` and L2 and R2 on systems that do not `owns_triggers()`,
  each only while held and only when that button is not plainly bound to a game button (upstream's own
  `bound_to_game` rule, so one press never reaches the core twice). `mask.rs` gains a three-line
  `holds()`; `session.rs` calls `mask_for` with the playing platform.
- SELECT+X flips the picture on SNES, Mega Drive and PlayStation only when no user shortcut is bound
  to SELECT+X (the user's binding wins).
- PlayStation: `trigger_to_game` keeps plain L2 and R2 out of the shortcut table (upstream binds Rewind
  and Fast Forward there by default), so they reach the game; SELECT+R2 still toggles fast-forward,
  now held through upstream's `held` release list.
- Upstream behaviour our GBA tests now pin: an unbound X no longer reaches a GBA or NES core (turbo A
  on X and turbo B on Y are gone on main unless a game button is bound to X or Y). `select_x_gba.rs`,
  `snes_select.rs` and `snes_then_gba.rs` expect the new upstream masks, checked by running the same
  script on the unpatched tree. New test `snes_raw_buttons.rs` covers `mask_for`.

### Named upstream test sites

- (h) moves: upstream appended its Controls rows after `QuickRow::ScreenGb` in the "rows that open
  pages" list of `slot-ui/tests/quick_menu.rs`, so the last entry is now `QuickRow::ControlsInGame`
  and our tokens go on that line (still "the last entry"). Appending the tokens to the `ScreenGb` line
  would need our rows in the middle of `QuickRow::ALL`, which the append-only rule forbids.
- (i) retired with the backlight-floor patch.
- (a), (b), (d), (e), (f) and (g) hold unchanged.

### Harness, tests and scripts

- `harness/frame_dump.rs` follows main in both trees: `OUTPUT_HZ` for the stub sink (5dc5b83), no
  `power_menu` (0ba5370), and the wait for a loading core polls with a zero-length update and no
  input, since a1c3314 joins the `slot-open` thread from an update.
- It also spaces emulator ticks at least 2 ms apart (`MIN_TICK`). The sound ratio follows the
  measured tick rate (as in v1.7.0); the harness ticks every 0.44 ms, so the ratio falls to 0.026.
  v1.7.0's linear resampler took that, but upstream's new sinc `Resampler::process` (5dc5b83) then
  reads past its history (`drain(..drop * 2)` with `drop` one to five frames over) and panics the
  emulator thread, in the unpatched tree too, at H1's first state save. On the device ticks follow
  the panel, so this needs a driver about 35 times faster than real time; it is still an
  upstream-first candidate (clamp `drop` to the frames held).
- `scripts/run-tests.sh` drops `slot:runahead` from `ci_timing` (the file is gone) and counts a
  skip that names the Games folder as a ROM skip: upstream's new `core.rs` test says "no vendored
  mGBA core or no Super Mario Advance 4 under sdcard/Games".
- `scripts/check-upstream-tests.sh`: site (h) anchored on `ControlsInGame`, site (i) removed.
- After the first CI run (39151890455): `scripts/zip-check.sh` expects upstream's new release files,
  `System/lid.sh`, `System/repair.sh`, `System/fsck.exfat` (aarch64), `licenses/exfatprogs-GPL-2.0.txt`
  and `licenses/exfatprogs-<EXFATPROGS_VERSION>.tar.gz` (checked against upstream's
  `EXFATPROGS_SHA256`); LICENSING and SUPPLY-CHAIN list exfatprogs.
- Upstream's `render_in_game_menu.rs` failed both tests on the macOS runner (one extra menu step to
  `GameL`, the footer brighter than the game) and passes here in both trees, with its mock core, also
  under a 14-way CPU load. It joins `layout.rs` in `run-tests.sh`'s both-trees list (ADR 0045): it
  gates on no failure upstream does not also have, and CI prints both trees' counts.

## Consequences

- Left stick on PlayStation: with "Left Stick as D-Pad" on (upstream's default) and a device in
  upstream's stick list (the RG34XXSP is, 1b20432), the left stick both steers the D-pad and moves the
  analog stick in a PS1 game. Decided by the maintainer on 2026-10-18: keep both, as upstream's
  setting and our analog stick each do on their own; a user who wants analog only turns "Left Stick
  as D-Pad" off. No PS1 special case.
- Upstream-first candidates: the resampler `drop` clamp above; making X, Y, L2 and R2 remappable (a `GameButton` list per system) would
  replace `raw_buttons.rs`; the lost GBA turbo on X and Y may be an upstream regression worth an issue.
- Lid: our doze rest (0050) keeps running the timers, so upstream's `lid_off_min` timer powers off on
  time while resting; `lid.sh` is a second line 60 s later.
- The PS1 state size is now cached once per game like every core's (656ce7e); pcsx_rearmed's
  `retro_serialize_size` is the constant 0x440000 at c8816799, so a disc swap does not change it.
- Our scroll render tests stop counting at y 424, the top edge of upstream's new carousel footer.
- Checked on the M5 Max: harness control and compare 0 diffs, inject ok; `bench:compare` 99.2 to
  100.1% of upstream (mGBA and gpSP, GBA, GB, GBC); `audio_start`, `emu_av_change`, `pal_pacing` and
  `pal_pacing_clock` also pass with the stub sink opened at 48000 instead of their 32768.
- Our `nes_window.rs` picture-size test failed twice under parallel load (picture 720 wide, the whole
  window) and passed 6 of 6 on a quiet machine; watch it.
- Needs the device: everything in the device-check list of this rebase (remapping, left stick,
  lid timer with doze rest, 48 kHz audio including PAL, PS1 disc load, Screen scroll).
