# slot-nes-snes

NES and SNES shelves for [slot](https://github.com/BrandonKowalski/slot), as a patch set on top of
slot's own releases.

> [!IMPORTANT]
> This is **not** part of slot, and it is not endorsed by its author. slot is Game Boy-centric by
> design, and its author has said plainly that slot will not add more systems
> ([#30](https://github.com/BrandonKowalski/slot/issues/30#issuecomment-6091021879)). That decision
> is respected here: nothing in this repo asks slot to change.
>
> **Please do not report bugs from this patch set to slot's tracker.** Open them here.

## What it does

The pinned base is slot v1.7.0 (`SLOT_PIN`, rebased from v1.6.0 on 2026-10-15, ADR 0038).

slot keeps GBA, GB and GBC on their own shelves, each with its own cores and settings. This patch
set adds more shelves the same way:

| Shelf | Folder | Default core | Alternative |
|---|---|---|---|
| NES | `Games/NES` | fceumm | nestopia |
| SNES | `Games/SNES` | snes9x | snes9x2005_plus |
| Game Gear | `Games/GG` (`.gg`) | Genesis Plus GX (3x, like Game Boy) | none yet |
| Master System | `Games/SMS` (`.sms`) | Genesis Plus GX (2x) | none yet |
| Mega Drive | `Games/MD` (`.md`, `.gen`, `.bin`) | Genesis Plus GX (2x, 6-button) | none yet |
| PlayStation (planned, not shipped) | `Games/PS1` (`.chd`, `.cue`, `.pbp`, `.m3u`) | pcsx_rearmed | none |

The Sega shelves (ADR 0050 to 0056) play like their nearest Nintendo cousin: Game Gear and Master
System like NES (slot keeps L1 and R1, X and Y are turbo, START is Pause on Master System), Mega
Drive like SNES (X, Y, L and R are its X, Y, Z buttons and the game's own keys, SELECT is MODE,
SELECT+X toggles the picture, and Stretch follows the game's 256 or 320 wide frame). Their shaders
are the NES and SNES retro list, stored in `Config/sega_shaders.txt`, not in `slot.state`.

PlayStation is planned, not shipped (Phase 8, ADRs 0063 to 0069, issue 56). A device spike on the
RG34XXSP passed on 2026-10-16. v1 will be a digital pad with L2 and R2 for the game, user-supplied
BIOS files in `BIOS/` (none shipped, HLE otherwise), disc swap, and no rewind.

The goal is that a NES or SNES cart feels like a GBA cart in slot: same insert, same saves and
save states, same rewind and fast-forward, same menus. GBA, GB and GBC behaviour stays
byte-identical to upstream. That is the goal. The quick menu keeps its rows on every shelf. The Turbo
Buttons row does nothing on SNES, where X and Y are real buttons and always reach the game. The first version has known gaps, listed under [Known gaps](#known-gaps).

## Known gaps

- **SNES picture mode is SELECT+X.** L and R are game buttons on SNES, so slot's L/R picture toggle does not apply. NES keeps L1 for Stretch (it moves between Crop and Stretch) and R1 for Actual. NES and SNES default to Crop, a stretch that hides the overscan edges a TV hid (NES 8 pixels on every edge, SNES 8 lines top and bottom, ADR 0062); SELECT+X on SNES cycles Crop, Stretch, Actual.
- SNES hi-res frames (512 wide, a few titles) are blended 2:1 and lose detail.
- No colour correction on NES and SNES: SELECT+Y does nothing there and the in-game Screen page hides the Color Correction and Palette rows.
- NES and SNES carts keep their own procedural look (ns.0 style), not slot v1.7.0's bitmap carts; the light and dark themes change only the chrome around them.
- The NES and SNES shaders live on the NES or SNES shelf's Screen page and the in-game Screen page, not in the platform list the other shelves open.
- slot remembers the shelf and its cart at power off and restart (upstream's memory); the other shelves do not keep their own cart.
- The Turbo quick-menu row does nothing on SNES.
- PAL (50 Hz) titles run at 50 fps with their own pitch, so on the 59.6 Hz panel about one frame in six is shown twice (a slight judder). The PAL Speed row in the NES, SNES, Master System, Mega Drive and PlayStation Screen sections switches a system back to Panel (60 Hz, about 20% fast). Master System games count as PAL only when Genesis Plus GX knows them as European (ADR 0071).
- Sega: no second core yet (PicoDrive for Mega Drive, Gearsystem for Game Gear and Master System are
  the candidates). Mega Drive is a provisional go until the heavy-title device gate (Virtua Racing,
  Sonic 3D Blast, Street Fighter II SCE, Thunder Force IV) passes on the RG34XXSP. A Game Gear game
  that runs in Master System mode (256x192) is cropped to the 240x160 Game Gear canvas. Interlace
  mode 2 (Sonic 2 two-player) uses the core's single-field blend. Sega bezels use the GBA bezel
  choice, like NES and SNES.
- PlayStation (planned): no rewind and no fast-forward gesture (L2 and R2 belong to the game). The pad is a DualShock with both sticks, but which physical stick is left is not verified yet (`sh scripts/stick-check.sh` writes `Config/sticks.txt`), and L3 and R3 are not mapped.
- Settings keyed only by file name collide if the same name exists on two systems.
- Zip ROMs are not supported.

More in [docs/QUALITY-BAR.md](docs/QUALITY-BAR.md#known-gaps-not-hidden).

## How it works

slot builds mGBA from a pinned upstream commit plus a few `.patch` files. This repo does the same
thing to slot: a pinned slot release, plus the patches in `patches/`, built into a replacement
`System/slot` with the extra cores.

## Setup

```sh
brew install mise colima docker
brew install zbar            # optional: the barcode test skips without it
mise trust && mise install   # in the repo: rust 1.96, task, cmake 3.x, adb (macOS)
colima start
```

## Choosing a cart shell by hand

Each cart on the shelf is drawn from one of four outlines: `nes`, `famicom` (NES shelf) and `snes`, `sfc` (SNES shelf). By default slot picks one from the game's region. A NES file with `(Japan)` or the GoodTools `(J)` in its name (and no `(USA)`, `(Europe)` or `(World)` tag, or `U` or `E` in a GoodTools code like `(JU)`) is drawn as a Famicom, any other NES file as a NES. A SNES ROM is read from the region byte in its internal header: Japan and the PAL regions give the Super Famicom, USA gives the Super NES. Korea, Canada and Brazil also give the Super Famicom for now (no source settles their shell yet), and a ROM with no readable header is drawn as a Super NES. The `(Japan)` tag match is case sensitive, as in No-Intro names.

To override one game, add a line to `Config/cart_shell.txt` on the SD card, one line per game, the file name without its extension, then `=`, then the outline word, a colour and a finish:

```
Super Mario Bros. (USA)=famicom 7a7a7a solid
Some Game=auto ac8642 glitter
```

Words: `nes`, `famicom`, `snes`, `sfc`, `gg`, `sms`, `segacard`, `megadrive`, `genesis`, `auto` (the region pick), plus the Game Boy words `notched` and `rounded`. A word that belongs to another platform is ignored and the cart is treated as `auto`: `sfc` on a NES game does nothing. The colour is six hex digits, the finish is `solid`, `clear` or `glitter`.

Keep NES and SNES overrides in `Config/cart_shell.txt`. The cart studio at studio.slot-cfw.fyi writes `Labels/cart_shell.txt`, and whether it keeps the new words when it rewrites that file has not been checked.

## Fetching real cart labels

`tools/fetch-labels.py` (python3 standard library only) puts the real printed label on every cart of every shelf: GBA, GB, GBC, NES, SNES, Game Gear, Master System and Mega Drive. It never uses a screenshot, and box art only for Master System, whose carts carry little more than the name: every Master System cart shows its whole front box (ScreenScraper `box-2D`, ADR 0057), and nothing it fetches is committed: art is downloaded on your machine, at the time you run it, into your cache folder (`~/Library/Caches/slot-nes-snes/labels` on macOS, `$XDG_CACHE_HOME` or `~/.cache` elsewhere), so a rerun fetches nothing twice.

```sh
# the SD card stays in the device, ROM library on this machine (nes/ snes/ gba/ gb/ gbc/ folders, loose or zipped)
task labels:fetch -- --device --library ~/ROMS --limit 5 --dry-run     # look first
task labels:fetch -- --device --library ~/ROMS --limit 5               # smoke test: 5 per system
task labels:fetch -- --device --library ~/ROMS                          # the lot
task labels:fetch -- --card /Volumes/SLOT                               # a mounted card instead of adb
```

Flags: `--only <GBA|GB|GBC|NES|SNES or one ROM stem>`, `--dry-run`, `--force`, `--limit N` (per system), `--sd` (default `/mnt/sdcard`), `--by-name`, `--report <file>`, `--suggest <file>` and `--aliases <file>` (a ROM no CRC finds copies a same-title sibling's label or is searched on ScreenScraper by name, see `docs/cart-art/BY-NAME.md`). It ends with a summary of matched, written, skipped (label already there), missing (no art found), unknown CRC and errors. Restart slot after the push so it reads the new labels.

How it works:
- Each ROM is found by CRC32, never by name. NES is hashed whole and then without the 16 byte iNES header, SNES without a 512 byte copier header. A zipped ROM is named for the ROM inside the zip, the same rule `scripts/push-roms.py` uses. The libretro-database dats map the CRC to the No-Intro name, for the report and for the region.
- With `--device` the device's `Games/<SYSTEM>/` is listed with a shell glob (its `ls` adds colour codes), and only labels that are not already on the device are pushed. An existing PNG or `Labels/cart_shell.txt` line is never replaced without `--force`. New lines are merged into the device's own `cart_shell.txt`.
- Label sources, in order: (1) Brandon Kowalski's art set at art.slot-cfw.fyi (GBA, GB, GBC), looked up by CRC32 in its `index.json`, one request at a time with a pause and a User-Agent naming this project; (2) ScreenScraper `support-texture`, when `SS_DEVID` and `SS_DEVPASSWORD` (and your own `SS_SSID`, `SS_SSPASSWORD`) are set in the environment. Credentials are never printed. It reads your account's quota, stops cleanly when it is spent, and the next run resumes where it stopped. The art set has no NES or SNES art, so those two shelves need ScreenScraper. A ROM no source has is listed as missing. A libretro logo fallback is not implemented, since it would need image code beyond the standard library.
- The PNG is written as fetched. slot cover-fits any PNG into the label box and caches it itself, so no resizing is needed here.
- For NES and SNES the dat's region adds a `Labels/cart_shell.txt` line only where slot would not pick the outline itself: `famicom` for a NES game the dat marks Japan only, `sfc` for a SNES game the dat marks Japan or a PAL region. A line sets the plastic colour too (slot's default grey), which replaces slot's per-title plastic for that cart. To pick a different outline by hand, edit `Config/cart_shell.txt` (see above), which wins over `Labels/cart_shell.txt`.

Terms of what it fetches. The libretro-database dats are CC BY-SA 4.0. ScreenScraper's art is CC BY-NC-SA: non-commercial use, with attribution to ScreenScraper and its contributors. The art set at art.slot-cfw.fyi is harvested from ScreenScraper under the same licence. The cart art itself is the property of its rights holders. Use it for your own device and do not redistribute it.

Second option for GBA, GB and GBC: [Cart Studio](https://studio.slot-cfw.fyi) (Brandon's browser tool) can write `Labels/` for those three shelves. Point it at a local mirror folder of your card (copy `Games/` and `Labels/` from the device with `adb pull`, run the studio on it, then `adb push` the resulting `Labels/` back). It does not do NES or SNES yet.

## Install on a device

Build the zip with `task zip` (it runs `task dist:device` and `task src-tarball` itself). It lands in `build/` as
`slot-nes-snes-<slot tag>-<ns.N>-h700.zip`. `sh scripts/zip-check.sh <zip>` checks it.

**Without adb (how most people install):** unzip, then copy the contents of the one top folder
(`System/`, `BIOS/`, `Config/`, `Games/`, ...) onto the root of the SD card, merging with what is
there. An update replaces `System/` and keeps `Config/`, `Saves/` and `States/`. Put NES carts in
`Games/NES`, Sega carts in `Games/GG`, `Games/SMS` and `Games/MD`.

**With adb:** `task deploy:device` pushes `System/` to `/mnt/sdcard` and reboots the device
(`SD=/other/path` overrides the target), then `task log:device` prints `slot.log`.

**Going back to stock slot:** an unpatched slot does not know the NES or SNES shelves. If its
`Config/slot.state` says `cart_platform=nes` (or `snes`, `gg`, `sms`, `md`) because one of our carts was in the slot,
it reads that as no platform and looks the cart up by name. The cart sits in `Games/NES`, which
stock slot never scans, so it finds nothing and boots to the shelf with the slot empty (unless a
GBA, GB or GBC cart has the same name, which it seats instead). Nothing panics and no file is
deleted: `Games/NES`, `Games/SNES`, `Saves/` and `States/` stay as they are.
`sh scripts/check-downgrade.sh` runs this case against the upstream tree.

## Status

Planned. No patches yet. Work starts with Phase 1 of [docs/PLAN.md](docs/PLAN.md).

Progress is tracked on the [project board](https://github.com/users/felipecpaiva/projects/8), one issue per pull request, with a milestone per phase. The issues are generated from [.github/issues/](.github/issues/) by `python3 scripts/setup-github-project.py` (safe to re-run).

- [docs/RESEARCH.md](docs/RESEARCH.md): code map of slot v1.6.0, core choices for the H700, licence notes
- [docs/EVAL.md](docs/EVAL.md): the options considered (upstream PR, shim core, patch set) and why
- [docs/PLAN.md](docs/PLAN.md): the phased build plan, with tests per phase
- [docs/DECISIONS.md](docs/DECISIONS.md): binding decisions and why
- [docs/QUALITY-BAR.md](docs/QUALITY-BAR.md): what "done" means, and the known gaps

## Licences

slot is GPL-3.0-or-later, so this patch set is too (see [LICENSE](LICENSE)). fceumm and nestopia
are GPL-2.0-or-later. **snes9x, snes9x2005_plus and Genesis Plus GX are not GPL**: they are free for
non-commercial use only. Builds that include them ship their licence files
(`System/licenses/snes9x-LICENSE.txt`, `System/licenses/snes9x2005-LICENSE.txt`,
`System/licenses/genesis_plus_gx-LICENSE.txt`) and must never be sold or bundled with anything sold.
See [LICENSING.md](LICENSING.md).

## Credit

All of the hard work is Brandon Kowalski's [slot](https://github.com/BrandonKowalski/slot). Go
star it.
