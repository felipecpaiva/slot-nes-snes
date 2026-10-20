# Atari 2600 and Atari 7800 on slot-nes-snes: plan (2026-10-19)

"Our tree" means upstream slot main `1b20432` plus our patches (ADR 0083, the rebase). "Stella" means
libretro/stella2014-libretro at `7d1361e`, "ProSystem" libretro/prosystem-libretro at `8a88014`
(ADR 0095). No slot fork carries either system, so there is nothing to credit beyond the cores; the
seams follow the NGP, Lynx and PS1 plans. Atari ST is out of scope and not planned.

## TL;DR

- **Verdict: go, both systems, one phase (14), two shelves.** Both cores are cheap, need no BIOS,
  and fit the 360x240 canvas at 2x with one per-platform rule each.
- **Done now (groundwork, this branch):** both cores pinned and built for host and device (issues
  154 and 155), the licence record, and host tests with generated carts
  (`patches/0098-atari-core-tests.patch`, issue 171, 12 tests).
- **Facts the tests pin, which shape the integration:**
  1. The console switches are RetroPad buttons, not core options. Stella **latches** difficulty and
     Colour/B&W; ProSystem counts **every** switch only **while held**, difficulty included.
  2. ProSystem has **no High Score Cartridge** support, and its BIOS is a file-presence switch, not an
     option. With the BIOS, an unsigned cart never draws.
  3. Stella's frame is 160 columns by the game's own rows (210 by default, 250 PAL, up to 256);
     ProSystem's is 320x223 or 320x272. Both PAL heights overflow 240 rows.
