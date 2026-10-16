# Licensing

## slot and this patch set

slot is GPL-3.0-or-later. The patches in `patches/` change slot, so they are GPL-3.0-or-later
too. The full text is in `LICENSE`.

### Source offer (GPL-3.0-or-later, section 6)

Every release zip carries the complete corresponding source of `System/slot` and of the cores
we add, so no written offer is needed. It is in `System/licenses/`:

- `slot-nes-snes-src-<release>.tar.gz`: the patched slot source (`slot/`, `work/slot` at the
  exported commit) plus this repository (`slot-nes-snes/`, with `patches/`). It does not hold
  the gpSP, fceumm, snes9x, nestopia or snes9x2005_plus sources; those sit next to it in the same folder (below). It also does not
  hold slot's Rust crates: Cargo fetches them by `slot/Cargo.lock`, exactly as upstream does.
  A vendored-crates archive (`cargo vendor`) can be provided on request: open an issue.
  Every download in the build is listed with its check in [docs/SUPPLY-CHAIN.md](docs/SUPPLY-CHAIN.md).
- `fceumm-src.tar.gz` and `fceumm-src.meta`: the exact fceumm source and its sha256.
- `snes9x-src.tar.gz` and `snes9x-src.meta`: the same for snes9x.
- `nestopia-src.tar.gz` and `nestopia-src.meta`: the same for nestopia.
- `snes9x2005_plus-src.tar.gz` and `snes9x2005_plus-src.meta`: the same for snes9x2005_plus.
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

> snes9x, snes9x2005_plus and Genesis Plus GX are licensed for non-commercial use only and are not
> GPL. This release includes them, with their licences in System/licenses/snes9x-LICENSE.txt,
> System/licenses/snes9x2005-LICENSE.txt and System/licenses/genesis_plus_gx-LICENSE.txt. Do not
> sell this zip or bundle it with anything that is sold.

## nestopia

Checked at commit `135dfa6dfda5e7603d61e751b9ddd0cc42546bc3`, the commit `SLOT_PIN` pins, in the unpacked `nestopia-src.tar.gz`
(634 `.c`, `.h`, `.cpp` and `.hpp` files under `source/` and `libretro/`, not counting
`libretro/libretro-common`).

**The nestopia core we ship is GPL-2.0-or-later**, and combined with slot (GPL-3.0-or-later) the
zip is an aggregate of separate programs: slot loads the core at run time across the libretro C
ABI, as for fceumm.

- `COPYING` is the GNU GPL version 2 text, copied verbatim to `licenses/nestopia-GPL-2.0.txt`.
  `README` says "Nestopia JG (GPL-2.0-or-later)", Copyright 2003-2008 Martin Freij, 2008-2018
  Nestopia UE Contributors, 2020-2026 Rupert Carmichael.
- 623 of the 634 files carry the GPL text and every one of them says "any later version", so
  GPL-2.0-or-later. No file says version 2 only and none says version 3. Command, run in the
  unpacked source root: `grep -rl 'any later version' source libretro --include='*.[ch]' --include='*.[ch]pp'
  | grep -v libretro-common | wc -l`.
- The other 11 have no licence text in their first 60 lines: the six `libretro/` glue files
  (`libretro.cpp`, `nesfont.h`, `nstdatabase.hpp`, `palettes.hpp`, `libretro_core_options.h`,
  `libretro_core_options_intl.h`) and five `source/nes_ntsc/` files. We treat the glue as covered by
  the README's GPL-2.0-or-later, a judgement, not a quote.
- Files with their own terms: `source/nes_ntsc/*` is LGPL-2.1-or-later, Shay Green (`source/nes_ntsc/license.txt`,
  README), and `libretro/libretro-common/*` is the RetroArch team's MIT text.
- The core links the C++ runtime statically on the device (`-static-libstdc++ -static-libgcc`,
  `device_ldflags=` in its `.meta`), as for snes9x.

Conclusion: the nestopia core is GPL-2.0-or-later with its full corresponding source shipped as
`nestopia-src.tar.gz`. Unlike fceumm, no GPL-3-only file was found.

## snes9x2005_plus

Checked at commit `a79dfe9047e7fec58808aefe48ad2bf499c7af11` of libretro/snes9x2005, the commit `SLOT_PIN` pins as
`snes9x2005_plus_commit`. It is built with `USE_BLARGG_APU=1`, which makes the makefile name the
output `snes9x2005_plus_libretro.so`. The licence is the `copyright` file at the root of that
source (it has no `LICENSE`), copied verbatim to `licenses/snes9x2005-LICENSE.txt`. The exact source
ships with the core as `snes9x2005_plus-src.tar.gz`, with `snes9x2005_plus-src.meta` recording its
sha256.

**snes9x2005_plus is not free software and is not GPL-compatible**, for the same reason as snes9x:
it is derived from Snes9x 1.43 and carries the Snes9x terms. The file says, quoted:

- "Permission to use, copy, modify and/or distribute Snes9x in both binary and source form, for
  non-commercial purposes, is hereby granted without fee, providing that this license information
  and copyright notice appear with all copies and any derived work."
