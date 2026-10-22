# 0108. Every console button is a row on the In-Game Controls page, named and saved per system

- Status: Accepted. Amends [0099](0099-arcade-on-finalburn-neo.md) and [0106](0106-rebase-to-slot-v1-8-0.md)
- Date: 2026-10-22
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0106](0106-rebase-to-slot-v1-8-0.md) (the control table port), [ADR 0099](0099-arcade-on-finalburn-neo.md)
  (arcade input map), [ADR 0047](0047-upstream-first-fixes.md), [ADR 0083](0083-rebase-to-slot-main-1b20432.md),
  patches 0151 to 0154, [docs/upstream/console-buttons-issue.md](../upstream/console-buttons-issue.md)

## Context

Two reports from the maintainer after v1.8.0-ns.1:

1. On some systems there is no control setting for X and Y. ADR 0106 kept X and Y as fixed console
   buttons (`raw_buttons`) on the systems that pass them to the game (SNES, Mega Drive, Sega CD, 32X,
   PlayStation, WonderSwan, Atari, Virtual Boy, arcade, Neo Geo CD, SuperGrafx with 6 Buttons) and hid
   upstream's Turbo A and Turbo B rows there. PlayStation L2 and R2, the Virtual Boy right pad and the
   arcade and Neo Geo buttons beyond A and B were not rows either ("Not ported" in ADR 0106). Every
   remaining row carried upstream's Game Boy Advance names, so on a Mega Drive the row called A Button
   is the console's C button, and on an arcade board nothing said which button is Attack.
2. In some arcade games, Knights of the Round (`knights`) the example, the buttons do nothing.

### The arcade report: what was checked

- FBNeo at the pin (2dbbac7) declares, for `knights`, Coin on SELECT, Start, the D-pad, Attack on
  RetroPad B (id 0) and Jump on RetroPad A (id 8): `P1 Attack` and `P1 Jump` are `p1 fire 1` and
  `p1 fire 2` in `d_cps1.cpp` (`KnightsInputList`), and the Classic RetroPad maps fire 1 and 2 to B and A
  (`RETRO_DEVICE_ID_FIRE01/02`, `retro_input.cpp`). The set has no third button; its special is Attack
  and Jump together. Read back from the core on the host (input descriptors, environment call 11): the
  same eight entries, and the core polls exactly ids 0 and 2 to 8.
- Through a whole slot session on the host, B sends mask 0x0001 and A 0x0100 (`SLOT_TRACE`), and the
  core answers both as pressed in `input_state` (`controls_real_games.rs` on the maintainer's good
  `knights.zip`, 2,355,180 bytes, the copy on the device card). A frame dump of the same session: a SELECT
  tap gives CREDIT 1, START joins (the player select screen), B picks Lancelot. The paths for A, B,
  SELECT and START on CPS1 are the same as in v1.8.0-ns.1: the X/Y pass-through of ADR 0106 never touched
  them, and the arcade map of ADR 0099 matches what FBNeo declares for `knights`, `ffight`, `sf2`, `ssf2t`,
  `ddtod`, `mslug` and `kof98` (below).
- So the report is not reproduced on the host, and the cause on the device is not known yet. What the
  device run has to tell apart (DEVICE-GATE "Controls page per shelf" step 3, `task controls:device`):
  the game waits for a coin, which is SELECT, and nothing on the page said so (a press of START or of the
  face buttons in attract mode does nothing, which looks like dead buttons); or a global In-Game row
  (A Button or B Button) was cleared or moved while looking for an X/Y setting (X on a row clears it, and
  the shared set reaches every system). Three real defects were found on the way, and they are fixed here:
  - A turned vertical CPS game (CPS Vertical Games: Turned) lost X, Y, L2 and R2 and its D-pad was not
    turned: the sideways pad code (`ws_input::SIDEWAYS`, 3) was the Virtual Boy's stick code
    (`vb_input::STICK`, 3), and `WsPad::remap` asks the Virtual Boy first, which keeps only D-pad, A, B,
    L, R, START and SELECT. Every six-button vertical game (19XX, 1944, Progear) lost half its buttons.
  - Nothing on the In-Game page named an arcade game's buttons: the rows said A Button and B Button
    and the X and Y rows were hidden, so a player had no way to find out that Attack is B.
  - A set FBNeo cannot run (a ROM missing or with the wrong CRC) shows FBNeo's own error screen, on
    which no button does anything, and slot says nothing (left as it is, below).
