# Licensing

## slot and this patch set

slot is GPL-3.0-or-later. The patches in `patches/` change slot, so they are GPL-3.0-or-later
too. The full text is in `LICENSE`.

### Source offer (GPL-3.0-or-later, section 6)

Every release zip carries the complete corresponding source of `System/slot` and of the cores
we add, so no written offer is needed. It is in `System/licenses/`:

- `slot-nes-snes-src-<release>.tar.gz`: the patched slot source (`slot/`, `work/slot` at the
  exported commit) plus this repository (`slot-nes-snes/`, with `patches/`). It does not hold
  the gpSP or fceumm sources; those sit next to it in the same folder (below). It also does not
  hold slot's Rust crates: Cargo fetches them by `slot/Cargo.lock`, exactly as upstream does.
  A vendored-crates archive (`cargo vendor`) can be provided on request: open an issue.
  Every download in the build is listed with its check in [docs/SUPPLY-CHAIN.md](docs/SUPPLY-CHAIN.md).
- `fceumm-src.tar.gz` and `fceumm-src.meta`: the exact fceumm source and its sha256.
- `snes9x-src.tar.gz` and `snes9x-src.meta`: the same for snes9x.
- `gpsp-<commit>.tar.gz` and the mGBA commit in `mgba-<commit>.meta`, with their patches, as
  slot ships them.

**Rebuilding `System/slot`.** Build the `slot/` tree in the main tarball as upstream does, with
Cargo and the network: Cargo fetches the crates by `Cargo.lock`. Without the network that works
only if you ran `cargo vendor` earlier or have a populated Cargo cache; we do not ship one. To
rebuild the whole zip from this repository instead, run `task zip`: it refetches the upstream
slot release named in `SLOT_PIN` (checked against its sha256), applies `patches/`, and checks
that result against the bundled `slot/` tree with `task patches:check`.

## fceumm

Checked at commit `ac0d00a7fc01166f84c7bac01d1084ebfd2b865e`, the commit `SLOT_PIN` pins. Every
count below was taken from the unpacked `vendor/fceumm-src.tar.gz` (631 `.c`, `.h` and `.cpp`
files under `src/`).

**The combined fceumm binary we ship is GPL-3.0-or-later.** fceumm is mostly
GPL-2.0-or-later, but part of it is derived from Mesen, which is GPL-3.0-or-later (below).
GPL-2.0-or-later code and GPL-3.0-or-later code can be combined only under GPL-3.0-or-later,
which is also slot's licence. We do not claim the combined core is GPL-2.0-or-later. The exact
source ships with the core as `vendor/fceumm-src.tar.gz`, with `fceumm-src.meta` recording its
sha256.

What is in the work:

- `Copying` is the GNU GPL version 2 text, copied verbatim to `licenses/fceumm-GPL-2.0.txt`.
  `README.md` says "Licensed under the GNU GPL v2. See the source headers for details."
- 491 `.c` and `.h` files under `src/` carry "any later version" (so GPL-2.0-or-later).
  Command, run in the unpacked source root:
  `find src \( -name '*.c' -o -name '*.h' \) -type f -exec grep -l 'any later version' {} + | wc -l`.
  Spot-checked by hand: `src/fceu.c`, `src/ppu.c`, `src/x6502.c`, `src/cart.c`,
  `src/sound.c`, `src/ines.c`, `src/boards/mmc1.c`, `src/boards/mmc3.c`. No file says
  version 2 only. `src/md5.c` says "licensed under the GPL" with no version.