- "Snes9x is freeware for PERSONAL USE only." Commercial use includes "charging money for Snes9x or
  software derived from Snes9x, including Snes9x or derivatives in commercial game bundles".
- The 2014-2016 RetroArch team notice adds "UNDER NO CIRCUMSTANCE WILL COMMERCIAL RIGHTS EVER BE
  APPROPRIATED TO ANY PARTY".
- Parts have other terms, all in the same file: the RetroArch team's MIT text, and ndssfc and ZSNES
  code under GPL-2.0-or-later. Those do not lift the non-commercial restriction on the whole.
  `libretro-common/` is the RetroArch MIT code.

The plugin boundary stance is the one for snes9x above: `snes9x2005_plus_libretro.so` is a separate
program loaded by `dlopen` across the libretro C ABI, and the zip is an aggregate of separate works.
This is our reading, not legal advice. The core is plain C, so no libstdc++ is linked. **The zip must
never be sold, or bundled with anything that is sold**, and the notice under snes9x covers this core
too. The README "Licences" paragraph names both.

## Genesis Plus GX

Checked at commit `393f70cd64c7334564c19a424c383f53986c13f4` of libretro/Genesis-Plus-GX, the commit
`SLOT_PIN` pins as `genesis_plus_gx_commit` (tarball sha256 `genesis_plus_gx_tarball_sha256`). It
is built by `cores/genesis_plus_gx/build.sh` for Game Gear, Master System and Mega Drive (ADR 0053),
and ships from the release that carries the first Sega platform (issue 50). Its licence, the root
`LICENSE.txt` of that source copied verbatim and whole, is `licenses/genesis_plus_gx-LICENSE.txt`,
which `scripts/dist-device.sh` copies into `System/licenses/` with every other file in `licenses/`, and
`scripts/zip-check.sh` requires and compares byte for byte. The exact source ships with the core as
`genesis_plus_gx-src.tar.gz`, with `genesis_plus_gx-src.meta` recording its sha256.

**Genesis Plus GX is not free software and is not GPL-compatible**, like snes9x. The file says, quoted:

- "Unless otherwise explicitly stated, all code in Genesis Plus GX is released under the following
  license", Copyright (c) 1998-2003 Charles MacDonald, (c) 2007-2026 Eke-Eke, "Some portions copyright
  Nicola Salmoria and the MAME team".
- "Redistributions may not be sold, nor may they be used in a commercial product or activity."
- "Redistributions that are modified from the original source must include the complete source code".
  We build the pinned source unmodified and ship the source tarball anyway.
- "Redistributions must reproduce the above copyright notice", which is why the whole file ships, not
  a summary.

Other terms inside the same file, for code compiled into `genesis_plus_gx_libretro.so` (from the link
line of the pinned `Makefile.libretro` build): the Nuked OPN2 core (`core/sound/ym3438.c`,
LGPL-2.1-or-later, Alexey Khokholov), the Nuked OPLL core (`core/sound/opll.c`, the same non-commercial
terms as above), the NTSC filters and Blip Buffer (Shay Green, LGPL-2.1-or-later), Tremor (Xiph, BSD
style), and libchdr with its LZMA (public domain), zstd (BSD), zlib and dr_flac notices. The
`libretro-common` files are the RetroArch team's MIT text. The LGPL parts sit in a separate shared
library with their full source shipped, which LGPL-2.1 allows. None of them lifts the non-commercial
restriction on the whole.

The plugin boundary stance is the one for snes9x above: a separate program loaded by `dlopen` across
the libretro C ABI, the zip an aggregate of separate works. This is our reading, not legal advice.
The core is plain C and links only `libc` and `libm` on the device. The notice under snes9x names
Genesis Plus GX too, and the release terms do not change: the zip was already never to be sold.

## PCSX ReARMed

Checked at commit `c8816799b50388e61cfe237fe2cdbb7d8175f20a` of libretro/pcsx_rearmed, the commit
`SLOT_PIN` pins as `pcsx_rearmed_commit` (tarball sha256 `pcsx_rearmed_tarball_sha256`). It is built
by `cores/pcsx_rearmed/build.sh` for PlayStation (ADR 0063) and ships from the release that carries
the PS1 platform (issue 58). Its licence, the root `COPYING` of that source copied verbatim and whole,
is `cores/pcsx_rearmed/pcsx_rearmed-GPL-2.0.txt` until then. The exact source ships with the core as
`pcsx_rearmed-src.tar.gz`, with `pcsx_rearmed-src.meta` recording its sha256.

**The pcsx_rearmed core we ship is GPL-2.0-or-later**, so it combines with slot's GPL-3.0-or-later
directly, with no plugin-boundary stance needed.

- `COPYING` is the GNU GPL version 2 text. `AUTHORS` names the PCSX, PCSX-df and PCSX-Reloaded
  teams, Ari64 (the ARM dynarec), Exophase (the NEON GPU) and notaz.
