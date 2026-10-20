More systems for [slot](https://github.com/BrandonKowalski/slot) on the Anbernic H700 handhelds
(tested on the RG34XXSP), as a patch set on slot's own source. The base is in the tag: a slot
release, or `main-<commit>` before upstream tags it. This release is built on slot main `1b20432`,
the coming 1.8.0. GBA, GB and GBC stay byte-identical to that slot.

## What is in it

Eleven new shelves beside slot's GBA, GB and GBC, each with its own folder, cores, saves and Screen
section:

| Shelf | Folder | Core (pinned commit) | BIOS |
|---|---|---|---|
| NES | `Games/NES` | fceumm `ac0d00a7fc01`, or nestopia `135dfa6dfda5` | none |
| SNES | `Games/SNES` | snes9x `fae2fea08f74`, or snes9x2005_plus `a79dfe9047e7` | none |
| Master System | `Games/SMS` | Genesis Plus GX `393f70cd64c7` | none |
| Game Gear | `Games/GG` | Genesis Plus GX `393f70cd64c7` | none |
| Mega Drive | `Games/MD` | Genesis Plus GX `393f70cd64c7` | none |
| Sega 32X | `Games/32X` | PicoDrive `1890c2932234` | none |
| PlayStation | `Games/PS1` | pcsx_rearmed `c8816799b503` | optional, your own `scph5501.bin` or similar (HLE otherwise) |
| TurboGrafx-16, PC Engine | `Games/TG16` | Beetle PCE Fast `3f946f277aef` | none (HuCards only) |
| WonderSwan, WonderSwan Color | `Games/WS` | Beetle Cygne `4b01295838ea` | none |
| Atari Lynx | `Games/Lynx` | Beetle Lynx `fcdefcfb3c11` | **required**, your own `lynxboot.img` |
| NeoGeo Pocket, Pocket Color | `Games/NGP` | Beetle NeoPop `a50d5ac288a8` | none |

Full commits and sha256s are in `SLOT_PIN`. mGBA and gpSP are slot's own, unchanged.

Also in this release:

- Real cart labels, PS1 jewel cases with cover and disc art, and the Master System front box, from
  `tools/fetch-labels.py` (fetched on your machine, never shipped), with a Logo Only fallback.
- Per-system Screen sections: shader, picture (Crop, Stretch, Actual, 4:3), PAL Speed, and more.
- PAL games at their own 50 Hz, with a Panel option for 60 Hz.
- A crash guard: a game that crashed slot while starting stays on the shelf instead of a boot loop.
- Fast shelf scroll on long shelves, a CPU row (Performance or Balanced), each shelf remembering its
  own cart, and files named `[BIOS]...` hidden from every shelf.
- `tools/hacks.py`: ROM hack updates that keep saves, `--add` for new hacks, PS1 disc patching,
  and rollback backups kept off the card if you want (`backups` setting, `--migrate-backups`).

## Licence notice

@NOTICE@

The rest is GPL: slot and this patch set are GPL-3.0-or-later, fceumm as shipped is
GPL-3.0-or-later, nestopia and pcsx_rearmed are GPL-2.0-or-later, and the Beetle cores are Mednafen's
GPL code (Beetle Cygne's NEC V30MZ emulator is by Bryan McPhail). The corresponding source is
`slot-nes-snes-src-@TAG@.tar.gz`, attached here, and every core's source is inside the zip at
`System/licenses/`. See LICENSING.md in the repo.

## Do not report issues to slot's tracker

This is not part of slot and its author does not endorse it. Please do not report bugs from this
release to slot's tracker. Open them at https://github.com/felipecpaiva/slot-nes-snes/issues.

## Install

1. Download `slot-nes-snes-@TAG@-h700.zip` and unzip it. It holds one folder of the same name.
2. Copy the contents of that folder (`System/`, `BIOS/`, `Config/`, `Games/` and the rest) onto the
   root of the SD card, merging with what is there.
3. Put games in their folders: `Games/NES`, `Games/SNES`, `Games/SMS`, `Games/GG`, `Games/MD`,
   `Games/32X`, `Games/PS1`, `Games/TG16`, `Games/WS`, `Games/Lynx` and `Games/NGP`. Zip ROMs are
   not supported. Put BIOS files in `BIOS/`.
4. Boot the device.

## Update

1. Delete `System/` from the SD card.
2. Copy the new `System/` from the zip in its place.
3. Keep `Config/`, `Saves/` and `States/`: they hold your settings, saves and save states.

## Known limits

- Device gate still open for Sega 32X, TurboGrafx-16, WonderSwan, Atari Lynx and NeoGeo Pocket:
  they pass their host tests and run on the device, but the full speed and audio gate has not been
  run. Mega Drive is a provisional go until its heavy-title gate passes.
- Sega 32X: the polygon games (Virtua Racing Deluxe, Star Wars Arcade, Virtua Fighter) may sit near
  the frame budget. If one misses frames, set Renderer to Fast, then Sound Rate to 22 kHz, in the
  32X Screen section. A 32X game left in `Games/MD` does not run there: move it to `Games/32X`.
- Atari Lynx needs `BIOS/lynxboot.img` (512 bytes) and keeps progress in save states only (no EEPROM).
- PlayStation: no rewind, and L3 and R3 are not mapped.
- SNES hi-res frames are blended 2:1. No colour correction on the new systems.
- Settings keyed only by file name collide if the same name exists on two systems.

The full list: https://github.com/felipecpaiva/slot-nes-snes#known-gaps
