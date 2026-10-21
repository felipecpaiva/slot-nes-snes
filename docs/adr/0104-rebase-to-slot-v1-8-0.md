# 0104. Rebase the patch set onto slot v1.8.0 and put our chords in its control table

- Status: Accepted
- Date: 2026-10-21
- Deciders: maintainer (Felipe Paiva)
- Related: [REBASE.md](../REBASE.md), [ADR 0083](0083-rebase-to-slot-main-1b20432.md) (the 1b20432 move),
  [ADR 0047](0047-upstream-first-fixes.md), [ADR 0068](0068-ps1-input-digital-then-analog.md),
  [ADR 0084](0084-keep-a-crashed-start-on-the-shelf.md), [ADR 0098](0098-expansion-card.md),
  [ADR 0100](0100-shelf-order-option.md), `SLOT_PIN`

## Context

Upstream tagged v1.8.0 on 2026-10-21 (commit 0ceac65, tarball sha256 83094bab...f244). It is 18
commits past our pin, main 1b20432, and changes 114 files. Most of the 1.8.0 changelog (remapping,
run-ahead removed, the 48 kHz windowed-sinc resampler, Left Stick as D-Pad, the lid watcher) was
already in 1b20432 and was reconciled by ADR 0083. The 18 new commits are:

- f4b7bc3, af9ff09, 0fa8ecc: every control resolves through one table (`input/table.rs`) with
  contexts (game, shelf, menu), two-button chords (`Modifier::Button`) and clash warnings
  (`Toast::Duplicate`, "Same as ...").
- 5a0b63f: Turbo A and Turbo B become `GameButton`s 11 and 12 (default X and Y). `bit()` maps
  them to `ButtonMask::X` and `Y`, which the emulator pulses as A and B.
- 9d2bc24, ee19b7a: the layout follows the panel size (`Layout` and `Compositor::begin_frame(Layout)`
  are gone, the bezel is a sprite), and `Labels/`, `Wallpapers/`, `Bezels/` ship a `README.txt`.
- 6d8f8db, b4a54d3: Brightness and Blue Light rows (Screen > General, first on the Screen page, and
  the end of the in-game Screen page), and one live Palette row over `GbColors` (Auto plus mGBA's
  48 palettes, mGBA gains `zz-gb-auto-palette.patch`).
- c5de4cc, b25c7a2, e22101c: SD card safety. `read_sav` and `read_resume` return
  `io::Result<Option<_>>` so an unreadable card is told apart from a missing file, SIGTERM saves
  before stopping, temp files a power cut left are swept at boot, crash dumps are gone (5 logs kept),
  and `repair.sh` runs fsck up to 6 passes.
- fdfc5d1: deleting a state asks first. ea438a0: the About sticker prints `git describe`.
- 211ec4e, 8d84346, be8acb6, 0b736f1, 0ceac65: link mode switch, sticker hash, test sound
  (`SLOT_SILENT` now only silences on `1`), changelog.

`MGBA_COMMIT` and `GPSP_COMMIT` did not move, so the `gpsp_*` pins stay; the mGBA build stamp lists
the new patch, so both mGBA builds are rebuilt. The bare v1.8.0 suite passes in full on the M5 Max
(including `slot-gfx/tests/layout.rs` and `render_in_game_menu.rs`, which upstream rewrote).

## Decision

Re-apply all 130 patches (134 with the SuperGrafx) by intent onto a fresh v1.8.0 tree with `git cherry-pick`, fold fixes into
the patch that owns the line with `--fixup` and `rebase --autosquash`, and keep their numbers. No
patch is dropped whole: none of them is in 1.8.0. One policy is dropped (`turbo_on_xy`), the input
patches move onto the control table, and the rest port with context fixes.

### Ported into upstream's control table