- **Library:** 578 zipped 2600 dumps (559 known to Stella's database), 73 zipped 7800 dumps, all
  headerless (66 games, all 66 in ProSystem's database). Zips stay a non-goal; the unzipped-copy path
  of #147 is the way in.
- Expected size: about 16 patches. Effort M each. Value medium (2600: a big owned library).

## 1. Core choice and licences (issues 154 and 155)

| | 2600 | 7800 |
|---|---|---|
| Core | Stella 2014 (Stella 3.9.3), `stella2014` | ProSystem, `prosystem` |
| Pin | `7d1361e407e63f29e52892655069e5fb4096e691`, sha256 `c0f5e53f...` | `8a88014287c7a01cd568067e5a557d0a2b2a051f`, sha256 `23401c8b...` |
| Language | C++ (static C++ runtime on device) | C (`pow` bound to GLIBC_2.17) |
| Device `.so` | sha256 `aff1feb9e5398d7924b31ead921cca17a72efcff145c0c3dfca9d4b862a76a87`, 98 compile lines with `-mcpu=cortex-a53`, NEEDED libc | sha256 `489a6f71ff9e77d76e4105c9a19c18fe1ca9b59b2abd3b7fdf7055c507b08798`, 32 compile lines with `-mcpu=cortex-a53`, NEEDED libc, libm |
| Licence | GPL-2.0-or-later by Stella's `Copyright.txt` at `release-3.9.3` (not in the tarball, shipped by us); in-tree headers point at the bare GPL-2.0 text | GPL-2.0-or-later (31 file headers), CoreTone zlib |
| GPL-2.0-only file | none | none |
| Alternative | current libretro Stella if the 3.9.3 grant were disputed (heavier, measure first) | none in libretro |

Both device builds ran in rust:1-bullseye `sha256:4730e387...` on the X1C (arm64 under qemu),
2026-10-19. ProSystem's first device build needed `pow@GLIBC_2.29` (CoreTone's note table); the
force-included `cores/prosystem/glibc-2.17.h` fixes it the TurboGrafx-16 way.

## 2. Core facts found while testing (2026-10-19)

**Stella 2014**
- **Options:** `stella2014_color_depth`, `_palette` (standard, z26, ...), `_mix_frames` (off, mix,
  ghosting), `_low_pass_filter` and `_range`, four paddle and two Stelladaptor options. **No TV
  type, no difficulty, no region option.**
- **Input (joystick):** RetroPad B is fire, A is not (tested). L / L2 set the left difficulty to A /
  B, R / R2 the right one, L3 / R3 set Colour / Black-White: all latch (tested). SELECT is Select and
  START is the Reset switch, both momentary (tested). Y is paddle fire.
- **Picture:** `video_cb` gets `tia.width()` = 160 columns and the game's rows: 210 for a default
  NTSC cart, 250 PAL (tested); Stella's database gives 7 of his dumps 220 to 256 rows. `base_width`
  says 320 but the frame is 160. XRGB8888.
- **Timing:** 59.92 fps for a 262-line frame, 49.92 for 312 lines (auto-detected, tested); sample
  rate fixed at 31400 Hz, 524 or 629 samples a frame.
- **Saves:** none (`SYSTEM_RAM` only, 128 bytes). State 549 bytes. AtariVox/SaveKey EEPROM is not
  handled and not planned.

**ProSystem**
- **Options:** `prosystem_color_depth`, `_low_pass_filter` and `_range`,
  `_gamepad_dual_stick_hack`. **No BIOS, region or high score option.**
- **Input:** RetroPad B is button 1, A button 2; X is Reset, SELECT Select, START Pause, L and R the
  difficulty switches. Every switch is momentary (held clears its SWCHB bit, so held is B) (tested).
- **Picture:** 320x223 NTSC, 320x272 PAL (header byte 57 or the database region), XRGB8888 or
  RGB565.
- **Timing:** exactly 60 or 50 fps; sample rate two samples a scanline, 31440 Hz NTSC or 31200 Hz
  PAL, 524 or 624 a frame (tested).
- **Carts:** a headered `.a78` uses its header; a headerless one is looked up by the md5 of the
  whole file in the core's database, else treated as a plain NTSC cart (tested). All 66 of his games
  are in the database. CC2 hack images (`>>` at offset 1) are refused.
- **BIOS:** `7800 BIOS (U).rom` (`(E)` when the cart is PAL) from the system dir, if present. A real
  signed game (Asteroids, his dump) shows the logo for about 2 seconds, then plays; the synthetic
  unsigned cart never draws (tested with `SLOT_7800_BIOS`).
- **Saves:** none at this pin: no `SAVE_RAM`, no High Score Cartridge. State 49221 bytes.

## 3. Shelves, scan and headers (issues 156 and 163)

- `Games/A2600`: `.a26` and `.bin`. The scan is keyed per shelf folder, so `.bin` here never meets
  Mega Drive's `.bin` in `Games/MD`. Title from the file stem (No-Intro names). Skip nothing; 2600
  carts have no header.
- `Games/A7800`: `.a78`, headered (128 bytes, `ATARI7800` at offset 1, title at 17) or headerless
  (all of his). Title from the header when present, else the stem. Skip `[BIOS]` files and the
  `(Program)` / `Development Card` / `Diagnostic` / `High Score Cartridge` dumps by name, so the shelf
  holds games.
- Zips: unzip with the #147 path; nothing in slot opens a zip.
- Platform policy answered explicitly for both (rewind on, fast-forward on, link off, no discs).

## 4. Options and switches (issues 157, 159, 164, 165 and 167)

**2600 core options slot sets:** `stella2014_palette=standard`, `stella2014_mix_frames=disabled`
(the default; flicker blending can be a later Screen row), colour depth 24bit. Nothing else.

**2600 switches** (Stella latches, so slot only needs to send one frame of the button):
- Left and right difficulty: two Screen rows, **A / B**, default B (Stella's default). Applied at load and on change as one frame of L or L2 (R or R2).
- TV type: a Screen row **Colour / B&W**, default Colour, one frame of L3 or R3. Some games read
  the switch as a game option (which ones is unverified), so it stays reachable.
- Select and Reset stay buttons: SELECT is Select, START is Reset, momentary, as the core maps them.

**7800 options:** colour depth 24bit, low-pass off. **BIOS** row **Off / On**, default Off (no boot
delay, and homebrew works). On opens ProSystem with `BIOS/` as the system dir; Off opens it with an
empty system dir (`Saves/A7800/system`, created on demand) so the core cannot find the file
(issue 165). On with a missing or wrong file (4096 bytes, md5 above; 16384 for `(E)`) shows a toast
and boots Off. **High score cart: not offered** (no support in the core); said in the README.

**7800 switches** (ProSystem counts them only while held):
- Difficulty: two Screen rows **A / B**, default B, which slot applies by **holding** L or R every
  frame while B is chosen (held clears the bit, which is B).
- START is Pause and SELECT is Select, as the core maps them. The core puts Reset on X, but X and Y
  are turbo on the NES-like shelves, so Reset becomes an in-game menu row ("Reset console") that
  holds X for a few frames. Buttons 1 and 2 stay on B and A.

## 5. Canvas and the Screen sections (issues 158 and 166)

The panel is 720x480. Both systems use the SNES-path 360x240 canvas at 2x (ADR 0050), each with its
own rule and its own Screen section (Shader from the retro list, Picture Actual / Stretch, PAL Speed,
plus the switch rows above).

- **2600:** the copy doubles each column (160 to 320) so the picture keeps the 2600's wide pixels
  (2:1 in the canvas, 4:2 on the panel): 160x210 shows as 640x420, centred. Rows over 240 (PAL 250,
  NTSC 220 to 256 for 7 of his dumps) are **cropped to the middle 240** in Actual, never halved:
  `copy_centred` would halve them today (the tests measure on a 720x480 canvas for that reason).
  Stretch scales the frame to fill 360x240.
- **7800:** 320x223 fits as is (640x446 on the panel). PAL 272 rows: Actual crops to the middle 240, Stretch scales
  272 to 240. Whether a PAL game draws anything in the 16 cropped rows at each edge is unverified;
  the device gate looks.

## 6. Pacing (issues 160 and 168)

- 2600 NTSC at 59.92 and 7800 NTSC at 60 sit inside ADR 0071's 2 fps window: the upstream path,
  nothing to do.
- PAL: 2600 at 49.92 (30 of his dumps are Europe) and 7800 at 50 (2 dumps) take ADR 0071's paced path.
  Each Screen section gets the **PAL Speed: Native / Panel** row, stored as `a2600` and `a7800` lines
  in `Config/pal_speed.txt`.
- The 31400 Hz (Stella) and 31440 / 31200 Hz (ProSystem) sample rates go through the existing
  resampler; nothing new.

## 7. Controls (issues 159 and 167)

| Device | 2600 (Stella) | 7800 (ProSystem) |
|---|---|---|
| D-pad | joystick | joystick |
| B | fire (RetroPad B) | button 1 (RetroPad B) |
| A | fire too (slot sends RetroPad B) | button 2 (RetroPad A) |
| X, Y | turbo fire, as on NES | turbo 1 and 2 |
| SELECT | Select switch | Select switch |
| START | Reset switch | Pause switch |
| L1, R1 | slot's own (rewind, fast forward) | slot's own |
| L2, R2 | not used | not used |
| Menu rows | difficulty A/B, Colour/B&W | difficulty A/B, Reset console, BIOS |

**Out of scope at first** (issue 172), from Stella's database matched against his 559 recognised
dumps: 35 paddle games (Kaboom!, Breakout, Super Breakout, Warlords, Circus Atari, Night Driver,
Street Racer, Video Olympics, Canyon Bomber, Demons to Diamonds, Casino, Party Mix, Steeplechase,
...), 15 keypad or kids-controller games (Star Raiders, BASIC Programming, Codebreaker, Brain Games,
Hunt & Score, Alpha Beam with Ernie, Big Bird's Egg Catch, Cookie Monster Munch, Oscar's Trash Race,
...), Indy 500 (driving controller), 3 Mindlink titles and Smurfs Save the Day (Kid Vid). Omega Race
(Booster Grip) plays on the joystick. Paddles are the obvious next step: the left stick through ADR
0068 v2 and Stella's `paddle_analog_*` options. 7800 two-button games already work (B and A).

## 8. Cart art (issues 161 and 169)

- ScreenScraper ids from Skyscraper's `platforms_idmap.csv` at
  [c253bfe](https://github.com/Gemba/skyscraper/blob/c253bfe0ea359aa4272f47694bd601bd53205d2b/platforms_idmap.csv):
  rows `atari2600,26,28,22` and `atari7800,41,34,27` (folder, ScreenScraper, MobyGames, TheGamesDB).
- Dats: libretro-database `metadat/no-intro/Atari - 2600.dat` and `Atari - 7800.dat` (checked at
  `12c21cf`). The 7800 dat lists headerless `.bin` CRCs (Asteroids (USA) `DFB93F40`, equal to his
  dump), so `fetch-labels.py` hashes the body without the 128-byte header when one is present.
- Cards: 2600 carts in the silver-label / picture-label / Activision shapes as a retro bitmap card;
  7800 the taller ProSystem-era shell. Label scans first, box art as the fallback, like SMS.

## 9. Tests and CI (issue 171)

`atari_core.rs` (patch 0098), 12 tests, all with generated carts and no ROM:

| System | Test |
|---|---|
| 2600 | NTSC cart: 160x210, 59.92 fps, 31400 Hz, 524 samples, audible tone |
| 2600 | 312-line cart is PAL: 160x250, 49.92 fps, 629 samples |
| 2600 | state round-trip, no save RAM |
| 2600 | difficulty and Colour/B&W latch; Select and Reset momentary |
| 2600 | right difficulty latches on R and R2 |
| 2600 | fire is RetroPad B, not A |
| 7800 | headered NTSC cart: 320x223, 60 fps, 31440 Hz, 524 samples |
| 7800 | header says PAL: 320x272, 50 fps, 31200 Hz, 624 samples |
| 7800 | headerless unknown dump runs as NTSC |
| 7800 | state round-trip, no save RAM |
| 7800 | every switch momentary, difficulty included |
| 7800 | with the NTSC BIOS (`SLOT_7800_BIOS`) an unsigned cart never draws; else a BIOS skip |

The platform half (scan, canvas rules, switch rows, `atari_then_gba.rs` after the PS1 and NGP
pattern) grows with each step.

## 10. Device gate (issues 162 and 170)

2600: Pitfall!, River Raid, Space Invaders, Yars' Revenge, Solaris, one PAL dump, 10 minutes each;
7800: Asteroids, Ms. Pac-Man, Food Fight, Ninja Golf, one PAL dump, BIOS Off and On. Full speed,
zero underruns, ms a frame for the PERFORMANCE.md rows, the crop rows on PAL, eject and GBA.

## 11. Issue list (Phase 14)

| Issue | Title | Size | Needs integration |
|---|---|---|---|
| 153 | Tracking | L | n/a |
| 154 | Build Stella 2014, licence | S | No, done |
| 155 | Build ProSystem, licence | S | No, done |
| 156 | `Platform::A2600`, shelf, scan | M | Yes |
| 157 | 2600 core options | S | Yes |
| 158 | 2600 canvas and Screen section | M | Yes |
| 159 | 2600 controls and switch rows | M | Yes |
| 160 | 2600 PAL pacing | S | Yes, after issue 66 |
| 161 | 2600 carts and labels | M | Yes |
| 162 | 2600 device gate | S | Yes |
| 163 | `Platform::A7800`, shelf, scan, header | M | Yes |
| 164 | 7800 core options, no high score cart | S | Yes |
| 165 | 7800 BIOS row and check | S | Yes |
| 166 | 7800 canvas and Screen section | S | Yes |
| 167 | 7800 controls and switch rows | M | Yes |
| 168 | 7800 PAL pacing | S | Yes, after issue 66 |
| 169 | 7800 carts and labels | M | Yes |
| 170 | 7800 device gate | S | Yes |
| 171 | Tests | S | Partly: core tests done |
| 172 | DEFERRED: paddles, keypads and other controllers | L | Later |

## 12. What remains for integration

Issues 156 to 170 and the platform half of 171. When a platform patch lands: that core's licence
files move from `cores/<core>/` to `licenses/`; the core joins `scripts/dist-device.sh` and
`scripts/zip-check.sh`; the shelf joins the `games` list. Issue, ADR, phase and patch numbers
(153 to 172, 0095, Phase 14, 0098) were renumbered past main on the rebase onto it and may move again at
merge. `cores/lib.sh`'s `device_include` hook is the TurboGrafx-16 branch's hunk, byte for byte, so
the two merge cleanly.