- Of the 245 `.c`, `.h` and `.S` files under `libpcsxcore/`, `plugins/` and `frontend/`, 161 say
  "any later version" or "version 2 or later" (some dual GPL-2.0-or-later or LGPL-2.1-or-later at
  the user's option), a few carry MIT, LGPL-2.1-or-later or BSD-3-Clause headers, and 72 carry no
  licence text, which we treat as covered by `COPYING`, a judgement, not a quote. No file says version
  2 only and none says version 3. Command, run in the unpacked source root: `find libpcsxcore plugins
  frontend \( -name '*.c' -o -name '*.h' -o -name '*.S' \) -type f -exec grep -l -i 'any later
  version\|version 2 or later\|v2 or later\|2.0-or-later\|2 or later' {} + | wc -l`.
- Bundled under `deps/` and compiled into the core (from the link line of the pinned
  `Makefile.libretro` build): libchdr (BSD-3-Clause, Romain Tisserand) with its LZMA SDK (public
  domain), zstd (BSD or GPL-2.0, the user's choice) and miniz (the Unlicense), for CHD discs
  (`HAVE_CHD=1`), and `libretro-common` (the RetroArch team's MIT text). lightrec (LGPL-2.1-or-later)
  and GNU lightning (LGPL-3.0-or-later) are in the tarball but not compiled: they build only with
  `DYNAREC=lightrec`, and our device build uses ari64 and the host build the interpreter.
- Every one of those terms permits combining with a GPL-3.0-or-later program.
- The core is plain C and links only `libc`, `libdl` and `libpthread` (and `libm` where the linker
  keeps it) at GLIBC_2.17 or older on the device, which `task core:device:pcsx_rearmed` checks.
- No PlayStation BIOS is shipped or used in CI. The core falls back to its own HLE BIOS.

The build recipe facts (the pin, `HAVE_PHYSICAL_CDROM=0`, `BUILTIN_GPU=neon`, CHD on, ari64 as the
aarch64 default) come from bently0602/slot and oauramos/omega-zero, both GPL-3.0, and are credited in
the commit that added the build.

## NES and SNES screen shaders

Patch `0017-retro-shaders` adds four NES and SNES screen shaders, ported from the libretro shader
collection into `crates/slot-gfx/src/pipeline/retro.rs`. Their attributions ship as
`licenses/retro-shaders.txt`, next to upstream's `licenses/shaders.txt`, which is left as it is:

- Sharp: sharp-bilinear-simple (rsn8887, after TheMaister). Public domain.
- Scanlines: scanlines-sine-abs (RiskyJumps). Public domain.
- crt-pi (davej, 2015-2016). GPL-2.0-or-later. Its copyright notice is kept in the licence file
  and as a comment in the GLSL source.
- crt-1tap v1.4 (fishku, GLSL port by DariusG). CC0.

Patch `0019-retro-line-pixel` adds two more in the same file:

- Pixel: pixellate (Fes, 2011-2012). ISC style permissive licence. Its full notice is kept in the
  licence file and as a comment in the GLSL source.
- Line: this project's own code. It reimplements the idea of MinUI's Line screen effect; no MinUI
  or NextUI code or images are used (MinUI has no licence, NextUI is PolyForm Noncommercial 1.0.0).

Each licence permits combining with slot under GPL-3.0-or-later.

## NES and SNES cart shells

Patch `0023-retro-bitmap-carts` adds `crates/slot-ui/assets/retro/nes_neutral.png`,
`famicom_neutral.png`, `snes_neutral.png` and `sfc_neutral.png`. They are generated by this
project's `crates/slot-ui/examples/retro_neutrals.rs` from our own outline and detail SVGs, so
they are GPL-3.0-or-later like the rest of the patch set. The lighting (grey levels, grain, edge
bevel and label well lips) is measured from upstream's `assets/gba_neutral.png`, painted by
Markus (@MarkusMaribu) for slot PR #74 and shipped under slot's GPL-3.0; no pixel of it is
copied. Credit for that look is his.

## Sega cart shells

Patch `0028-sega-carts` adds `gg_neutral.png`, `sms_neutral.png`, `segacard_neutral.png`,
`megadrive_neutral.png` and `genesis_neutral.png` beside them, made by the same example from our own
Sega outline and detail SVGs, with the same lighting measured from upstream's `gba_neutral.png`. They
are GPL-3.0-or-later. The reference photos in `docs/cart-art/refs/` that guided the outlines are
listed with their own licences in `docs/cart-art/refs/SOURCES.md`; none of their pixels is used in any
asset, and none ships in a release. Patch `0029-sms-box-art` regenerates `sms_neutral.png` and
`segacard_neutral.png` with the tall box art well (ADR 0057), by the same example, under the same licence.

## Code from other slot forks

Patch `0030-need-fullpath` follows two GPL-3.0 forks of slot, compatible with this patch set's
GPL-3.0-or-later: the path-only load of AaronC1990/tray (the original path, not canonicalised)
and the `SystemInfo` field order of bently0602/slot. Both are credited in the patch commit.
