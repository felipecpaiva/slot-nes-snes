# 0097. Bring Neo Geo, CPS1 and CPS2 into scope on one pinned FinalBurn Neo, a shelf per board, the zip as the romset

- Status: Accepted. Amends [0002](0002-cores.md), the docs/PLAN.md "Who it's NOT for" line on more systems, and the "zip ROMs" non-goal for the three arcade shelves only
- Date: 2026-10-20
- Deciders: maintainer (Felipe Paiva)
- Related: [next systems research](../research/next-systems-2026-10-20.md) sections 3, 5 and CPS3, [ADR 0059](0059-need-fullpath-load.md) (need_fullpath), [ADR 0093](0093-lynx-on-beetle-lynx.md) (the BIOS check precedent), [ADR 0096](0096-sega-32x-on-picodrive.md) (the non-commercial core precedent), issues 153 to 163, patches `0098-arcade-core-tests` to `0104-arcade-carts`

## Context

The maintainer asked for arcade: Neo Geo, CPS1 and CPS2 on FinalBurn Neo, CPS3 only if it runs at full
speed on the H700. The research of 2026-10-20 counted 153 Neo Geo games, 32 CPS1 and 38 CPS2 games in his
backup by name. Arcade differs from every shelf so far in three ways:

- **There is no cart file.** A game is a romset: a zip of the board's ROM chips, named after the set
  (`mslug.zip`). FBNeo picks the driver from the zip's base name and reads the members by CRC32 (by name
  only for a patched romset), so a set must match the pinned core's own list.
- **The picture is not the console's.** CPS boards draw 384x224, wider than the 360x240 canvas the
  Mega Drive uses, and `copy_centred` halves any frame wider than its canvas. Neo Geo draws 320x224 or
  304x224 depending on the set. Some sets are vertical: the driver draws sideways and asks the frontend
  for a quarter turn (`RETRO_ENVIRONMENT_SET_ROTATION` 1), which slot refused for every core.
- **The licence is non-commercial and forbids asking for donations** on any project using its code.

FBNeo at the pin, read in its source:

- `retro_get_system_info` sets `need_fullpath` (and `block_extract`), so ADR 0059's path-only load
  applies unchanged: slot never reads the zip, FBNeo opens it.
- It looks for a set in `<system>/fbneo/patched/` first, then the zip's own folder, then
  `<system>/fbneo/` and `<system>/` (`locate_archive`, `libretro.cpp`). The Neo Geo BIOS set
  `neogeo.zip` is found in `BIOS/` that way. A set missing a file fails to start with FBNeo's own
  message; a Neo Geo set without the BIOS still loads and draws FBNeo's 640x480 error page.
- It writes a board's NVRAM or EEPROM to `<save dir>/fbneo/<set>.nv` (Neo Geo `<set>.fs`) at unload, and
  exposes no `SAVE_RAM`. States carry everything; a state is 270 KB (CPS1) to 420 KB (Neo Geo).
- Frame rates: CPS 59.63 Hz, Neo Geo 59.18 Hz, both inside ADR 0071's window, so they run one frame a
  vsync.

## Decision

- **Scope.** Neo Geo, CPS1 and CPS2 are in scope as Phase 16, on one core. Three shelves,
  `Games/NEOGEO`, `Games/CPS1` and `Games/CPS2`, because every system here gets its own shelf and Screen
  section. `Platform::NeoGeo`, `Cps1` and `Cps2` are appended to `SHELVES`, `Core::Fbneo` to `EVERY`;
  upstream's `ALL` lists are untouched and every policy method answers the three explicitly.
- **Core pin.** libretro/FBNeo `2dbbac7623fbae1c7894a6437769e8a3adb78610` (its master on 2026-10-19,
  "Fix for arm64 builds" two commits before it), archive sha256 `8d170ae5...41c7`, FBNeo v1.0.0.03, whose
  dats (`dats/`) are the version the sets must match. Only the Neo Geo and CPS drivers are built:
  `cores/fbneo/Makefile.arcade` includes FBNeo's own `Makefile.neogeo` and `Makefile.cps12` subset
  makefiles together, `REGEN_HEADERS=1` has FBNeo's perl script write the driver list for exactly those
  sources, and `TARGET_NAME=fbneo` names the core `fbneo_libretro`. The device build is
  `platform=unix -mcpu=cortex-a53`, the C++ runtime linked statically, and `log` and `pow` bound to
  `GLIBC_2.17` (`cores/fbneo/glibc-2.17.h`, the PicoDrive header); NEEDED is `libc`, `libm`, `libpthread`.
  The host core is 10 MB, the device core 14 MB. No FBNeo source file is changed; the makefile and the
  header are public in this repository and in every release's source tarball.
