# WonderSwan and WonderSwan Color on slot-nes-snes: plan (2026-10-18)

"Our tree" means slot v1.7.0 plus patches 0001 to 0057. The integration patches will be written on
upstream main 1b20432 (ADR 0083), so this plan names seams, not line numbers. "Cygne"
means libretro/beetle-wswan-libretro at `4b01295` (ADR 0092). The reference is nelynes/slotPlus
branch `main` ([273ded9](https://github.com/nelynes/slotPlus/commit/273ded9) core build,
[69b8379](https://github.com/nelynes/slotPlus/commit/69b8379) shoulder modifiers,
[0f895d3](https://github.com/nelynes/slotPlus/commit/0f895d3) vertical controls,
[2ab147a](https://github.com/nelynes/slotPlus/commit/2ab147a) SELECT inert on horizontal games,
[ceed887](https://github.com/nelynes/slotPlus/commit/ceed887) 360x240 buffer,
[21cc4b0](https://github.com/nelynes/slotPlus/commit/21cc4b0) carts). We take ideas from it and
reimplement them with credit. Nothing is cherry-picked (docs/research/fork-nelynes.md section 2).
This follows the NeoGeo Pocket groundwork (on its own branch) step for step.

## TL;DR

- **Verdict: go.** Light core, no BIOS, saves through the ordinary `.sav` path:
  - horizontal games are 224x144, a 3x fit in the 240x160 GBA-sized path (672x432 on the panel);
  - vertical games are 144x224, drawn upright by the core itself, a 2x fit in a 360x240 canvas
    (288x448);
  - no host rotation code: slot refuses `SET_ROTATION`, so the core turns the picture;
  - the work is the input remap (issue 96).
- **Speed: 60 Hz mode by default, Native 75 Hz as a user option** (section 3, ADR 0092). Both play
  the game at its own speed; the default rides the upstream path.
- **Done now (groundwork, this branch):**
  - the core build, pinned for host and device (issue 92);
  - the licence record;
  - host tests with a generated cart (`patches/0059-wswan-core-tests.patch`, issue 97). They prove
    boot, the 224x144 and 144x224 pictures, both frame rates, the 5-in-4 cadence, states with 60 Hz
    mode on, the SELECT trap, and save RAM.
- **Two declared-default traps**, both pinned by tests: `wswan_60hz_mode` (unanswered, 75.47 fps)
  and `wswan_rotate_display` (unanswered, `manual`: every SELECT press turns the picture). The
  options patch sets both on every load.
- Expected size: 7 patches on the main 1b20432 base. Input is M, everything else S or M.

## 1. What nelynes did (reference only)

| Area | nelynes/slotPlus `main` | Ours |
|---|---|---|
| Core | beetle-wswan `4b01295`, `make platform=unix`, `-mcpu=cortex-a53`, no sha256 | Same commit, pinned with archive sha256, glibc gate (issue 92, done) |
| Enums | `Platform::Ws` and `Core::Cygne` added to upstream's `ALL`; upstream tests edited | `Platform::Ws` in `SHELVES`, `Core::MednafenWswan` in `EVERY`, upstream `ALL` and tests untouched (ADR 0092) |
| Shelf | `Games/WS`, `.ws .wsc` | Same |
| Speed | `wswan_60hz_mode` never set, so 75.47 fps through the fork's `Owed` pacing | Set explicitly, 60 Hz mode default, Native a user option (section 3) |
| Rotation | Answers `SET_ROTATION`, rotates on the CPU in `video_refresh` | Refuses it (upstream already does), `wswan_rotate_display` per game from the footer (section 4) |
| Canvas | 360x240 buffer; horizontal through a 240x160 window at 3x, vertical whole at 2x | 240x160 for horizontal carts, 360x240 for vertical ones, chosen once per game (section 4) |
| Input | Shoulder modifiers on horizontal games, turned maps on vertical ones, SELECT flips vertical games only | Same scheme, our own code and tests (section 5) |
| Shader | `shader_ws` inside `slot.state` | Own Screen section, setting outside `slot.state` (ADR 0051) |
| Cart | Bitmap cart, black for `.ws`, clear for `.wsc` | Retro bitmap cart (ADR 0054), their drawing as a credited reference |
| Tests | Input tables, `ws_video.rs` geometry | Real-core tests on a generated cart (patch 0064), platform tests per step |

## 2. Core facts found while building (2026-10-18)

- **Build.** Host `mednafen_wswan_libretro.dylib` (arm64, `platform=osx`). Device
  `mednafen_wswan_libretro.so`:
  - sha256 `c52d0c086cc5c17b3f2b84e741c9dbebeb84288ac6eec09dbef3ddea35b1d010`;
  - built in rust:1-bullseye `sha256:4730e387...`;
  - all 16 compile lines carry `-mcpu=cortex-a53` (the Makefile appends to `CFLAGS`);
  - plain C, linked by `$(CC)`; NEEDED is `libc.so.6` only, at GLIBC_2.17 or older.
- **Name.** The makefile's `TARGET_NAME` is `mednafen_wswan`, so `Core::as_str()` is
  `mednafen_wswan`. The option prefix is `wswan` (every key is `wswan_*`). Declared keys:
  `wswan_language`, `wswan_name_source`, `wswan_birth_year`, `wswan_birth_month`,
  `wswan_birth_day`, `wswan_sex`, `wswan_blood`, `wswan_rotate_display`, `wswan_rotate_keymap`,
  `wswan_mono_palette`, `wswan_gfx_colors`, `wswan_frameskip`, `wswan_frameskip_threshold`,
  `wswan_60hz_mode`, `wswan_sound_sample_rate`, `wswan_sound_low_pass`.
- **Hardware.** The core always emulates a WonderSwan Color (`wsc = 1`); mono carts run in its mono
  mode. A ROM under 64 KB is refused. The footer is the last 16 bytes: a far jump at 0xfff0 (the
  reset vector), then publisher, colour flag (0xfff7), game id, version, ROM size, **save type
  (0xfffb)**, **flags (0xfffc, bit 0 vertical)**, mapper and a checksum. WonderSwan ROMs carry no
  title, so names come from the file and the dat.
- **Picture.** RGB565, landscape 224x144 at a pitch of 448 bytes. The host's 240x160 path centres
  it at (8, 8); the test pins every pixel.
- **Timing.** 3,072,000 / (159 x 256) = 75.47 fps, 44100 Hz. With `wswan_60hz_mode=enabled`:
  60.38 fps, five emulated frames every four `retro_run` calls, the sound of the five spread over
  the four. Unanswered, 75.47 fps although the declared default is `enabled` (`libretro.c` starts
  it false). `check_variables` runs inside `retro_load_game`, before slot reads the av info, so
  setting the key before load is enough. Tested: 60.38 and 75.47 fps, and about 44100 sound frames
  a second of game in both modes.
- **Rotation.** slot's env handler answers no `SET_ROTATION` (it falls to `_ => false`), so the
  core rotates in software into `rotate_buf`. `portrait` draws 144x224, `landscape` 224x144. The
  core ignores the footer's vertical flag (the Mednafen code is under `#if 0`), so slot must read it.
  `manual`, the value when slot does not answer, lets every SELECT press turn the picture. Tested.
- **Input.** With `wswan_rotate_keymap=disabled` the core reads one map: X pad on the D-pad, Y pad on
  R2 (up), R (right), L2 (down), L (left), RetroPad A is A, RetroPad B is B, START is Start. SELECT
  is only the core's rotate key.
- **Saves.** `retro_get_memory_data(SAVE_RAM)` is the cart's EEPROM (128, 1024 or 2048 bytes, save
  type 0x10, 0x50, 0x20) or SRAM (8 KB to 512 KB, types 0x01 to 0x05), or a WonderWitch block (SRAM
  plus 512 KB of flash). No RTC is exposed (`MEMORY_RTC` is NULL), and the core writes no file of its
  own. A cart with no save type gives `None`. The console's internal EEPROM (the owner profile) is
  rebuilt from the `wswan_name`, birth date, sex and blood options at every boot and never persisted.
  Tested: the SRAM marker, the sizes per type, no file in `Saves/`, and a second boot reading back
  what slot writes after load. States carry SRAM, EEPROM, the RTC and the 60 Hz cadence (tested with
  60 Hz mode on).

## 3. Speed: 60 Hz mode or native 75.47 Hz

| | 60 Hz mode (`enabled`) | Native (`disabled`) |
|---|---|---|
| Reported fps | 60.38 | 75.47 |
| Game speed | Its own (5 frames per 4 calls) | Its own |
| Frames shown on a 59.6 Hz panel | 4 in 5, fixed cadence chosen by the core | About 4 in 5, cadence from `av_rate::owed_frames` (1 or 2 a tick) |
| Path in slot | Inside ADR 0071's 2 fps window: the upstream path, panel-locked, about 1.3% slow (NES at 60.1 fps is 0.8% slow the same way) | ADR 0071's paced path with 2-frame ticks, which no core exercises yet (PAL owes 0 or 1); upstream's frame trim applies to the second frame |
| Pitch | Scaled with the panel like every NTSC core | The core's own |
| Better on | Any 60 Hz class panel | A panel that runs near 75 Hz, if one ever ships |

**Decision (ADR 0092): 60 Hz mode is the default; Native is a user option.** ADR 0071 made Native
the PAL default because there the panel rate changes the content's speed. Here neither mode does,
60 Hz mode is the core author's declared default rather than a value tuned for our panel, and it
keeps WonderSwan on the most tested path. Native stays available, as the maintainer's rule asks,
as a **Refresh: 60 Hz / Native** row in the WonderSwan Screen section; the user's choice persists
and becomes their default, and applies from the next game (changing `wswan_60hz_mode` mid-game makes
the core send `SET_SYSTEM_AV_INFO`, which slot reads only at spawn). Native ships with a host test
of the 2-frame tick through `owed_frames`.

## 4. Video and the Screen section (issue 95)

- **Canvas per game, from the footer.** Horizontal cart: `(240, 160)`, the GBA-sized path, 3x,
  Actual 672x432 centred. Vertical cart: `(360, 240)`, the core draws 144x224 upright, 2x, Actual
  288x448. The footer is read at scan time (issue 93), so the canvas is chosen once at load, with no
  per-frame source rect. This needs one new seam: today `Core::canvas(core, platform)` is per
  platform (read by `open_named` and `App::source_rect`), so issue 93 adds a per-game answer fed by
  the footer's vertical bit.
- **Tradeoff: the turned view of a vertical game.** nelynes lets SELECT flip a vertical game between
  upright and turned (play with the handheld held sideways). With a per-game canvas, the turned view
  is a 224x144 frame in the 360x240 canvas at 2x (448x288), not 3x. v1 takes that: the flip changes
  `wswan_rotate_display` and the button map, never the canvas. A 3x turned view needs a per-frame
  source window (a 240x160 crop of the 360x240 canvas when the frame is landscape); it is a follow-up
  if anyone asks.
- **Own Screen section** `SCREEN_WS` (the maintainer's rule), three rows:
  - **Shader**: Off, then upstream's LCD3x (for the 3x horizontal picture, the ADR 0060 precedent; a
    vertical game at 2x falls back to Off for LCD3x, logged once), then the shared retro list. Stored
    in its own `Config/` file (ADR 0051).
  - **Picture**: Actual (default) and Stretch. No Crop (no overscan). In `Config/picture.txt`
    (ADR 0061).
  - **Refresh**: 60 Hz (default) and Native (section 3). No PAL Speed row: there is no PAL
    WonderSwan.
- The Transparent look (nelynes 9201b8a, an unlit reflective LCD) is a later, separate item for NGP
  and WonderSwan together, as a retro mode in `RETRO_FRAG` (fork review).

## 5. Input (issue 96)

The WonderSwan has two 4-way pads (X and Y), A, B and Start. The SP has a D-pad, four face buttons,
four shoulders, START and SELECT. slot sets `wswan_rotate_keymap=disabled` and does all the
mapping, in the `snes_input.rs` pattern. nelynes' tables are the reference, credited.

- **Horizontal games** (most of the library): the D-pad is the X pad, A and B are A and B, START is
  Start. Holding L turns the D-pad into the Y pad; holding R turns the face diamond (X up, A right,
  B down, Y left) into the Y pad (nelynes 69b8379). X and Y are turbo A and B when no modifier is
  held. SELECT does nothing in the game (nelynes 2ab147a), so the picture never turns.
- **Vertical games**: the D-pad is the Y pad and the face diamond the X pad, turned so up is the
  game's up; L and R are A and B (nelynes 0f895d3, matching the core's own portrait map).
- **The flip**: on a vertical game only, a SELECT tap swaps upright and turned (section 4), with the
  matching map. It is a per-game choice remembered in the cart's state, not a global row.
- **Open for the device gate**: the SP's L2 and R2 could carry the Y pad directly (the core's own
  descriptors) for players who prefer it to the modifiers. If wanted, it is a choice in the Screen
  section, never a silent change.
- SELECT combos stay slot's (Select+X picture, Select+Y guard).
- Policy: `owns_shoulders` false and `passes_xy_through` true (the Mega Drive answers), because L,
  R, X and Y all reach the remapper, which applies turbo to X and Y itself when no modifier is held.

## 6. Saves (part of issue 93)

The ordinary path: `RetroCore::save_ram()` is `Some` for any cart with a save type, so `.sav`
writes on autosave, eject and `flush_resume`, ADR 0072's no-state path and `save_ram_trusted` all
apply unchanged. What the issue still owns:

- `Saves/WS/<stem>.sav` per ADR 0012, and ADR 0082's hack updates keep it.
- A cart with no save type writes no `.sav` (`save_ram()` is `None`).
- No RTC in the `.sav`: the few RTC carts keep their clock in save states only, and the core reads
  the host clock at boot. Recorded, not fixed.
- The owner profile in the internal EEPROM is rebuilt each boot from options; slot sets
  `wswan_name_source` and the profile keys to fixed values so the profile is deterministic.
- WonderWitch images (detected by the core) persist SRAM plus 512 KB flash as one block; they work
  through the same path and are noted, not tested.

## 7. Shelf, scan, cart art (issues 93 and 98)

- Scan `.ws` and `.wsc` onto one `Games/WS` shelf. The core also lists `.pc2` (Benesse's Pocket
  Challenge V2), which is in neither dat and is left out. The title is the file stem. A footer reader in
  our own `slot_store::ws` module returns the colour flag (0xfff7), the save type (0xfffb) and the
  vertical flag (0xfffc bit 0). A file under 64 KB lists but is not seatable (the core refuses it).
- Cart: the retro bitmap renderer (ADR 0054), two shells, black (WonderSwan) and clear (Color),
  chosen by the extension and the footer colour flag (nelynes 21cc4b0 as a drawing reference).
- Labels: `tools/fetch-labels.py` takes one ScreenScraper id per shelf, but WonderSwan has two:
  `wonderswan` 45 and `wonderswancolor` 46 (Skyscraper `platforms_idmap.csv` at ccd49ae, rows
  `wonderswan,45,48,4925` and `wonderswancolor,46,49,4926`). Dats are `Bandai - WonderSwan` and
  `Bandai - WonderSwan Color` (libretro-database `metadat/no-intro`). The NGP choice (issue 78 on
  its branch) applies: one `WS` entry with both dats, the id picked per ROM by the footer colour flag.

## 8. Issue list (Phase 11)

| Issue | Title | Size | Needs the new base |
|---|---|---|---|
| 91 | Tracking: WonderSwan and WonderSwan Color on Beetle Cygne | L | n/a |
| 92 | Build Beetle Cygne from a pinned commit for host and device and record its licence | S | No, done |
| 93 | Add `Platform::Ws` with its own shelf, scan, footer reader, saves and explicit policy | M | Yes |
| 94 | Set the WonderSwan core options: 60 Hz mode, rotation and keymap on every load | S | Yes |
| 95 | Give WonderSwan its canvases and its own Screen section with Shader, Picture and Refresh rows | M | Yes |
| 96 | Map the WonderSwan X and Y pads for horizontal and vertical games | M | Yes |
| 97 | Test WonderSwan with a generated cart that paints, turns and saves | S | Partly: core tests done, platform tests per step |
| 98 | Draw WonderSwan carts (black and clear shells) and fetch their labels | M | Yes |
| 99 | WonderSwan device gate on the RG34XXSP | S | Yes |

Nine issues: `scripts/setup-github-project.py` globs two-digit stems, so there is no issue 100, and
saves sit in issue 93 because they need no new mechanism.

## 9. Device gate (issue 99)

1. Play Gunpey (vertical), Judgement Silversword (vertical shooter), Klonoa: Moonlight Museum and
   Final Fantasy (Color) for 10 minutes each under `SLOT_TRACE`: full speed, zero audio underruns,
   and the ms a frame recorded (estimate 1 to 2 ms, plus 0.1 to 0.3 ms for the core's rotation copy
   on vertical games, unmeasured).
2. Both Refresh values on one horizontal and one vertical game; judder looks the same 4 in 5.
3. Save in-game, eject, boot: the save is there with and without the resume.
4. Eject and GBA: the GBA leg equals a GBA-only run.

## 10. What remains for the integration step (on main 1b20432)

Issues 93 to 96 and 98 to 99, plus the platform half of 97, in that order. When the platform patch
lands:

- `licenses/mednafen_wswan-GPL-2.0.txt` moves out of `cores/mednafen_wswan/`;
- the core joins `scripts/dist-device.sh` and `scripts/zip-check.sh` (the cores list, the `req`
  and `ok` lists, the licence file list and the strings cross-check pair `mednafen_wswan:Beetle.WonderSwan`, the core's `library_name`);
- `zip-check.sh` gains `WS` in its `games` list;
- docs/PLAN.md's "Who it's NOT for" line gains WonderSwan (left alone here, every system branch
  edits it).