- **Mesen-derived files, GPL-3.0-or-later.** `src/hdpack/hdpack_audio.c`, `hdpack_image.c`,
  `hdpack_load.c`, `hdpack_patch.c`, `hdpack_ppu.c`, `hdpack_render.c` and `hdpack_data.h` have
  no licence header. `hdpack_load.c` says it is a "Faithful port of Mesen's HdPackLoader", and
  `hdpack.h` says it is Mesen HD texture pack support. Mesen's licence, read from its primary
  source: the repository `LICENSE` is the GNU GPL version 3 text
  (<https://github.com/SourMesen/Mesen/blob/master/LICENSE>, GitHub reports GPL-3.0), and its
  `README.md` says "Mesen is available under the GPL V3 license" with the header "either version
  3 of the License, or (at your option) any later version", Copyright (C) 2014-2020 Sour
  (<https://github.com/SourMesen/Mesen/blob/master/README.md>). Mesen2 is the same
  (<https://github.com/SourMesen/Mesen2/blob/master/LICENSE>). So these files are
  GPL-3.0-or-later, and fceumm cannot ship them as GPL-2.0-or-later.
- **Headerless files, a judgement.** 79 of the 631 files have no licence text in their first 60
  lines, listed in `licenses/fceumm-headerless-files.txt` with the command that produced the
  list. The 7 hdpack files above are among them (3 more are under `libretro-common`, 10 are
  `src/fir` tables). Those files have no per-file grant. The README says GPL v2, so we treat
  them as covered by the project licence and distribute the whole under GPL-3.0-or-later with
  source. It is a judgement, not a quote.
- Files with their own terms, each read in the file: `src/ntsc/*` (LGPL 2.1 or later, see
  `nes_ntsc.c` and `src/ntsc/license.txt`), `src/boards/pic16c5x.c` and `.h` (MAME-style tag
  `license:BSD-3-Clause`, Tony La Porta), and `src/drivers/libretro/libretro-common/*` (the RetroArch
  team's MIT text, in 56 of its 61 files). `src/boards/emu2413.c` and `.h` carry no licence
  statement; the author is named (Mitsutaka Okazaki, 2001). We keep the files unmodified, as
  fceumm does.

Conclusion: fceumm minus the Mesen files is GPL-2.0-or-later; with them, and combined with
slot, the core we distribute is GPL-3.0-or-later with the full corresponding source shipped.

## snes9x

Checked at commit `fae2fea08f74180759ef540ee94259213f503480`, the commit `SLOT_PIN` pins. The
licence is the `LICENSE` file at the root of that source, copied verbatim to
`licenses/snes9x-LICENSE.txt`. The exact source ships with the core as `snes9x-src.tar.gz`, with
`snes9x-src.meta` recording its sha256.

**snes9x is not free software and is not GPL-compatible.** Its terms, quoted from that file:

- Permission to use, copy, modify and distribute is granted "for non-commercial purposes", in
  binary and source form, provided the licence and copyright notice appear with all copies and
  derived work.
- "Snes9x is freeware for PERSONAL USE only." Commercial use includes "charging money for Snes9x
  or software derived from Snes9x, including Snes9x or derivatives in commercial game bundles,
  and/or using Snes9x as a promotion for your commercial product." Commercial users must ask the
  copyright holders first.
- The software is provided as-is, with no warranty.
- Some parts have their own terms (snes_ntsc LGPL, xBRZ GPLv3, JMA), listed at the end of the file.
  At the pinned commit only `filter/snes_ntsc.c` (LGPL) is compiled into `snes9x_libretro.so`
  (`libretro/Makefile.common`). xBRZ and JMA are not in the libretro source tree. The snes_ntsc
  licence travels inside `snes9x-src.tar.gz` as `filter/snes_ntsc-license.txt`.
- On the device the core links the C++ runtime statically (`-static-libstdc++ -static-libgcc`,
  recorded as `device_ldflags=` in its `.meta`), so it needs only `libc` and `libm`. libstdc++ and
  libgcc are GPL-3.0 with the GCC Runtime Library Exception, which allows that.

Because the non-commercial clause is a restriction GPL-3.0 forbids, snes9x code cannot be
combined into slot's GPL-3.0-or-later binary, and we do not claim it can. **The plugin boundary
stance:** `snes9x_libretro.so` is a separate program that slot loads at run time across the libretro
C ABI (`retro_*` functions through `dlopen`). slot contains no snes9x code and does not link it.
The libretro buildbot distributes `snes9x_libretro` beside the GPL RetroArch
(<https://buildbot.libretro.com/nightly/linux/aarch64/latest/snes9x_libretro.so.zip>). We treat the zip as an aggregate of separate
works, each under its own licence, and this is our reading, not legal advice.

What follows for users:

- **The zip must never be sold, or bundled with anything that is sold.** Commercial redistribution
  is unsupported. Every release must carry the notice below.
- The licence file stays in `System/licenses/` beside the core, as its terms require.

Notice text (README "Licences" and the release notes carry it):

> snes9x is licensed for non-commercial use only and is not GPL. This release includes it, with
> its licence in System/licenses/snes9x-LICENSE.txt. Do not sell this zip or bundle it with
> anything that is sold.

## nestopia

To be verified in issues 13 and 19.