- **The zip is the romset (the zip non-goal stays for every other shelf).** A shelf lists `.zip` files
  whose stem is a set of that board in the pinned core, from `slot_store::arcade`'s table
  (`arcade_sets.tsv`): board, set, parent, flags, title, 1,473 rows, written by
  `tools/arcade-sets.py` from the `BurnDriver` structs of `d_neogeo.cpp`, `d_cps1.cpp` and `d_cps2.cpp`
  at the pin, debug-only drivers, BIOS sets and the Neo Geo system drivers left out. Anything else (the
  BIOS set, a CPS1 set in `Games/CPS2`, a set of another board, a `.7z`) is logged and left off. `task
  arcade:sets:check` regenerates the table and fails on a difference, for a pin bump. slot never opens
  the zip.
- **Titles.** The table's full title names the cart, sorts the shelf and drives the letter jumps
  (`Cart::shelf_name`): `mslug.zip` is "Metal Slug - Super Vehicle-001", `ffight.zip` "Final Fight
  (World, set 1)", cleaned of its tags like every other shelf. The stem stays the set name, since FBNeo
  needs it and saves, states and labels are keyed by it.
- **Neo Geo BIOS: never shipped, never fetched, checked.** Before a Neo Geo set is inserted (from the
  shelf or resumed at boot), slot reads the zip directory of `BIOS/neogeo.zip` and launches only if it
  holds the CRCs of the four files FBNeo boots the default BIOS with: `sp-s3.sp1` (MVS Asia/Europe ver. 6,
  `0x91b64be3`), `sm1.sm1` (`0x94416d67`), `sfix.sfix` (`0xc2ea0cfd`) and `000-lo.lo` (`0x5a86cff2`),
  by CRC like FBNeo, so a set naming the first `asia-s3.rom` counts. Otherwise the set stays on the shelf
  with "Neo Geo needs BIOS/neogeo.zip". CPS1 and CPS2 need no BIOS on FBNeo (no `romof` for `sfa3` or
  `ssf2t`, no `qsound` set). The Neo Geo mode option stays DIPSWITCH, so a user who wants AES or UniBIOS
  sets it in FBNeo's terms later; slot adds no row for it.
- **Options** (`core_options_policy::FBNEO`): frameskip Auto (`fbneo-frameskip-type`, frames skipped only
  when the audio buffer runs low, so in fast-forward), diagnostic input None (FBNeo's default, Hold Start,
  opens the service menu on a held Start), Neo Geo mode DIPSWITCH, memory card off, patched romsets
  allowed. Every other key keeps FBNeo's compiled-in default: 48 kHz, 4-point interpolation, hiscores
  on (they need `hiscore.dat` in `BIOS/fbneo/`, which slot does not ship), CPU clock 100%.
- **Canvas and picture.** Neo Geo uses the Mega Drive's 360x240 canvas and follows the frame width (320
  or 304). CPS draws 384x224 on a 432x288 canvas. Picture is the Mega Drive's: Stretch by default, then
  Actual and 4:3, per board in `Config/picture.txt`.
- **Vertical games.** FBNeo asks for a quarter turn for a vertical set; slot now answers it for the
  arcade cores only (`answer_quarter_turn`) and turns the frame itself, counter-clockwise, into a 3:4
  picture in the middle of a 3:2 canvas as tall as the board's long side (576x384 for CPS), shown whole:
  360x480 on the 720x480 panel. That is **Upright**, the default. The CPS1 and CPS2 sections have a
  **Vertical Games** row (`Config/arcade.txt`): **Turned** sets FBNeo's `fbneo-vertical-mode` to
  `enabled`, so the frame stays as the board draws it, sideways and filling the panel, and slot turns the
  D-pad for a handheld held with its right edge up (Right is Up, Up is Left, Left is Down, Down is
  Right); buttons stay. Checked on the maintainer's `1941` set: turned counter-clockwise, the attract
  screen reads upright. Neo Geo's only vertical sets are homebrew, so it has no row and stands them
  upright. Every other core is still refused quarter turns.
- **Input.** slot plugs RetroPad, which FBNeo reads as its Classic device (`retro_set_controller_port_device`,
  `retro_input.cpp`). Its own map at the pin: coin on SELECT, start on START; Neo Geo A, B, C, D on B, A,
  Y, X (`RETRO_DEVICE_ID_FIRE01..04`); the six-button CPS games (CPS2 with five or more buttons, or a
  CPS1 set with three punches and three kicks) use the Street Fighter layout, punches on Y, X, L and kicks
  on B, A, R (`bStreetFighterLayout`, `RETRO_DEVICE_ID_[1-3]{ST,ND,RD}_COL_*`). So L1 and R1 belong to the
  game (`owns_shoulders` false), X and Y pass through, and the picture toggle is SELECT+X, as on Mega
  Drive.
