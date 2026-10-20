# slot-nes-snes

More systems for [slot](https://github.com/BrandonKowalski/slot) on the Anbernic RG34XXSP (H700):
NES, SNES, Master System, Game Gear, Mega Drive, Sega 32X, PlayStation, TurboGrafx-16 and PC Engine,
WonderSwan and WonderSwan Color, Atari Lynx, NeoGeo Pocket and Pocket Color, Atari 2600 and 7800, Virtual
Boy, the Neo Geo, CPS1 and CPS2 arcade boards, and the PC Engine SuperGrafx, beside slot's own
GBA, GB and GBC. It is a patch set applied to slot's source at a pinned upstream commit. Each new
system gets its own shelf, cores, saves and settings, the same way slot treats GBA, GB and GBC, and
GBA, GB and GBC stay byte-identical to upstream.

> [!IMPORTANT]
> This is **not** part of slot, and it is not endorsed by its author. slot is Game Boy-centric by
> design, and its author has said plainly that slot will not add more systems
> ([#30](https://github.com/BrandonKowalski/slot/issues/30#issuecomment-6091021879)). That decision
> is respected here: nothing in this repo asks slot to change.
>
> **Please do not report bugs from this patch set to slot's tracker.** Open them here.

The pinned base is slot main `1b20432`, the coming 1.8.0 with no tag yet (`SLOT_PIN`, ADR 0083).
Releases are named after it: `main-1b20432-ns.1` is the first.

## Systems

| Shelf | Folder | File types | Core | BIOS | Status |
|---|---|---|---|---|---|
| GBA, GB, GBC | `Games/GBA`, `Games/GB`, `Games/GBC` | as slot | mGBA, gpSP (slot's own) | as slot | unchanged from upstream |
| NES | `Games/NES` | `.nes` | fceumm, or nestopia | none | device tested |
| SNES | `Games/SNES` | `.sfc`, `.smc` | snes9x, or snes9x2005_plus | none | device tested |
| Master System | `Games/SMS` | `.sms` | Genesis Plus GX | none | device tested |
| Game Gear | `Games/GG` | `.gg` | Genesis Plus GX | none | device tested |
| Mega Drive | `Games/MD` | `.md`, `.gen`, `.bin` | Genesis Plus GX | none | provisional, heavy-title gate open |
| Sega 32X | `Games/32X` | `.32x`, `.bin` with a 32X header | PicoDrive | none | device gate pending |
| PlayStation | `Games/PS1` | `.chd`, `.cue`, `.pbp`, `.m3u` | pcsx_rearmed | optional, your own `scph5501.bin` or similar | device tested (CTR, Spyro) |
| TurboGrafx-16, PC Engine | `Games/TG16` | `.pce` | Beetle PCE Fast | none (HuCards only) | device gate pending |
| WonderSwan, WonderSwan Color | `Games/WS` | `.ws`, `.wsc` | Beetle Cygne | none | device gate pending |
| Atari Lynx | `Games/Lynx` | `.lnx`, `.lyx` | Beetle Lynx | **required**, your own `lynxboot.img` | device gate pending |
| NeoGeo Pocket, Pocket Color | `Games/NGP` | `.ngp`, `.ngc`, `.ngpc` | Beetle NeoPop | none | device gate pending |
| Atari 2600 | `Games/A2600` | `.a26`, `.bin` | Stella 2014 | none | device gate pending |
| Atari 7800 | `Games/A7800` | `.a78` (headered or not) | ProSystem | optional, your own `7800 BIOS (U).rom`, off by default | device gate pending |
| Virtual Boy | `Games/VB` | `.vb`, `.vboy` | Beetle VB | none | device gate pending |
| Neo Geo | `Games/NEOGEO` | `.zip` romsets (FinalBurn Neo sets) | FinalBurn Neo | **required**, your own `neogeo.zip` | device gate pending |
| Capcom CPS1 | `Games/CPS1` | `.zip` romsets (FinalBurn Neo sets) | FinalBurn Neo | none | device gate pending |
| Capcom CPS2 | `Games/CPS2` | `.zip` romsets (FinalBurn Neo sets) | FinalBurn Neo | none | device gate pending |
| PC Engine SuperGrafx | `Games/SGX` | `.sgx`, `.pce` | Beetle SuperGrafx | none | device gate pending |

"Device gate pending" means the system passes its host tests and runs on the device, but the full
speed and audio gate in [docs/DEVICE-GATE.md](docs/DEVICE-GATE.md) has not been run on it yet.

### BIOS files

No BIOS ships in the zip and none is ever fetched. Put your own dumps in `BIOS/` on the SD card.

- **PlayStation:** optional. pcsx_rearmed looks for `scph5500.bin`, `scph5501.bin`, `scph5502.bin`,
  `scph101.bin`, `scph7001.bin` and `scph1001.bin`, and uses its own HLE BIOS when none is there.
  A real BIOS is more compatible.
- **Atari Lynx:** required. `BIOS/lynxboot.img`, 512 bytes. Without it the cart stays on the shelf
  and slot says "Lynx needs BIOS/lynxboot.img" (a 0-byte placeholder counts as missing). A 512-byte
  file that is not the known dump still launches, with a one-time toast.
- **Atari 7800:** optional and off by default. With the BIOS row On (7800 Screen section), ProSystem
  loads `BIOS/7800 BIOS (U).rom` (`(E)` for a PAL cart) and shows the Atari logo before a signed game;
  an unsigned cart (homebrew) does not boot with it. Off hides the file from the core.
- **Neo Geo:** required. `BIOS/neogeo.zip`, the FinalBurn Neo BIOS set. slot checks that it holds the
  MVS Asia/Europe ver. 6 BIOS and the three shared files (`sp-s3.sp1` or `asia-s3.rom`, `sm1.sm1`,
  `sfix.sfix`, `000-lo.lo`, matched by CRC); without them a Neo Geo set stays on the shelf and slot says
  "Neo Geo needs BIOS/neogeo.zip". CPS1 and CPS2 need none.
- **Every other new system:** none.

A file whose name starts with `[BIOS]` (a System Card, a boot ROM, any No-Intro or Redump firmware
dump) is never shown as a cart on any shelf, so a ROM set copied in whole stays clean.

### Notes per system

- **NES.** fceumm by default, nestopia in the core picker. NES and Famicom cart shells by region.
  L1 cycles Crop, Stretch and 4:3, R1 is Actual.
- **SNES.** snes9x by default, snes9x2005_plus for heavy titles. SNES and Super Famicom shells from
  the header region. L and R belong to the game, so the picture toggle is SELECT+X (Crop, Stretch,
  Actual, 4:3).
- **Master System and Game Gear** play like NES (X and Y are turbo, START is Pause on Master System).
  Game Gear is drawn at 3x like Game Boy and adds the LCD3x filter. Master System shows the whole
  front box, and its Region row (Auto, Japan, USA, Europe) runs European carts the core does not
  know at 50 Hz.
- **Mega Drive** plays like SNES: a six-button pad (SELECT is MODE), SELECT+X for the picture, and Stretch follows the game's 256 or 320 wide frame.
- **Sega 32X** plays like Mega Drive, on its own shelf. A `.32x` always lists; a `.bin` lists only if
  its header says 32X, because `.bin` is also a Mega Drive extension. The Mega Drive shelf stays on
  Genesis Plus GX, so a 32X game left in `Games/MD` does not run: move it to `Games/32X`. Its Screen
  section has Renderer (Accurate, Good, Fast) and Sound Rate (44 kHz, 22 kHz) rows for heavy titles.
- **PlayStation.** Jewel cases with cover art (US, EU and JP styles, a double case for multi-disc);
  the case opens and the disc slides in with its label. 640x480 picture, disc swap on SELECT+L2,
  one memory card per game (`Saves/PS1/<stem>.srm`, shared by a multi-disc `.m3u`), DualShock
  sticks, and L1, R1, L2 and R2 go to the game. SELECT+R2 toggles fast-forward.
- **TurboGrafx-16 and PC Engine** play like Game Gear: B is II, A is I, START is Run, X and Y are
  turbo. Picture is Crop by default (8 lines off the top and bottom), then Stretch and Actual. Every
  HuCard keeps a 2 KB `.sav`. CD games are out of scope; SuperGrafx cards have their own shelf.
- **PC Engine SuperGrafx** has its own shelf, `Games/SGX`, on Beetle SuperGrafx: the five SuperGrafx
  HuCards (`.sgx`) and the PC Engine cards with SuperGrafx enhancements (Darius Plus and Darius Alpha,
  `.pce`), every one run on the SuperGrafx hardware. It plays and saves like the TurboGrafx-16 (B is II,
  A is I, START is Run, X and Y are turbo, a 2 KB `.sav` per card); Picture is Crop by default, then
  Stretch, Actual and 4:3. The Pad row switches to the 6-button pad (III and IV on Y and X, V and VI
  on L1 and R1, the picture toggle on SELECT+X) from the next start. A SuperGrafx card is drawn as a Super HuCard, its label the other way up
  from a standard HuCard's. A `.pce` card on the TG16 shelf stays a TurboGrafx-16 game.
- **WonderSwan and WonderSwan Color.** Horizontal games are drawn at 3x, vertical ones upright at
  2x, read from the cart's own footer; a SELECT tap turns a vertical game sideways and back. 60 Hz by
  default, and the Refresh row switches to the native 75 Hz.
- **Atari Lynx.** The 160x102 picture at 4x or stretched. Each game runs at the rate it programs (most
  at 59.9 Hz, some at 75 or 50). Carts made to be held sideways keep the picture as drawn, and Flip
  Right Carts (on by default) turns right-handed ones so every turned cart is held the same way.
  `Config/lynx_rotation.txt` (`<stem> = left`, `right` or `none`) overrides the pick.
- **NeoGeo Pocket and Pocket Color.** One shelf, the 160x152 screen at 3x. The game's saves live in
  the cart's flash, which slot checks before the core reads it and writes atomically at every lid
  close, POWER tap, autosave and eject, in `Saves/NGP/<game>.flash`.
- **Atari 2600.** Joystick on the d-pad, fire on A or B (the left stick turns paddles in paddle
  games, which also fire on A or B), SELECT is Select and START is Reset. L1 and R1 stay slot's. The
  console switches are rows in the 2600 Screen section: Left and Right Difficulty (Auto, A, B) and TV
  Type (Auto, Colour, B&W). Auto sends nothing, so a game starts with Stella's default for it, and a
  switch set to A or B stays there in Stella until the game is started again. 4:3 by default, 2600
  pixels kept wide. Keypad, driving and Mindlink games are not supported. Saves are save states only.
- **Atari 7800.** B is button 1, A button 2, X is Reset, SELECT is Select and START is Pause. Left and
  Right Difficulty rows (B and A by default, ProSystem's own choice), and a BIOS row. No High Score
  Cartridge (ProSystem has none), so saves are save states only.
- **Virtual Boy.** One flat picture: the left eye in red on black, 384x224 at 1.875x (720x420), or
  stretched to the panel. The Palette row swaps the red for white, blue, cyan, electric cyan, green,
  magenta or yellow. The D-pad is the left D-pad and the right analog stick is the right D-pad; the
  Right Pad row's ABXY choice puts the right D-pad on X, A, B and Y (A and B move to R2 and L2), for
  games such as Red Alarm and Teleroboxer that use it as buttons. Games run at their own 50.27 Hz.
  Every cart keeps a 64 KB `.sav` in `Saves/VB`.
- **Neo Geo, CPS1 and CPS2** run on FinalBurn Neo, one shelf per board. The zip is the romset, named
  as the set (`mslug.zip`, `ffight.zip`, `ssf2t.zip`), for the pinned FinalBurn Neo (dat 1.0.0.03):
  a zip that is not a set of that board is left off the shelf, and an older MAME set may lack a file
  (FinalBurn Neo then shows which one). The shelf shows each game's full title. SELECT is Coin and START
  is Start. Neo Geo A, B, C, D are on B, A, Y, X; the six-button CPS games have the punches on Y, X, L1
  and the kicks on B, A, R1 (FinalBurn Neo's own Street Fighter layout), so L1 and R1 belong to the game
  and the picture toggle is SELECT+X. Vertical games (1941, Varth, 19XX...) stand upright in the
  middle of the screen; the CPS Vertical Games row turns them sideways at full size, with the D-pad
  turned for a handheld held with its right edge up. On the shelf a Neo Geo game is a black AES cart, a
  CPS2 game its B-board case in its region's colour (Japan green, USA and Europe blue, Asia grey), and a
  CPS1 game the grey CPS Changer case, each with the game's art from the label fetcher. The board's own settings and high scores
  (`Saves/fbneo/`) are written when the game closes; progress mid-game is in save states. CPS3 is not
  included.

### The Screen page

Every system has its own section on the Screen page, and its own rows in the in-game Screen page.

| Row | Systems | Values |
|---|---|---|
| Shader | every new system | Off, Grid, Dot, Sharp, Scanlines, crt-pi, crt-1tap, Line, Pixel (Game Gear adds LCD3x) |
| Picture | every new system | Crop (NES, SNES, TurboGrafx-16, SuperGrafx), Stretch, Actual, 4:3 (NES, SNES, Master System, Mega Drive, 32X, Neo Geo, CPS1, CPS2, SuperGrafx, Atari 2600 and 7800, where it is the default) |
| PAL Speed | NES, SNES, Master System, Mega Drive, 32X, PlayStation, Atari 2600 and 7800 | Native (50 Hz, the default) or Panel (60 Hz, about 20% fast) |
| Region | Master System | Auto, Japan, USA, Europe |
| Renderer, Sound Rate | 32X | Accurate, Good, Fast; 44 kHz, 22 kHz |
| Refresh | WonderSwan | 60 Hz, 75 Hz |
| VB Speed | Virtual Boy | Native (50.27 Hz, the default) or Panel |
| Palette | Virtual Boy | Red (the default), White, Blue, Cyan, Electric Cyan, Green, Magenta, Yellow |
| Right Pad | Virtual Boy | Stick (the default) or ABXY |
| Speed | Lynx | Native, Panel |
| Left, Right Difficulty; TV Type | Atari 2600 | Auto, A, B; Auto, Colour, B&W |
| Left, Right Difficulty; BIOS | Atari 7800 | B, A; Off, On |
| Vertical Games | CPS1, CPS2 | Upright (the default), Turned |
| Pad | SuperGrafx | 2 Buttons (the default), 6 Buttons |

What you pick in a row becomes that system's default from the next game. A cart's own picture
setting still wins for that cart. 4:3 draws the picture at a TV's aspect, 640x480 centred.

## What else changes from plain slot

- **Cart art.** Every cart is a generated shell coloured the slot way, faced with the real printed
  label you fetch with the label fetcher (below). Nothing is ever a screenshot.
- **Crash guard.** A game that crashed slot while it started is kept on the shelf on the next boot
  with a "Last start failed" banner, instead of resuming into a boot loop. Tap A to resume, hold A
  to start clean. Nothing is deleted.
- **Fast shelf scroll.** Holding Left or Right on a long shelf moves 3 carts at a time after about 2
  seconds, drawing placeholders instead of waiting for cart faces. Measured on a 1014-cart shelf:
  p99 frame time 17 ms, no empty frames.
- **CPU row.** General gains a CPU row: Performance (the default, every measurement here) or
  Balanced (the `schedutil` governor, saves battery, heavy games may miss frames).
- **Shelf order.** General gains a Shelf Order row: Classic (the default, the usual order) or
  Release Year, which puts the system shelves after Recents and Favorites in the order the
  platforms first came out, from Atari 2600 (1977) to Game Boy Advance (2001), and lists the
  systems on the Screen page in the same order. It applies at once and is saved as
  `order = release-year` in `Config/shelf_order.txt` (ADR 0100).
- **PAL games at 50 Hz.** A core more than 2 fps from 60 runs at its own speed and pitch. PAL Speed:
  Panel brings back the old 60 Hz.
- **No audio stall at game start.** The audio device stays open while a game feeds it.
- **Each shelf remembers its own cart**, not only the last shelf.
- **Settings > Screen scrolls**, so every system's section stays above the legend.
- **Battery saves are kept when the core gives no state**, on resume, eject and autosave.
- **Cart faces stay on the right cart** after a favourite toggle or a restock.
- **Battery Low banners** at 15% and at 10%, once per discharge.
- **The display rests while dozing**: two dark frames, then no drawing until the lid opens.
- **Volume HUD on a silent start**, so a muted game is not taken for a broken core.
- **Up and Down** move through the save state switcher.

## Known gaps

- SNES hi-res frames (512 wide, a few titles) are blended 2:1 and lose detail.
- No colour correction on the new systems: SELECT+Y does nothing there and the Color Correction and
  Palette rows are hidden.
- Mega Drive is a provisional go until its heavy-title device gate (Virtua Racing, Sonic 3D Blast,
  Street Fighter II SCE, Thunder Force IV) passes. A Game Gear game that runs in Master System mode
  is cropped to the 240x160 Game Gear canvas.
- Sega 32X: the polygon games (Virtua Racing Deluxe, Star Wars Arcade, Virtua Fighter) are expected
  to sit near the frame budget on the H700. If one misses frames, set Renderer to Fast and then Sound
  Rate to 22 kHz in the 32X Screen section. The device gate (issue 152) is still open.
- Virtual Boy: one eye only, so there is no depth. In ABXY mode L2 and R2 belong to the game, so
  there is no rewind button and fast-forward is SELECT+R2. The device gate (issue 182) is still open.
- PC Engine SuperGrafx: with the 6-button pad turbo is off and L1 and R1 belong to the game. Beetle
  SuperGrafx has no frameskip, so fast-forward is slower than on the TurboGrafx-16. The device gate (issue 199) is
  still open.
- PlayStation: no rewind (states are 4.4 MB) and no fast-forward gesture on L2 or R2, which belong to
  the game. L3 and R3 are not mapped, and which physical stick is left is not verified yet.
- Atari Lynx: save states only. Beetle Lynx has no EEPROM emulation at the pinned commit, so the few
  carts that save to an EEPROM keep progress only through the resume state and save states.
- Atari 2600 and 7800: a PAL game is shown at the NTSC picture height in 4:3 and Stretch (the middle
  210 or 223 rows); Actual shows the whole PAL frame. Keypad, driving and Mindlink 2600 games are not
  supported. The device gates (issues 162 and 170) are still open.
- At Native PAL speed, a 50 fps game on the 59.6 Hz panel repeats about one frame in six.
- Settings keyed only by file name collide if the same name exists on two systems.
- Zip ROMs are not supported.

More in [docs/QUALITY-BAR.md](docs/QUALITY-BAR.md#known-gaps-not-hidden).

## Install

Download `slot-nes-snes-<release>-h700.zip` from the
[releases page](https://github.com/felipecpaiva/slot-nes-snes/releases).

1. Unzip it. It holds one folder of the same name.
2. Copy the contents of that folder (`System/`, `BIOS/`, `Config/`, `Games/` and the rest) onto the
   root of the SD card, merging with what is there.
3. Put games in the folders from the [Systems](#systems) table, and any BIOS files in `BIOS/`.
4. Boot the device.

### Update

1. Delete `System/` from the SD card.
2. Copy the new `System/` from the zip in its place.
3. Keep `Config/`, `Saves/` and `States/`: they hold your settings, saves and save states.

### Going back to stock slot

It is safe. Stock slot does not scan the new folders, so a new-system cart left in the slot boots to
an empty slot. No file is deleted. `sh scripts/check-downgrade.sh` runs this case against the
upstream tree.

### Expansion Card

A device with two TF slots (the RG34XXSP has them) can keep whole systems on a second card. The card
in TF1 (the **Base System card**, the one BaseOS runs from) stays the main card: carts, `Saves/`,
`States/`, `Config/`, `Labels/`, `BIOS/` and `System/` all stay on it. The card in TF2 (the
**Expansion Card**) holds only the game folders of the systems you move there, for example
`Games/PS1/`. At launch `System/expansion.sh` mounts it at `/mnt/expansion` and binds each listed
folder onto `Games/<SYS>` of the main card, so slot sees one `Games/` tree (ADR 0098).

Prepare the card on a Mac (or on Linux with `--disk /dev/sdX`). BaseOS mounts the first partition of
TF2 as the main card whenever anything there mounts, so the tool makes that partition 16 MiB of
zeros and puts the games on a second, exFAT partition named `EXPANSION`. It erases the whole disk, so
it refuses unless the identifier, the exact size in bytes and a current volume name all match, and
without `--yes` it only prints its plan:

```sh
diskutil info disk4 | grep "Disk Size"            # the size in bytes
python3 tools/expansion-card.py --disk disk4 --size 255869321216 --label MuOs --systems PS1
sudo python3 tools/expansion-card.py --disk disk4 --size 255869321216 --label MuOs --systems PS1 --yes
```

On macOS the tool runs one `diskutil partitionDisk -noEFI` for the table and the exFAT partition,
zeroes p1 and reads it back. It prints `ok:` for each step it ran; if one fails it says whether the
card was touched yet. A card left half done is not for the device: run the tool again with the label
it now shows (`diskutil list`). Take the card out and put it back first after a failed run, so macOS
reads its table again.

Then copy the games into `Games/PS1/` on `EXPANSION` (run `dot_clean -m /Volumes/EXPANSION` after a
Finder copy) and list the moved systems in `Config/expansion.txt` on the main card, one folder name
per line. `#` starts a comment:

```
# Systems on the Expansion Card
PS1
```

- **Without the Expansion Card** the base card's own folders show, as before. A listed system's shelf
  is whatever the base card holds (usually nothing), and a seated game from it is not resumed. The
  launch waits at most one second for a late card and writes every step to `Logs/slot-session.log`.
- **Files under a moved folder on the base card are hidden** while the Expansion Card is in, and
  still take space there. The session log says so when it finds any. Once the games play from the
  Expansion Card, delete the old copies from the base card (with the Expansion Card out, or from a
  computer) to get the space back.
- **Saves, states and labels of moved systems stay on the main card**, so a game keeps its saves when
  the Expansion Card is swapped.
- **USB storage mode** (hold MENU at power on) exports TF2 when a card is in it, so you get the
  Expansion Card. Take it out to reach the main card over USB.
- **Card repair** checks the main card only. It unmounts the Expansion Card folders first.
- **The tools** see the same paths over adb (`--device`). With the main card mounted on a Mac, pass
  the Expansion Card too: `--card /Volumes/SLOT --expansion /Volumes/EXPANSION`. Without it they stop
  (or skip that system) and say why. They never read the empty folder as no games.

### Building from source

```sh
brew install mise colima docker
mise trust && mise install   # in the repo: rust, task, cmake, adb
colima start
task zip                     # the release zip in build/, then: sh scripts/zip-check.sh <zip>
task deploy:device           # optional: push System/ over adb and reboot; task log:device reads slot.log
```

`task zip` fetches the slot source named in `SLOT_PIN` (checked by sha256), applies `patches/`,
builds slot and every core for the device, and bundles the corresponding source. Details are in
[CONTRIBUTING.md](CONTRIBUTING.md) and [docs/SUPPLY-CHAIN.md](docs/SUPPLY-CHAIN.md).

## Tools on the Mac

Both are python3 standard library only and work on the card inside the device (`--device`, over
adb) or on a mounted card (`--card <root>`).

### Cart labels: `tools/fetch-labels.py`

Puts the real printed label on every cart of every shelf, the front box on Master System, and the
front cover and disc label on PlayStation. Each ROM is matched by CRC32 against the libretro
databases, never by name. Sources: Brandon Kowalski's art set at art.slot-cfw.fyi (GBA, GB, GBC),
then ScreenScraper.

```sh
task labels:fetch -- --device --library ~/ROMS --limit 5 --dry-run   # look first
task labels:fetch -- --device --library ~/ROMS                        # the lot
task labels:fetch -- --device --library ~/ROMS --by-name              # games no CRC finds
task labels:logo-tool                                                 # once, for --logo-fallback
task labels:fetch -- --device --library ~/ROMS --by-name --logo-fallback
```

`--by-name` (opt in) gives art to games whose CRC is in no database: a same-title sibling's label on
the card, then the front box, then a ScreenScraper name search taken only on a single confident
match. `--logo-fallback` is the last resort: the game's logo (libretro `Named_Logos`, or the
ScreenScraper wheel of a game already matched by name) drawn on a plain ground in the style of Cart
Studio's Logo Only. See [docs/cart-art/BY-NAME.md](docs/cart-art/BY-NAME.md).

ScreenScraper needs `SS_DEVID` and `SS_DEVPASSWORD` (and your own `SS_SSID`, `SS_SSPASSWORD`) in
the environment. They are never committed and never printed. Fetched art is cached on your machine
and never committed.

### ROM hacks: `tools/hacks.py`

Checks the hacks on the card against their latest releases, updates them, and installs new ones.
The patch (BPS, IPS, UPS, xdelta or PPF) is applied in pure Python to the clean base ROM found in
your library by CRC32, and checked by CRC.

```sh
task hacks:check -- --device --library ~/ROMS                                      # read only
task hacks:update -- --device --library ~/ROMS --update pokemon-unbound --dry-run  # look first
task hacks:update -- --device --library ~/ROMS --update pokemon-unbound            # asks before writing
task hacks:update -- --device --library ~/ROMS --rollback pokemon-unbound
task hacks:update -- --device --library ~/ROMS --add castlevania-2-retranslation   # a new hack, next to its original
task hacks:update -- --device --init                       # write ~/.config/slot-nes-snes/hacks.json
task hacks:update -- --device --migrate-backups --dry-run  # move card backups to the backups folder
```

- An update goes in under the same file name, so the battery save, label and settings stay. Every
  save state of that game is moved to the backup, since an old state can crash a new version.
  `--rollback` brings everything back. Nothing is deleted.
- `--add <id>` installs a registry hack as a new game next to its original, which is only read. It
  refuses a duplicate by name or CRC.
- **PS1 disc patching.** PPF patches go onto track 1 of a `.chd` through `chdman` (extract, check
  track 1 against the redump CRC, patch, rebuild, extract again and compare).
- **Backups off the card.** By default the old version is kept in `Backups/hacks/` on the card. The
  `backups` setting in `hacks.json` (or `--backups <folder>` for one run) keeps it in a folder on the
  Mac instead, such as a backup drive. Every copy is checked by size and CRC32 before anything is
  removed from the card, and an unreachable folder refuses before any write; the tool never falls
  back to the card on its own. `--migrate-backups` moves the card's existing backups there.

The registry is `tools/hacks.json`, with your own `hacks.json` read on top. See
[docs/HACKS.md](docs/HACKS.md).

## How it is built and kept honest

- **A patch set on a pinned upstream.** `SLOT_PIN` names the slot commit and every core commit, each
  with its sha256. `patches/` applies in order, one concern per patch. Each upstream release is a
  rebase ([docs/REBASE.md](docs/REBASE.md)).
- **Upstream first.** A fix that belongs in slot also goes to slot as a pull request, and our patch
  is dropped once upstream ships it.
- **Upstream tests stay unmodified**, except at a few named sites, each checked exactly by
  `scripts/check-upstream-tests.sh`.
- **GBA does not change.** `task harness:compare` must show 0 differing GBA, GB and GBC frames
  against unpatched slot, and `task bench:compare` keeps the GBA frame cost within 2%.
- **A device gate.** Full speed and no audio underruns are measured on a real RG34XXSP, and the
  results live in [docs/DEVICE-GATE.md](docs/DEVICE-GATE.md).

Rules: [CONTRIBUTING.md](CONTRIBUTING.md). Decisions: [docs/DECISIONS.md](docs/DECISIONS.md).

## Licences

slot is GPL-3.0-or-later, so this patch set is too ([LICENSE](LICENSE)). fceumm as shipped is
GPL-3.0-or-later, nestopia and pcsx_rearmed are GPL-2.0-or-later, and the Beetle cores (PCE Fast,
Cygne, Lynx, NeoPop) are Mednafen's GPL code. Every release carries the complete corresponding
source in `System/licenses/`.

> snes9x, snes9x2005_plus, Genesis Plus GX, PicoDrive and FinalBurn Neo are licensed for non-commercial
> use only and are not GPL. This release includes them, with their licences in
> System/licenses/snes9x-LICENSE.txt, System/licenses/snes9x2005-LICENSE.txt,
> System/licenses/genesis_plus_gx-LICENSE.txt, System/licenses/picodrive-LICENSE.txt and
> System/licenses/fbneo-LICENSE.txt. Do not sell this zip or bundle it with anything that is sold. This
> project never asks for donations.

Each core is loaded at run time across the libretro C ABI and is a separate program; the zip is an
aggregate of separate works, each under its own licence. That is our reading, not legal advice.
Details per core: [LICENSING.md](LICENSING.md).

## Credits

- All of the hard work is Brandon Kowalski's [slot](https://github.com/BrandonKowalski/slot). Go
  star it. Its Cart Studio's Logo Only style is the basis of the logo fallback.
- Markus (@MarkusMaribu) painted the GBA cart lighting our cart shells are measured from.
- Code ideas from other GPL-3.0 slot forks, reimplemented and credited in each patch:
  AaronC1990/tray, bently0602/slot, oauramos/omega-zero, cloudwithax/unslot, nelynes/slotPlus,
  suprsomething/slot.advance, marghost/slot_modded, jgraving/slot and pvaibhav/slot.
- Art comes from [ScreenScraper](https://www.screenscraper.fr) (CC BY-NC-SA) and its contributors,
  and game data from the libretro-database dats (CC BY-SA 4.0) and libretro-thumbnails. It is
  fetched on your machine for your own device. Do not redistribute it.

## Docs

| Doc | What it holds |
|---|---|
| [docs/PLAN.md](docs/PLAN.md) | The phased build plan, with tests per phase |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Every binding decision, as ADRs in [docs/adr/](docs/adr/README.md) |
| [docs/QUALITY-BAR.md](docs/QUALITY-BAR.md) | What "done" means, and the known gaps |
| [docs/DEVICE-GATE.md](docs/DEVICE-GATE.md) | Device results on the RG34XXSP |
| [docs/PERFORMANCE.md](docs/PERFORMANCE.md) | Frame cost, fast-forward and rewind per system |
| [docs/HACKS.md](docs/HACKS.md) | The ROM hack tool |
| [docs/cart-art/](docs/cart-art/VARIANTS.md) | Cart, box and jewel case research, and labels by name |
| [docs/REBASE.md](docs/REBASE.md) | Rebasing onto a new slot release |
| [docs/UPSTREAM-TOUCHPOINTS.md](docs/UPSTREAM-TOUCHPOINTS.md) | Every place a patch changes an upstream file |
| [docs/SUPPLY-CHAIN.md](docs/SUPPLY-CHAIN.md) | Every download in the build and its check |
| [docs/research/fork-review-2026-10-18.md](docs/research/fork-review-2026-10-18.md) | What we took from other slot forks, and what we skipped |
| [LICENSING.md](LICENSING.md) | Licences of slot, every core and every asset |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Code standards and the pull request checklist |
