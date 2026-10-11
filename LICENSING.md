# Licensing

## slot and this patch set

slot is GPL-3.0-or-later. The patches in `patches/` change slot, so they are GPL-3.0-or-later
too. The full text is in `LICENSE`.

## fceumm

fceumm (libretro-fceumm) is GPL-2.0-or-later. Checked at commit
`ac0d00a7fc01166f84c7bac01d1084ebfd2b865e`, the commit `SLOT_PIN` pins:

- `Copying` is the GNU GPL version 2 text, copied verbatim to `licenses/fceumm-GPL-2.0.txt`.
- `README.md` says "Licensed under the GNU GPL v2. See the source headers for details."
- 490 of the `.c` and `.h` files under `src/` carry the header "either version 2 of the
  License, or (at your option) any later version". Spot-checked by hand: `src/fceu.c`,
  `src/ppu.c`, `src/x6502.c`, `src/cart.c`, `src/sound.c`, `src/ines.c`,
  `src/boards/mmc1.c`, `src/boards/mmc3.c`. No file says version 2 only.
- Files with no GPL header at all, for example `src/drivers/libretro/libretro.c`, the
  `src/fir/*.h` tables and most plain headers, are part of the same work and covered by the
  README statement. This is not a per-file grant, so it is a judgement, not a quote.
- Some files carry their own terms: `src/ntsc/*` (LGPL 2.1 or later, `license.txt` there),
  `src/boards/pic16c5x.c` (BSD-3-Clause), `src/boards/emu2413.c` (permissive, Mitsutaka
  Okazaki) and `libretro-common/*` (MIT). All are compatible with GPL-2.0-or-later.

Conclusion: the combined fceumm work is GPL-2.0-or-later. The source tarball for the exact
commit ships beside the core as corresponding source (`vendor/fceumm-src.tar.gz`).

## snes9x

To be verified in issues 13 and 19.

## nestopia

To be verified in issues 13 and 19.