- The device itself was not available for this change (another job was reading it). Whether the device
  showed something the host does not is what DEVICE-GATE "Controls page per shelf" step 3 and
  `task controls:device` answer, with Knights of the Round as a named check.

FBNeo's declared inputs for the sample sets (id: name), read back on the host:

- `knights`: 2 Coin, 3 Start, 4-7 D-pad, 0 Attack, 8 Jump.
- `ffight`: 2 Coin, 3 Start, 4-7 D-pad, 0 Attack, 8 Jump, 1 Special.
- `sf2`, `ssf2t`: 2 Coin, 3 Start, 4-7 D-pad, 1 Weak Punch, 9 Medium Punch, 10 Strong Punch, 0 Weak Kick,
  8 Medium Kick, 11 Strong Kick, 12 Buttons 3x Punch, 13 Buttons 3x Kick.
- `ddtod`: 2 Coin, 3 Start, 4-7 D-pad, 0 Attack, 8 Jump, 1 Use, 9 Select.
- `mslug`, `kof98`: 2 Coin, 3 Start, 14 Select, 4-7 D-pad, 0 Button A, 8 Button B, 1 Button C, 9 Button D,
  11 Buttons AB, 10 Buttons CD, 13 Buttons ABC, 12 Buttons BCD.

## Decision

### Rows

The In-Game page is upstream's twelve rows plus two appended rows, L2 and R2 (`QuickRow::GameL2`,
`GameR2`, `GameButton::L2`, `R2`, all appended; `QuickRow::IN_GAME` is the page, `QuickRow::CONTROLS` and
`GameButton::ALL` keep their pinned twelve). A row stands for one RetroPad bit before slot's remaps. On a
system that passes X and Y to the game, upstream's Turbo A and Turbo B rows are those console buttons
(their bits are X and Y; slot sends them unpulsed there, as it always did), so X and Y need no new row.
`raw_buttons` is gone: X and Y reach the game only from their rows, and L2 and R2 only from theirs, so
moving a row moves the console button.

### Names

While a game plays, each row is named after what its bit becomes in the core, taken through the same
remap the emulator thread runs (`ws_input::pass`, then turbo): `console_pad::label`. The names per
RetroPad id and system come from each core's input code at the pinned commit (the table in
`console_pad::core_name`; sources below). A row whose bit reaches nothing the core reads is hidden. The
arcade boards take every name from the set itself: FBNeo declares its inputs per set on its first frame
(environment call 11, `slot-retro/src/pad_names.rs`), and the page shows them (Attack, Jump, Weak Punch,
Button A...). What the player sees per shelf is in the README and in DEVICE-GATE.

Layered buttons keep one name. WonderSwan horizontal: L is "Y Pad on D-Pad" and R "Y Pad on Buttons"
(hold them to turn the D-pad or the face buttons into Y1 to Y4); X and Y alone are turbo A and B. Neo Geo
and FBNeo's other combo inputs ("Buttons AB", "Buttons ABC") are rows when the set declares them on a
bit a row sends; on L2 and R2 they start unbound (those are Rewind and Fast Forward by default).

### Saving

Upstream keeps one set of In-Game buttons for every console (`Config/controls.txt`). That stays as it is
and is still what the main menu's In-Game page edits, and what Game Boy, Game Boy Color and Game Boy
Advance play with. The other 23 systems read it too, and a change made on the In-Game page while one
of them plays is written for that system alone, to `Config/controls/<SHELF>.txt` (`SNES.txt`,
`CPS1.txt`...), one `key = value` line per changed row in upstream's own key and value words. A system's
file overrides the shared set row by row, so a choice made on the main menu still reaches every system
that has not changed that row. Reset on the In-Game page while a game plays resets that system's rows to
the factory buttons. The factory buttons do not change: every row starts where upstream's starts, and L2
and R2 start on L2 and R2 where the game owns them (PlayStation, Virtual Boy right-pad mode) and unbound
elsewhere. Saving is per system, not per arcade set: the CPS1 file serves every CPS1 set.