| Ours | Before | Now |
|---|---|---|
| SELECT+X picture flip (SNES, MD, PS1, WS, Lynx, NGP, 32X, VB, arcade, PICO-8, SuperGrafx with 6 Buttons) | a special case in `Gestures::down` (`video_mode_chord`) | a new Shortcuts row, **Picture Next**, default SELECT+X (`Shortcut::PictureNext`, `QuickRow::ScPictureNext`, appended). It shows on Controls > Shortcuts, can be moved to any chord upstream allows, and takes part in the clash warnings. Its entry is dropped from the gesture table while a system without the flip plays (`snes_input::keep_applicable`, told by `App::picture_chord`, which also answers yes for a seated six-button SuperGrafx), so SELECT+X on GBA, GB, GBC and the others sends exactly what upstream sends (`select_x_gba.rs` re-derived from the unpatched tree) |
| SELECT+L2 swaps the PS1 disc and flips the FDS disk | `ps1_chord` in `Gestures::down` remapped `PalettePrev` while `disc_chord` was set | `keep_applicable` turns the Palette Back entry into `DiscNext` while PS1 or FDS plays. The swap follows Palette Back wherever the user moves it, single or chord. No row of its own: as a row it would share Palette Back's default and show a clash triangle on every fresh card, and the two never apply to the same system (no palettes on PS1 or FDS). `gesture/ps1.rs` loses the disc chord; `slot-input/tests/ps1_gesture.rs` loses its two chord tests, which move to `slot/tests/disc_chords.rs` |
| X and Y pass through as the console's X and Y (SNES, MD, PS1, WS, 32X, Atari, VB, arcade, SuperGrafx with 6 Buttons) | `raw_buttons` | kept, and on these systems `Pad::mask_with` (renamed from `mask_with_triggers`, it takes the seated X/Y flag `App::xy_to_game` instead of the platform) removes the Turbo A and Turbo B bindings before it builds the mask (`game_buttons`), so moving Turbo A to another button never sends the console's X from it, and the in-game Controls page hides the two turbo rows there (`in_game_hidden`) |

Not ported, with the reason:

- Per-system buttons beyond upstream's 12 `GameButton`s (PS1 L2/R2 and Square/Triangle, VB right pad
  modes, arcade 6-button maps, Atari switches, the sticks): they are console buttons, not shortcuts.
  Making them rows means a `GameButton` list per system; `GameButton::ALL` (12) and the
  `QuickRow::CONTROLS` labels are pinned by upstream tests (`slot-ui/tests/quick_menu.rs`). They stay
  on `raw_buttons`, `ws_input`, `vb_input` and the analog path. Upstream-first candidate below.
- PS1 SELECT+R2 fast-forward latch and plain L2/R2 to the game (`ps1_down`, `trigger_to_game`): they
  depend on the game, not on a binding. Kept in `gesture/ps1.rs`; in v1.8.0's `down` the plain
  shortcut lookup in game context gains `.filter(|_| !self.trigger_to_game(b))`, one token.

### Dropped as covered upstream

- `Platform::turbo_on_xy` (TurboGrafx-16, patch 0061): X and Y reached the core raw only so slot's
  turbo could pulse I and II. Upstream's Turbo A and Turbo B rows do this for every system that does
  not pass X and Y through, and can be remapped. The policy, its use in `raw_buttons` and its test
  lines are removed (0061, 0091, 0100, 0103, 0120, 0128, and the SuperGrafx patches 0132). NES, FDS, GG, SMS, Lynx, NGP, PICO-8 and
  TG16 gain Turbo A and B on X and Y (they had none since 1b20432).
- The SuperGrafx (merged from main as 0131 to 0134 during this rebase, ADR 0103) ports onto the
  same paths: its 2-button pad uses upstream's Turbo A and B, its 6-button pad passes X and Y
  through and gets the picture chord through `xy_to_game` and `picture_chord`.
