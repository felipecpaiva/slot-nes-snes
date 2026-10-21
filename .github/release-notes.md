More systems for [slot](https://github.com/BrandonKowalski/slot) on the Anbernic H700 handhelds
(tested on the RG34XXSP), as a patch set on slot's own source. The base is in the tag: this release is
built on slot's tagged release 1.8.0 (`0ceac65`), and `-ns.1` is our first release on it. GBA, GB and
GBC stay byte-identical to that slot.

## What is new

The release before this one was never published, so this is the first public build. Since slot's own
1.8.0, the patch set adds:

- **More shelves**: Famicom Disk System, Sega CD / Mega-CD, PC Engine CD, PC Engine SuperGrafx,
  Atari 2600, Atari 7800, Virtual Boy, Neo Geo CD, PICO-8, and arcade boards on FinalBurn Neo (Neo Geo,
  CPS1, CPS2), on top of the shelves of the earlier notes. That is 26 system shelves beside Recents
  and Favorites.
- **Shelf order by release year**: Settings > General > Shelf Order, Classic or Release Year. The
  Screen page follows the same order.
- **Expansion Card**: a second TF card holds whole systems' game folders, for the large disc shelves.
  Setup is below.
- **Slot 1.8.0 controls**: the picture flip is the Shortcuts row Picture Next (SELECT+X by default)
  and every control can be remapped. Disc and disk swap follows Palette Back (SELECT+L2).
- **Label fetcher**: `--by-name` for games no CRC finds, and `--logo-fallback` for a game's logo on a
  plain ground when no art exists. PICO-8 labels come from the cart itself, offline.
- **ROM hack tool**: `tools/hacks.py` can keep rollback backups off the card.
- **Crash guard and fast scroll**: a game that crashed slot while starting stays on the shelf, and long
  shelves scroll 3 carts at a time when you hold Left or Right.
- A faster scan of the arcade shelves, and [BIOS] files kept off every shelf.

## Shelves

| Shelf | Folder | Core (pinned commit) | BIOS |
|---|---|---|---|
| NES | `Games/NES` | fceumm `ac0d00a7fc01`, or nestopia `135dfa6dfda5` | none |
| Famicom Disk System | `Games/FDS` | fceumm `ac0d00a7fc01` | **required**, your own `disksys.rom` |
| SNES | `Games/SNES` | snes9x `fae2fea08f74`, or snes9x2005_plus `a79dfe9047e7` | none |
| Master System | `Games/SMS` | Genesis Plus GX `393f70cd64c7` | none |
| Game Gear | `Games/GG` | Genesis Plus GX `393f70cd64c7` | none |
| Mega Drive | `Games/MD` | Genesis Plus GX `393f70cd64c7` | none |
| Sega 32X | `Games/32X` | PicoDrive `1890c2932234` | none |
| Sega CD, Mega-CD | `Games/SEGACD` | Genesis Plus GX `393f70cd64c7` | **required**, your own `bios_CD_U.bin`, `bios_CD_E.bin`, `bios_CD_J.bin` |
| PlayStation | `Games/PS1` | pcsx_rearmed `c8816799b503` | optional, your own `scph5501.bin` or similar (HLE otherwise) |
| TurboGrafx-16, PC Engine | `Games/TG16` | Beetle PCE Fast `3f946f277aef` | none (HuCards only) |
| PC Engine CD, TurboGrafx-CD | `Games/PCECD` | Beetle PCE Fast `3f946f277aef` | **required**, your own `syscard3.pce` |
| PC Engine SuperGrafx | `Games/SGX` | Beetle SuperGrafx `9c11dcd213a7` | none |
| WonderSwan, WonderSwan Color | `Games/WS` | Beetle Cygne `4b01295838ea` | none |
| Atari Lynx | `Games/Lynx` | Beetle Lynx `fcdefcfb3c11` | **required**, your own `lynxboot.img` |
| NeoGeo Pocket, Pocket Color | `Games/NGP` | Beetle NeoPop `a50d5ac288a8` | none |
| Atari 2600 | `Games/A2600` | Stella 2014 `7d1361e407e6` | none |
| Atari 7800 | `Games/A7800` | ProSystem `8a88014287c7` | optional, off by default |
| Virtual Boy | `Games/VB` | Beetle VB `d5ae54c8e23b` | none |
| Neo Geo (MVS and AES arcade sets) | `Games/NEOGEO` | FinalBurn Neo `2dbbac7623fb` | **required**, your own `neogeo.zip` |
| Capcom CPS1 | `Games/CPS1` | FinalBurn Neo `2dbbac7623fb` | none |
| Capcom CPS2 | `Games/CPS2` | FinalBurn Neo `2dbbac7623fb` | none |
| Neo Geo CD | `Games/NEOCD` | NeoCD `b1e04c738cb4` | **required**, your own `neocd.bin` in `BIOS/neocd/` |
| PICO-8 | `Games/PICO8` | FAKE-08 `814991a2571a` | none |

Full commits and sha256s are in `SLOT_PIN`. mGBA and gpSP are slot's own, unchanged.

## Licence notice

@NOTICE@

The rest is GPL: slot and this patch set are GPL-3.0-or-later, fceumm as shipped is
GPL-3.0-or-later, nestopia and pcsx_rearmed are GPL-2.0-or-later, and the Beetle cores are Mednafen's
GPL code (Beetle Cygne's NEC V30MZ emulator is by Bryan McPhail). NeoCD is LGPL-3.0 apart from its
non-commercial Z80 core, and FAKE-08 is MIT-licensed free software. The corresponding source is
`slot-nes-snes-src-@TAG@.tar.gz`, attached here, and every core's source is inside the zip at
`System/licenses/`. See LICENSING.md in the repo for each core.

## Do not report issues to slot's tracker

This is not part of slot and its author does not endorse it. Please do not report bugs from this
release to slot's tracker. Open them at https://github.com/felipecpaiva/slot-nes-snes/issues.

## Install

1. Download `slot-nes-snes-@TAG@-h700.zip` and unzip it. It holds one folder of the same name.
2. Copy the contents of that folder (`System/`, `BIOS/`, `Config/`, `Games/` and the rest) onto the
   root of the SD card, merging with what is there.
3. Put games in the folders of the table above. Zip ROMs are not supported, except on the three
   arcade shelves, where the zip is the romset (FinalBurn Neo 1.0.0.03 sets, named as the set, for
   example `mslug.zip`). Put BIOS files in `BIOS/`, the Neo Geo one as `BIOS/neogeo.zip`.
4. Boot the device.

## Update

1. Delete `System/` from the SD card.
2. Copy the new `System/` from the zip in its place.
3. Keep `Config/`, `Saves/` and `States/`: they hold your settings, saves and save states.

## Expansion Card

Disc shelves are large. A second TF card (TF2) can hold whole systems' game folders while the main card
stays the one BaseOS runs from.

1. On a Mac, prepare the card with `tools/expansion-card.py`. It erases the whole disk and refuses
   unless the identifier, the exact size and the volume name match; without `--yes` it only prints its
   plan: `python3 tools/expansion-card.py --disk disk4 --size <bytes> --label <name> --systems PS1`.
2. Copy the games into `Games/<SYS>/` on the partition named `EXPANSION`.
3. List the moved systems in `Config/expansion.txt` on the main card, one folder name per line (for
   example `PS1`, `SEGACD`, `NEOCD`). `#` starts a comment.

Saves, states and labels stay on the main card. Without the Expansion Card in, the base card's own
folders show. The README has the full steps.

## Known limits

- Neo Geo CD is silent while a disc loads.
- Atari Lynx has a short audio gap at the very first frame of a game that runs at 75 Hz. Lynx carts
  made to be held sideways, and the NeoGeo Pocket in-game save, are still to be checked by hand on the
  device.
- PC Engine CD plays one disc per game (no disc change, no `.m3u`) and needs System Card 3.0.
- Sega 32X: the polygon games (Virtua Racing Deluxe, Star Wars Arcade, Virtua Fighter) may sit near
  the frame budget. If one misses frames, set Renderer to Fast, then Sound Rate to 22 kHz, in the 32X
  Screen section. A 32X game left in `Games/MD` does not run there: move it to `Games/32X`.
- Mega Drive stays provisional until its heavy-title gate passes.
- Atari Lynx needs `BIOS/lynxboot.img` (512 bytes) and keeps progress in save states only (no EEPROM).
- PICO-8 has no save states, no resume and no rewind, and FAKE-08 stops on a Lua error in some carts.
- Arcade sets must match FinalBurn Neo 1.0.0.03; an older MAME set may lack a file. CPS3 is not
  included.
- PlayStation: no rewind, and L3 and R3 are not mapped.
- SNES hi-res frames are blended 2:1. No colour correction on the new systems.
- Settings keyed only by file name collide if the same name exists on two systems.

The full list: https://github.com/felipecpaiva/slot-nes-snes#known-gaps