### Clash warnings

Within a game the warning compares only rows shown for that system, and on the systems where slot gives
plain L2 and R2 to the game (PlayStation, Virtual Boy right-pad mode) it leaves out the shortcuts that sit
on plain L2 or R2, which `Gestures::down` already skips there. A fresh card flags nothing on any page.

## Tests

- `slot/tests/controls_pages.rs` (no cores): for every `Platform::SHELVES` entry and each pad mode (WonderSwan
  horizontal and vertical, Virtual Boy stick and right-pad, SuperGrafx 2 and 6 buttons, CPS upright and
  turned) it lists the ids the core reads (kept apart from slot's name table), presses each visible row's
  factory button alone and with every other visible row's button through the real `Pad::mask_with` and
  `ws_input::pass`, and asserts (1) every id the core reads is reached by a visible row, (2) no two visible
  rows start on the same device button, (3) turbo rows show only where the console's face buttons are A and B
  (NES, Disk System, Game Gear, Master System, TurboGrafx-16, PC Engine CD, SuperGrafx 2-button, WonderSwan
  horizontal, Lynx, Neo Geo Pocket, PICO-8), and that a turned vertical CPS game keeps X and Y and turns the
  D-pad. A new `Platform` does not compile until it has a list. Broken on purpose: putting back the Turbo A
  strip on X/Y systems fails (1) and the turned test.
- `slot/tests/arcade_controls.rs` (FBNeo, zero-filled sets of the pinned dat): for `knights`, `ffight`, `sf2`,
  `ddtod` and `mslug`, every input the set declares (FBNeo's combo inputs and L3/R3 aside) reaches the core
  from a visible row named exactly as the set names it; `knights` hides X, Y, L and R. (`kof98` declares the
  same Neo Geo inputs as `mslug`; its zero-filled set would be 100 MB, so it runs only in the real-game test.)
- `slot/tests/console_controls.rs` (snes9x and pcsx_rearmed, generated games): X and Y rows named on SNES, a
  move of the SNES X row lands in `Config/controls/SNES.txt` only and sends X from the new button, and the
  PlayStation page shows L2 and R2 rows with nothing flagged.
- `slot/tests/controls_real_games.rs` and `task test:controls`: one real game per shelf from the
  maintainer's library (`harness/controls-games.tsv`, skipped without `SLOT_CONTROLS_GAMES`), played in a
  whole session: every visible row's button is pressed and the core's own `input_state` answers are read
  back (`console_pad::PadSeen`). Every id the core polls that `controls_common::reads` lists for it must be
  answered for some row, and no row may reach an id its name does not cover (a button slot holds by itself,
  the Atari 7800 difficulty switch, is measured first and left out). Many cores poll all 16 ids every frame,
  so a polled id outside the core's list is printed, not required. Run on 2026-10-22 on the M5 Max: all 26
  shelves pass (games in `harness/controls-games.tsv`; PlayStation Ace Combat 2 answers L2 and R2, SNES Super
  Mario World X and Y, Mega Drive Street Fighter II' all six buttons and Mode, Knights of the Round Attack,
  Jump, Coin and Start).
- `scripts/device-controls.sh` and `task controls:device`: the same check on the RG34XXSP over adb, from the
  `slot: pad polled`, `slot: pad answered` and `slot: pad names` trace lines, against
  `harness/controls-reads.tsv` (the same lists as hex masks; `controls_pages.rs` fails if the two drift).

What a core reads and slot leaves without a row, on purpose: L3 and R3 (the device has no stick clicks;
the Virtual Boy right pad on L2/R2/L3/R3 is reached in ABXY mode from X, A, B and Y), the cores' own turbo
and extras slot replaces or does not offer (fceumm and nestopia X, Y and VS coins; the PC Engine cores' III
to VI on a 2-button pad), FBNeo's fire 7 to 10 and its combo inputs on L2 and R2 (rows, unbound), and the
Atari switches (Screen rows). They are not in `controls_common::reads`.

## Consequences

- The player sees, per shelf, the rows and names listed in the README section "Controls". X and Y can be
  moved on every system that has them, L2 and R2 on PlayStation, the right pad on the Virtual Boy, all six
  buttons on CPS and four on Neo Geo.
- Behaviour change from ADR 0106 on purpose: a button bound to another row no longer also stops the
  console's X or Y (that was `raw_buttons`' "not bound to the game" filter); both rows fire and the clash
  warning names the other row, as upstream does for any two rows.
- GBA, GB and GBC are unchanged: no console rows, the shared `controls.txt`, upstream's names. The L2 and R2
  rows are hidden there (`in_game_rows_hidden`; upstream's own `in_game_hidden()` list is unchanged, which
  `in_game_menu.rs` pins). Harness compare 0 diffs.
- New upstream test site (l), approval pending: `the_thumb_reaches_the_bottom_only_on_the_last_row` in
  `slot-ui/tests/quick_menu.rs` walks `QuickRow::IN_GAME` instead of `QuickRow::CONTROLS` (one token), because
  the In-Game page has 14 rows now. Placing L2 and R2 anywhere else breaks
  `turbo_b_moves_off_y_from_the_in_game_page` or `in_game_buttons_are_set_from_the_main_menu_and_reach_a_game`
  instead (both count rows with an empty hidden list on the main menu). See CONTRIBUTING site (l).
- Upstream files touched: `bindings.rs` (two variants, their arms, the 14-slot array, three `pub(crate)`),
  `quick_menu.rs` (two variants, `ALL`, two arms, the page and scroll lists, `quick_text_label_face`),
  `mask.rs` (two arms, `EVERY`, `pub fn bit`), `input/mod.rs`, `libretro.rs` (one environment arm, one
  line in `input_state`), `core.rs` (two trait methods with defaults), `app.rs`, `session.rs`, `emu.rs`,
  `frontend.rs`. Listed in `docs/UPSTREAM-TOUCHPOINTS.md`.
- Left as it is: FBNeo's error screen for a broken set takes no input and slot does not say why. A banner
  for it is a separate change.
- Known limits: the clash warning's text ("Same as Console ...") is drawn once at boot from the fixed row
  names, so on SNES a clash with the X row reads "Same as Console Turbo A". With Turbo set to Off, the
  WonderSwan horizontal X and Y rows (turbo alone) are hidden, and with them the reminder that R with X or Y
  gives Y1 or Y4 (the buttons still work). The names follow the game's starting layout; a vertical
  WonderSwan game turned with a SELECT tap keeps the upright names.
- On every upstream rebase and every change to input, the control table or a core's input options, run
  `task check` (it runs the three no-library tests), `task test:controls` and DEVICE-GATE "Controls page per
  shelf" (CONTRIBUTING section 10).
- Upstream-first candidate (ADR 0047), not opened (the maintainer cannot open pull requests upstream at the
  moment): a per-system list of console buttons in upstream's control table, named by the core's input
  descriptors. Draft: `docs/upstream/console-buttons-issue.md`.

## Sources for the names (pinned commits in `SLOT_PIN`)

fceumm `libretro.c` 2943-2962, nestopia `libretro.cpp` 822-831, snes9x `libretro.cpp` 1839-1855,
snes9x2005_plus `libretro.c` 500-528, Genesis Plus GX `libretro.c` 469-499 (6-button pad on X, Y, Z, Mode),
picodrive 1792-1804 (6-button pad, `picodrive_input1`), pcsx_rearmed 2257-2274, Beetle PCE Fast 2322-2361,
Beetle SuperGrafx 1580-1605, Beetle WonderSwan 1316-1340 (slot's own rotation, `ws_input.rs`), Beetle Lynx
322-375 (its descriptor swaps A/B and the options; the polling code is what counts), Beetle NeoPop 534-560,
Beetle VB 1134-1148, stella2014 `libretro.cxx` 972-987, prosystem `libretro.c` 317-335, NeoCD
`libretro_input.cpp` 50-68, FAKE-08 `libretro.cpp` 292-334, FBNeo `retro_input.cpp` (generic fire N on the
Classic RetroPad, Street Fighter layout 2452-2471, Neo Geo 2435-2450) and each set's own input list.
