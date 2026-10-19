# Atari Lynx on slot-nes-snes: plan (2026-10-18)

"Our tree" means slot v1.7.0 plus our patches at the time of writing. The integration landed on
slot main 1b20432 (ADR 0083) on 2026-10-19, as patches 0070 to 0079 (section 11). "Beetle" means
libretro/beetle-lynx-libretro at `fcdefcf` (ADR 0093). The reference is nelynes/slotPlus branch
`main`: [749523c](https://github.com/nelynes/slotPlus/commit/749523c) (core, shelf, rotation),
[98419f4](https://github.com/nelynes/slotPlus/commit/98419f4) (card),
[0848fcb](https://github.com/nelynes/slotPlus/commit/0848fcb) and
[b264635](https://github.com/nelynes/slotPlus/commit/b264635) (pacing),
[d7d0e74](https://github.com/nelynes/slotPlus/commit/d7d0e74) (rotation by title, override file),
[185257a](https://github.com/nelynes/slotPlus/commit/185257a) (turned play). We take ideas and
reimplement them with credit; nothing is cherry-picked.

## TL;DR

- **Verdict: go, last of the new systems, with one open choice.** The maintainer confirms the core:
  - **Beetle Lynx** (built and tested here, nelynes' core): needs the BIOS, states only.
  - **Handy** (libretro/libretro-handy): boots without a BIOS through an HLE boot and saves EEPROM,
    but ships a source file with no licence (`lynx/lynxdec.cpp`) and writes its EEPROM only at
    reset and deinit.
- **Done now (groundwork, this branch):** the Beetle build pinned for host and device (issue 102),
  the licence record, and host tests (`patches/0065-lynx-core-tests.patch`, issue 110).
- **Three facts the fork review had wrong or open, now pinned by tests:**
  1. The core's reported 75 fps is a constant. Each `retro_run` is one game frame: **59.9 Hz** as the
     boot ROM leaves the timers, 75 Hz only if the game sets it. Pacing must follow the real rate
     (issue 107).
  2. **The core does turn the pad**, through `lynx_rot_screen` in its libretro glue. slot must always
     set that option (issues 105 and 109).
  3. **Missing BIOS:** the cart loads, no error, no frame ever ends, dark fill. slot checks the file
     first (issue 104).
- Size: ten patches (0070 to 0079) on slot main 1b20432. Effort L, value low to medium.

## 1. What nelynes did (reference only)

| Area | nelynes/slotPlus `main` | Ours |
|---|---|---|
| Core | beetle-lynx `fcdefcf`, no sha256 | Same commit, archive sha256, static C++ runtime, glibc gate (issue 102, done) |
| Licence | One `lynx-GPL-2.0.txt` | `COPYING` plus the Handy zlib text; counts and headerless list in LICENSING.md |
| BIOS | `BIOS/lynxboot.img`, not shipped, no check | Same place, never shipped, checked before launch with a toast (issue 104) |
| Rotation | Core's `auto` plus a host "handheld turned ccw" quarter turn of picture and pad; 4-title list; `Config/lynx_rotation.txt` | `lynx_rot_screen` always `0` or `180`; right carts flipped so every turned cart is held the same way; same list and override file (issue 109) |
| Pacing | `Owed`: audio-implied rate above 62 fps | Measured rate for Lynx only, through ADR 0071's owed frames; Lynx Speed row (issue 107) |
| Canvas | 160x102 in a 180x120 window at 4x | Same, `Core::canvas = (240, 160)`, own Screen section (issue 106) |
| Saves | States only | States only, said in the README (issue 108) |
| Tests | `lynx_video.rs` (geometry) | Real-core tests with a homebrew image and synthetic carts, BIOS-gated where they need it (patch 0070) |

## 2. Core facts found while building (2026-10-18)

- **Build.** Host `mednafen_lynx_libretro.dylib` (arm64, `platform=osx`). Device
  `mednafen_lynx_libretro.so`: sha256
  `8c81d44977e563029522e49528f6f1d613fbfcb38ed40a42cdd304a9be71da32`, built in rust:1-bullseye
  `sha256:4730e387...`, all 29 compile lines with `-mcpu=cortex-a53`, needs only glibc at 2.17 or
  older.
- **Name.** `TARGET_NAME := mednafen_lynx`, option prefix `lynx`. Options: `lynx_rot_screen`
  (`auto` default, `manual`, `0`, `90`, `180`, `270`), `lynx_pix_format` (`16` default, `32`),
  `lynx_force_60hz` (`disabled` default).
- **Picture.** Always 160x102 through `video_cb`, RGB565 by default. In the generic host it lands
  at (40, 29) in 240x160. Lines the display never drew are filled with `MAKECOLOR(30, 30, 30)`.
- **Timing.** `av_info.fps` is 75.0 (60.0 with `lynx_force_60hz`), sample rate 44100. `retro_run`
  emulates until the display frame ends, or 700000 cycles (43.75 ms). Measured in sample frames per
  run: 736 (59.9 Hz) with the boot ROM's or the homebrew preset's timers, 588 (75 Hz) after the game
  writes HTIMBKUP $7E and PBKUP $20. `lynx_force_60hz` leaves both unchanged.
- **BIOS.** `lynxboot.img` from the system dir, first 512 bytes. Missing or shorter: the ROM is
  0x88 everywhere and nothing reports it. No HLE path for carts. The core's own cart list names the
  BIOS: crc32 `0x0d973c9d`, 512 bytes (md5 `fcd403db69f54290b51035d82f835e7b`). BS93 homebrew
  (`.o`) is copied to RAM and started at its load address with display timers preset, so it runs
  with no BIOS; the tests use that.
- **Files.** `.lnx`: 64-byte header, `LYNX`, bank 0 and 1 page sizes, version 1, title at 0x0a (32
  bytes), maker at 0x2a (16), rotation at 0x3a. `.lyx` (raw) only at 128, 256 or 512 KB. The core
  hashes the headerless body and, when its 87-entry list knows it, takes page size and rotation
  from the list over the header.
- **Rotation.** `update_input` remaps the d-pad by `rotate_screen` and calls `SET_ROTATION` and
  `SET_GEOMETRY` (aspect 80:51 or 51:80) when it changes. `auto` gives LEFT carts 1 (90 ccw) and RIGHT
  carts 3 (270). With the key unanswered, `rotate_mode` stays 0: no turn. `lynx.rotateinput` (the
  mednafen setting) is hard-wired off and never used.
- **Input.** RetroPad B is Lynx A, RetroPad A is Lynx B, L and R are Option 1 and 2, START is Pause,
  SELECT rotates only in `manual`.
- **Saves.** `SYSTEM_RAM` only (64 KB). No EEPROM at this pin. A state carries the whole machine.

## 3. BIOS handling (issue 104)

- slot never ships, fetches or names a source for the BIOS. The player puts their own
  `lynxboot.img` in `BIOS/`.
- Before a Lynx launch: present, 512 bytes, crc32 `0x0d973c9d`. Missing or the wrong size refuses
  the launch with a toast; the right size with the wrong checksum launches with a one-time toast.
- A 0-byte placeholder of the right name (common in BIOS packs) counts as missing.
- Tests: the missing and short cases need no BIOS and always run. Booting a cart needs the real file
  through `SLOT_LYNX_BIOS`; CI always takes that skip (section 7).
- With Handy, the same check becomes a warning: Handy falls back to its HLE boot.

## 4. Pacing (issue 107)

| Game rate | ADR 0071 as is (reported 75) | Panel (one frame a vsync) | Proposed Native (measured) |
|---|---|---|---|
| 59.9 Hz (boot ROM default) | 25% fast, sound overflows | Right speed; pitch right only if resampled from what the frame carried | Right speed, 1 frame a tick |
| 75 Hz (game sets it) | Right | 80% speed | Right, 1 or 2 frames a tick, 5:4 judder |

The row is **Lynx Speed: Native / Panel**, Native the default (ADR 0071's reasoning). The measure
is sample frames per run over the sample rate, smoothed and clamped, for this core only, so GBA and
the PAL path are untouched. `lynx_force_60hz` stays off.

## 5. Video, rotation and the Screen section (issues 106 and 109)

- Canvas 240x160, 4x Actual = 640x408 centred on 720x480; Stretch fills it.
- Own Screen section: Shader (Off, Grid, Dot, retro list; no LCD3x), Picture (Actual, Stretch),
  Lynx Speed, Turned carts (Flip right-turned / As drawn).
- Rotation: the raw frame is the Lynx LCD as drawn, so the player turns the handheld. Left carts:
  `lynx_rot_screen=0`. Right carts with "Flip right-turned": slot draws the frame flipped 180 and sets
  `lynx_rot_screen=180`, and the core turns the pad 180 (tested). One direction for every turned
  cart. The upright tall view needs a full 90 degree host turn and is deferred.
- Rotation source, in precedence: `Config/lynx_rotation.txt`, the title list (d7d0e74), the core's
  rotated checksum entries, header byte 0x3a.

## 6. Shelf, scan, cart art (issues 103 and 111)

- `Games/Lynx`, `.lnx` and `.lyx`. Title from the header, else the stem.
- Retro bitmap card after nelynes 98419f4.
- Labels: ScreenScraper `atarilynx` **28** (Skyscraper `platforms_idmap.csv` at ccd49ae, row
  `atarilynx,28,18,4924`), dat `Atari - Lynx`. Hash the body without the 64-byte header.

## 7. Tests and CI

`lynx_core.rs` (patch 0070), 10 tests:

| Needs a BIOS | Test |
|---|---|
| No | homebrew draws 160x102 at 59.9 Hz while reporting 75 |
| No | `lynx_force_60hz` changes only the reported fps |
| No | a game that sets 75 Hz gets 75 Hz frames |
| No | state round-trip; no save RAM |
| No | no BIOS: a `.lnx` loads, never draws, frames run to the cap; a short BIOS the same |
| Yes | a `.lnx` boots through the cc65 loader, draws at 59.9 Hz; its state round-trips |
| Yes | the pad turns only when `lynx_rot_screen` asks (`0`, unset, `auto`, `180`) |

The BIOS comes only from `SLOT_LYNX_BIOS` and is copied into the test's temporary `BIOS/`. It is
never in the repo, `vendor/` or CI. Without it the three tests print `skipping: no Lynx BIOS ...`,
which `run-tests.sh` classes as a ROM skip, so CI and `SLOT_REQUIRE_CORES=1` stay green. Run them
locally with `SLOT_LYNX_BIOS=/path/to/lynxboot.img task check`.

## 8. Device gate (issue 112)

California Games, Chip's Challenge, Blue Lightning, Klax (right) and Lexis (left), 10 minutes each:
full speed, zero underruns, the measured rate per game, ms a frame; the missing-BIOS toast; the
turned-cart direction; eject and GBA.

## 9. Issue list (Phase 12)

| Issue | Title | Size | Needs the new base |
|---|---|---|---|
| 101 | Tracking | L | n/a |
| 102 | Build Beetle Lynx pinned for host and device, licence | S | No, done |
| 103 | `Platform::Lynx`, shelf, scan, LNX header, policy | M | Yes |
| 104 | BIOS check and toast | S | Yes |
| 105 | Core options: `lynx_rot_screen` always set, `lynx_force_60hz` off | S | Yes |
| 106 | 240x160 canvas at 4x, own Screen section | S | Yes |
| 107 | Pacing at the measured rate, Lynx Speed row | M | Yes, after issue 66 |
| 108 | Saves: states only | S | Yes |
| 109 | Buttons and turned carts | M | Yes |
| 110 | Tests | S | Partly: core tests done |
| 111 | Cards and labels | M | Yes |
| 112 | Device gate | S | Yes |

## 10. Integration (done 2026-10-19)

Issues 103 to 111 landed on slot main 1b20432 with the licence files moved to `licenses/`, the core
in `scripts/dist-device.sh` and `scripts/zip-check.sh` (strings pair `mednafen_lynx:Beetle.Lynx`),
`Lynx` in the zip's `games` list, and `Lynx` (ScreenScraper 28, dat `Atari - Lynx`, the CRC of the
body after the 64-byte header) in `tools/fetch-labels.py`. The maintainer picked Beetle Lynx; Handy
stays out while `lynxdec.cpp` has no licence. Issue 112, the device gate, is open.

## 11. Patches

| Patch | Issue | What |
|---|---|---|
| 0070-lynx-core-tests | 110 | Core tests (groundwork), helpers now in `tests/lynx_common` |
| 0071-platform-lynx | 103 | `Platform::Lynx`, `Core::MednafenLynx`, `slot_store::lynx` header reader, shelf, Screen section with Shader and Picture, named sites (b), (e), (g), (h) |
| 0072-lynx-bios | 104 | BIOS check in `App::insert`, the refusal toast, the one-time unknown-dump toast |
| 0073-lynx-options | 105 | `lynx_rot_screen` 0, `lynx_force_60hz` disabled, `lynx_pix_format` 16 |
| 0074-lynx-screen | 106 | Actual at 4x (180x120 window), Stretch fills |
| 0075-lynx-pacing | 107 | Measured rate, Lynx Speed row, `EmuHandle::paced_fps` |
| 0076-lynx-saves | 108 | States only, pinned by a real session test |
| 0077-lynx-rotation | 109 | Turn sources, `SET_ROTATION` 2 as a flip, Flip Right Carts row |
| 0078-lynx-carts | 111 | Generated Lynx card and its neutral |
| 0079-lynx-tests | 110 | GBA after a turned 75 Hz Lynx game equals a GBA-only run |

Host measurement of the maintainer's 88-cart set with the real boot ROM (20 s each, no input but a
START and A tap): 59.9 Hz for most; 75 Hz for Batman Returns, Checkered Flag, Desert Strike,
European Soccer Challenge, Klax, Rampart and Switchblade II; 50.1 Hz for Alien vs Predator (proto),
Daemonsgate (proto), Dinolympics, Lemmings, Lexis, Marlboro Go! (proto), Ninja Gaiden, Road Riot 4WD
(proto) and Super Off-Road; 52.6 Hz for Krazy Ace; Ishido and California Games change rate between
screens. Turned by slot: Gauntlet - The Third Encounter and Klax (right), Lexis and NFL Football
(left).
