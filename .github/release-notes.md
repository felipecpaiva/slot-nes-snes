NES and SNES shelves for [slot](https://github.com/BrandonKowalski/slot) (the base is in the tag: a slot
release, or `main-<commit>` before upstream tags it) on the Anbernic
H700 handhelds (tested on the RG34XXSP). Games/NES and Games/SNES sit beside the GBA, GB and GBC
shelves.

## Licence notice

@NOTICE@

The rest is GPL: slot and this patch set are GPL-3.0-or-later, fceumm and nestopia are
GPL-2.0-or-later. The corresponding source is `slot-nes-snes-src-@TAG@.tar.gz`, attached here and
inside the zip at `System/licenses/`. See LICENSING.md in the repo.

## Do not report issues to slot's tracker

This is not part of slot and its author does not endorse it. Please do not report bugs from this
release to slot's tracker. Open them at https://github.com/felipecpaiva/slot-nes-snes/issues.

## Install

1. Download `slot-nes-snes-@TAG@-h700.zip` and unzip it. It holds one folder of the same name.
2. Copy the contents of that folder (`System/`, `BIOS/`, `Config/`, `Games/` and the rest) onto the
   root of the SD card, merging with what is there.
3. Put NES carts in `Games/NES` and SNES carts in `Games/SNES`. Zip ROMs are not supported.
4. Boot the device.

## Update

1. Delete `System/` from the SD card.
2. Copy the new `System/` from the zip in its place.
3. Keep `Config/`, `Saves/` and `States/`: they hold your settings, saves and save states.

## Known gaps

See the README: https://github.com/felipecpaiva/slot-nes-snes#known-gaps