- The "lost GBA turbo on X and Y" upstream-first candidate of ADR 0083: fixed upstream (#127).

### Context fixes worth naming

- `GameButton::of`: every `&GameButton::ALL[..8]` arm (systems where slot owns the shoulders) becomes
  `&GameButton::GAME_BOY`, which keeps the turbo rows, so `bound_to_game` still sees them.
- Our tests call `begin_frame()` (no `Layout`), compare `read_sav(..).ok().flatten()`, and wait for
  `Ok(Some(_))` from `read_resume`. The FDS save check maps the `Ok` of the new `read_sav`.
- `Toast::Retro` now starts at `Toast::all().len()`, after upstream's new `Duplicate` toasts.
- `quick_value` keeps our "only recurse when the playing row differs" guard and covers the new
  `PlayBrightness` and `PlayBlueLight` rows.
- The Screen page starts with General: `QuickRow::SCREEN` gains it first, the Release Year order
  (`ShelfOrder::screen_rows`) puts it first too, and every `QuickRow::SCREEN[n]` in our tests
  moves by one.
- `device_app.rs`: upstream's SIGTERM stop check runs before our doze-rest `continue`, so a stop
  while resting still saves.
- `launch_frontend.sh`: upstream's link-down line runs before `expansion.sh`. `repair.sh` keeps our
  submount unmount inside `unmount()`, which still runs before the first fsck pass.

### Named upstream test sites

- (g) and (h) move: upstream's Screen labels line now starts with `"General"` and its "rows that
  open pages" list now ends with `QuickRow::ScreenGeneral`. Our tokens follow `"Game Boy"` inside
  the new line and go on the `ScreenGeneral` line. `check-upstream-tests.sh` matches the new lines.
- (a), (b), (d), (e), (f), (j) and (k) hold unchanged; `durability.rs` and `gpsp.rs` changed upstream
  away from our lines.

### Release name

v1.8.0 is a tag, so the release is `v1.8.0-ns.1` (`SLOT_PIN` tag `v1.8.0` plus `VERSION` `ns.1`);
`release.yml` already takes `v*-ns.*`.

## Consequences

- Behaviour the player sees: a Picture Next row on Controls > Shortcuts; Turbo A and B on X and Y
  on the systems listed above; the turbo rows hidden in game on the X/Y systems; upstream's Screen >
  General, live Palette row (GB only), state delete question, card repair passes and SIGTERM save.
- Harness: `harness/frame_dump.rs` follows v1.8.0 in both trees: `begin_frame()` takes no layout, and
  `open_screen` steps past the new General row first. Checked on the M5 Max: harness control and
  compare 0 diffs, inject ok; `bench:compare` 99.1 to 100.3% of upstream (mGBA GBA, GB, GBC and gpSP).
  Audio: the 48 kHz path did not change since 1b20432; `audio_start`, `emu_av_change`, `pal_pacing`,
  `pal_pacing_clock` and `lynx_pacing` pass in the full suite. Upstream's `rumble.rs` failed
  once under a full parallel load and passes alone (timing, both trees).
- `scripts/check-format.sh` fails only on files we add or change: rustfmt also walks the modules a
  changed `lib.rs` declares and reaches upstream's own `sticker.rs`, which 1.8.0 left unformatted.
- `zip-check.sh` accepts upstream's `README.txt` in `Labels/`, `Wallpapers/` and `Bezels/` (and only
  that file, equal to upstream's).
- The About sticker prints `git describe` of the build tree; our `build/slot` has no tags, so it
  shows the crate version 0.1.0, as before ea438a0.
- `card/test-coresave.sh` (new in 1.8.0) fails on this Mac in the unpatched tree too: macOS `sh` keeps
  `CMDLINE` after `CMDLINE=... run ...`, so the later busybox crash reads as slot's and its log is kept.
  `task check` now runs the card tests through `scripts/card-tests.sh`, which gates a card test only
  when the unpatched tree passes it, like `run-tests.sh` does for the layout tests (ADR 0045).
- Upstream-first candidates (ADR 0047), not opened: a `GameButton` list per system so extra console
  buttons become remappable rows (would replace `raw_buttons`); a context or platform filter on
  table entries so a chord can apply to some systems only (would replace `keep_applicable`); the
  resampler `drop` clamp from ADR 0083, still present in 1.8.0.