- **Saves.** No `.sav`: FBNeo keeps the board's NVRAM and EEPROM (settings, high scores) in
  `Saves/fbneo/<set>.nv` and `.fs`, written at unload, so a crash or power cut loses what changed since
  the game started. That is settings and scores, never progress; progress is in save states, the
  resume state included. Rewind is on (the states are small), run-ahead stays gated to mGBA.
- **Screen sections.** Neo Geo: Shader, Picture. CPS1 and CPS2: Shader, Picture, Vertical Games. Shader
  is the retro list in `Config/neogeo_shader.txt`, `cps1_shader.txt`, `cps2_shader.txt`. No PAL Speed (no
  PAL boards) and no speed rows: on the host the sample rate and interpolation move the cost by less than
  the run-to-run spread (below); the device gate decides whether a row is needed.
- **Shelf objects.** Arcade has no cart, so each board gets the object its games came in that carries a
  game's art face-on, at the same fidelity as the other shells (outline, relief, lit neutral, label well,
  shadow), sourced in [docs/cart-art/ARCADE.md](../cart-art/ARCADE.md): Neo Geo the black AES cart (the
  MVS cart names its game only on a 165 x 20 mm top-edge strip), CPS2 the B-board top cover standing, in
  its region's colour read from the set's title (Japan green, Asia grey, Hispanic and Brazil orange,
  rental yellow, else blue), CPS1 the grey CPS Changer and CPS 1.5 case. Art is shown whole inside the
  well (a flyer is portrait). Every other neutral regenerates byte for byte.
- **Labels.** `tools/fetch-labels.py` asks ScreenScraper for a set by its file name under 142, 6 or 7 and
  takes the cart label scan, else the flyer, else the box front; a name search and the logo fallback go by
  the set's full title.
- **Licence.** Handled exactly like snes9x and PicoDrive: LICENSING.md names it and quotes its terms,
  `licenses/fbneo-LICENSE.txt` (FBNeo's `src/license.txt` verbatim), the MAME licence it names
  (`licenses/fbneo-MAME-license.txt`, at the MAME commit it cites), the µGUI and Source Han Sans OFL text
  FBNeo carries for its on-screen font (`licenses/fbneo-ugui-OFL.txt`), the binary-carried notices
  (`licenses/fbneo-notices.txt`) and the list of sources with no licence text all ship in
  `System/licenses/`; the pinned source ships with every release; the plugin boundary stance applies; the
  zip is never sold. **Standing rule: this project never asks for donations, anywhere** (FBNeo: "You may
  not ask for donations to support your work on any project that uses the FB Neo source code"). No link
  asking for a donation or sponsor for this project in the repository, the README, the release notes or
  the zip, and no `FUNDING.yml`. `tools/hacks.json` keeps one third-party author's Ko-fi shop as the
  download source of his hack; it is not a request for this project (it reaches the zip only inside the
  source tarball).
- **CPS3 is left out.** It is the same core but a separate SH-2 driver set; nothing in this repository can
  show it holds full speed on the H700 (the device is not part of this change, and the only evidence is
  an unopened forum claim about a Pi 3B+), and none of its six games is in the maintainer's genres. It can
  come later behind a device gate.

## Performance

Host only, a direction: M5 Max, `core_bench` on the maintainer's sets, median ms a frame over 600 frames
after 600 frames of warm-up, 3 repeats.

| Set | Board | ms a frame |
|---|---|---|
| mslug | Neo Geo | 0.21 |
| 1941 | CPS1 (vertical) | 0.22 |
| dino | CPS1 (QSound) | 0.28 |
| ddtod | CPS2 | 0.30 |

Sample rate 44.1 or 48 kHz and interpolation off or on changed these by under 2%. That is 4 to 5 times
cheaper than PicoDrive's 32X on the same host. FBNeo's own README says the core "will already run really
well on low-end devices (rpi3, ...)"; with no Cyclone on aarch64 the 68000 is the C core. We expect every
Neo Geo and CPS1/CPS2 set to hold 59.18 or 59.63 fps on the H700; the device gate measures it.

## Consequences

- Seven patches, 0098 to 0104. Nothing touches GBA, GB or GBC; the harness compare stays at 0 diffs.
- Upstream test sites take three tokens each, after the 32X's: (b) `| Platform::NeoGeo | Platform::Cps1 |
  Platform::Cps2`, (e) `| Core::Fbneo`, (g) `, "Neo Geo", "CPS1", "CPS2"`, (h) `, QuickRow::ScreenNeoGeo,
  QuickRow::ScreenCps1, QuickRow::ScreenCps2`, by the standing rule.
- The maintainer's sets must match FBNeo 1.0.0.03. The romset audit (`docs/rom-library/best-copy/`)
  says which do.
- On an FBNeo pin bump: run `task arcade:sets:check`, re-read `locate_archive`, `SetRotation` and the
  default input map, recheck the libm symbols (`task core:device:fbneo` fails otherwise), and recount
  the licence classes in LICENSING.md.
