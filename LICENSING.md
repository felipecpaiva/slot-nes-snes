# Licensing

## slot and this patch set

slot is GPL-3.0-or-later. The patches in `patches/` change slot, so they are GPL-3.0-or-later
too. The full text is in `LICENSE`.

### Source offer (GPL-3.0-or-later, section 6)

Every release zip carries the complete corresponding source of `System/slot` and of the cores
we add, so no written offer is needed. It is in `System/licenses/`:

- `slot-nes-snes-src-<release>.tar.gz`: the patched slot source (`slot/`, `work/slot` at the
  exported commit) plus this repository (`slot-nes-snes/`, with `patches/`). It does not hold
  the gpSP, fceumm, snes9x, nestopia, snes9x2005_plus or pcsx_rearmed sources; those sit next to it in the same folder (below). It also does not
  hold slot's Rust crates: Cargo fetches them by `slot/Cargo.lock`, exactly as upstream does.
  A vendored-crates archive (`cargo vendor`) can be provided on request: open an issue.
  Every download in the build is listed with its check in [docs/SUPPLY-CHAIN.md](docs/SUPPLY-CHAIN.md).
- `fceumm-src.tar.gz` and `fceumm-src.meta`: the exact fceumm source and its sha256.
- `snes9x-src.tar.gz` and `snes9x-src.meta`: the same for snes9x.
- `nestopia-src.tar.gz` and `nestopia-src.meta`: the same for nestopia.
- `snes9x2005_plus-src.tar.gz` and `snes9x2005_plus-src.meta`: the same for snes9x2005_plus.
- `pcsx_rearmed-src.tar.gz` and `pcsx_rearmed-src.meta`: the same for pcsx_rearmed.
- `picodrive-src.tar.gz`, `picodrive-emu2413-src.tar.gz`, `picodrive-dr_libs-src.tar.gz`,
  `picodrive-libpicofe-src.tar.gz` and `picodrive-src.meta`: PicoDrive and the three submodules its
  build compiles, each the archive `SLOT_PIN` pins (below).
- `fbneo-src.tar.gz` and `fbneo-src.meta`: the exact FinalBurn Neo source and its sha256 (below).
- `gpsp-<commit>.tar.gz` and the mGBA commit in `mgba-<commit>.meta`, with their patches, as
  slot ships them.
- `exfatprogs-<version>.tar.gz` and `exfatprogs-GPL-2.0.txt`: the GPL-2.0 source and licence of
  `System/fsck.exfat`, which upstream slot ships for its SD card repair (SELECT+START), as slot ships them.

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

> snes9x, snes9x2005_plus, Genesis Plus GX, PicoDrive and FinalBurn Neo are licensed for non-commercial
> use only and are not GPL. This release includes them, with their licences in
> System/licenses/snes9x-LICENSE.txt, System/licenses/snes9x2005-LICENSE.txt,
> System/licenses/genesis_plus_gx-LICENSE.txt, System/licenses/picodrive-LICENSE.txt and
> System/licenses/fbneo-LICENSE.txt. Do not sell this zip or bundle it with anything that is sold. This
> project never asks for donations.

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
by `cores/pcsx_rearmed/build.sh` for PlayStation (ADR 0063) and ships with the PS1 platform (patch
`0034-platform-ps1`, issue 58). Its licence, the root `COPYING` of that source copied verbatim and
whole, is `licenses/pcsx_rearmed-GPL-2.0.txt`, which `scripts/dist-device.sh` copies into
`System/licenses/` and `scripts/zip-check.sh` requires and compares byte for byte. The exact source
ships with the core as `pcsx_rearmed-src.tar.gz`, with `pcsx_rearmed-src.meta` recording its sha256.

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

## Beetle PCE Fast (TurboGrafx-16 and PC Engine)

Checked at commit `3f946f277aef3aa99a95551618bbcd1dd2bda0d9` of libretro/beetle-pce-fast-libretro, the
commit `SLOT_PIN` pins as `mednafen_pce_fast_commit` (tarball sha256 `mednafen_pce_fast_tarball_sha256`). It
is built by `cores/mednafen_pce_fast/build.sh` for TurboGrafx-16 and PC Engine HuCards (ADR 0091). It
joined `dist:device` and `zip-check.sh` with the TG16 platform patch (patch 0058, issue 83), and its
licence files moved from `cores/mednafen_pce_fast/` to `licenses/`, which `dist-device.sh` copies whole
into the release:

- `mednafen_pce_fast-GPL-2.0.txt`, the root `COPYING` of that source, copied verbatim and whole. It is
  the GPL version 2 text once. The fork review's remark that the file is "GPLv2 twice plus Xiph BSD"
  describes nelynes' `licenses/pce-GPL-2.0.txt`, not upstream's `COPYING`.
- `mednafen_pce_fast-tremor-BSD.txt`, `mednafen/tremor/COPYING` verbatim: the Xiph.org BSD licence of the
  Tremor Vorbis decoder. The makefile always links Tremor (CD audio), so the binary must carry its notice.

The exact source ships with the core as `mednafen_pce_fast-src.tar.gz`, with `mednafen_pce_fast-src.meta`
## Beetle Cygne (WonderSwan)

Checked at commit `4b01295838ea89e3f1355bbe4cb5cf98aa6108cd` of libretro/beetle-wswan-libretro, the
commit `SLOT_PIN` pins as `mednafen_wswan_commit` (tarball sha256 `mednafen_wswan_tarball_sha256`).
It is built by `cores/mednafen_wswan/build.sh` for WonderSwan and WonderSwan Color (ADR 0092) and
ships from the WonderSwan platform patch (issue 93, patch 0065) in `dist:device`, checked by
`zip-check.sh`. Its licence, the root `COPYING` of that source copied verbatim and whole, is
`licenses/mednafen_wswan-GPL-2.0.txt` (`dist-device.sh` copies every file in `licenses/` into the
release). The exact source ships as `mednafen_wswan-src.tar.gz`, with `mednafen_wswan-src.meta`
recording its sha256.

**The combined core we ship is GPL-3.0-or-later.** Every licensed file permits it, as below.

- The Mednafen files say "Mednafen - Multi-system Emulator", GPL. `README.md` has no licence line. The
  sound buffer is Shay Green's Blip_Buffer.
- Scope of the counts: the 96 `.c`, `.h` and `.cpp` files under `mednafen/` plus `libretro.c`,
  `libretro_core_options.h` and `libretro_core_options_intl.h` at the root, 99 files. The fork review
  (docs/research/fork-nelynes.md) counted 100 with the same exclusions (libretro-common, deps, intl);
  the 38 or-later count matches, the headerless count is 31 here against its 29.
  - 38 say "any later version": 36 are GPL-2.0-or-later (the CD ECC files `lec.c`, `galois.c`,
    `l-ec.c` and `recover-raw.c` among them, and `libretro.c`, whose Mednafen block starts at line
    587), `mednafen/sound/Blip_Buffer.c` is LGPL-2.1-or-later, and `mednafen/msvc_compat.h` is
    GPL-3.0-or-later (RetroArch's, compiled only for MSVC).
  - The 31 files of `mednafen/tremor/` are Xiph.org BSD ("governed by a BSD-style source license
    included with this source", the licence file above).
  - No file says version 2 only.
  - Command, run in the unpacked source root: `{ find mednafen -type f \( -name '*.c' -o -name '*.h'
    -o -name '*.cpp' \); ls *.c *.h; } | xargs grep -l -i 'any later version' | wc -l`.
- **Headerless files, a judgement.** 31 of the 99 have no licence text in their first 60 lines. They
  are listed in `licenses/mednafen_pce_fast-headerless-files.txt` with the command that
  produced the list. They include most of the `mednafen/pce_fast/` headers. `libretro.c` is on the list
  too, because its GPL-2.0-or-later block is past line 60; the other 30 have no licence text anywhere.
  We treat them as covered by `COPYING`. That is a judgement, not a quote.
- `deps/` holds four bundled libraries, **not compiled** because the build sets `HAVE_CHD=0`. They ship
  only inside the source tarball, each with its own notice there:
  - `deps/zlib-1.2.11`: the zlib licence (Jean-loup Gailly and Mark Adler);
  - `deps/lzma-19.00`: public domain (Igor Pavlov), `deps/lzma-19.00/LICENSE`;
  - `deps/zstd`: dual BSD-3-Clause or GPL-2.0 at the recipient's choice (`deps/zstd/LICENSE` and
    `COPYING`). We take the BSD terms, so it is not a GPL-2.0-only file;
  - `deps/libchdr`: BSD-3-Clause (Romain Tisserand), `deps/libchdr/LICENSE.txt`.
- `libretro-common/` carries the RetroArch team's MIT text in 56 of its 61 `.c` and `.h` files. The
  other five are `include/compat/zlib.h`, `zconf.h` and `zutil.h` (zlib's, unused with `HAVE_CHD=0`),
  `include/compat/ifaddrs.h` and `include/compat/msvc/stdint.h`; none of them is compiled on unix or
  osx. Every object linked from it by the pinned build is MIT:
  - `streams/file_stream`, `file_stream_transforms`, `vfs/vfs_implementation`, `file/file_path`,
    `file/retro_dirent`, `lists/string_list`, `lists/dir_list` and `time/rtime`;
  - `string/stdstring`, `encodings/encoding_utf`, `encodings/encoding_crc32` and `memmap/memalign`;
  - `compat/fopen_utf8`, `compat_strl`, `compat_snprintf`, `compat_posix_string` and `compat_strcasestr`.
- `intl/` is Python tooling for core option translations, not built.
- Every one of those terms permits combining with a GPL-3.0-or-later program.
- The core is all C, but the makefile links with `$(CXX)` and `-lrt`. The device build links
  `-static-libstdc++ -static-libgcc -Wl,--as-needed` and binds `powf` to `GLIBC_2.17`
  (`cores/mednafen_pce_fast/glibc-2.17.h`). It needs only `libc.so.6` and `libm.so.6` at GLIBC_2.17
  or older, which `task core:device:mednafen_pce_fast` checks.
- No BIOS is shipped or needed for HuCards. CD system cards are out of scope.

The build recipe facts (the core, `make platform=unix`, `-mcpu=cortex-a53`, the commit) come from
nelynes/slotPlus ([92b7022](https://github.com/nelynes/slotPlus/commit/92b7022), GPL-3.0) and are
credited in the commit that added the build. `HAVE_CDROM=0`, `HAVE_CHD=0`, the link flags and the
`powf` binding are ours.
- `COPYING` is the GNU GPL version 2 text. `readme.md` has no licence line. The WonderSwan files
  derive from Cygne by Dox; the CPU is Bryan McPhail's NEC V30MZ emulator; the sound buffer is Shay
  Green's Blip_Buffer.
- Scope of the counts: the 32 `.c` and `.h` files under `mednafen/` plus `libretro.c`,
  `libretro_core_options.h` and `libretro_core_options_intl.h` at the root, 35 files (the same scope
  as docs/research/fork-nelynes.md).
  - 12 say "any later version". 10 are GPL-2.0-or-later, `libretro.c` among them (its notice is at
    line 385). `mednafen/sound/Blip_Buffer.c` is LGPL-2.1-or-later. `mednafen/msvc_compat.h` is the
    RetroArch team's GPL-3.0-or-later; no file includes it and it is not compiled.
  - No file says version 2 only: every file that says "version 2 of the License" also says "any
    later version", and none says "only".
  - Command, run in the unpacked source root: `{ find mednafen -type f \( -name '*.c' -o -name '*.h'
    -o -name '*.cpp' \); ls *.c *.h; } | xargs grep -l -i 'any later version' | wc -l`.
- **Headerless files, a judgement.** 24 of the 35 have no licence text in their first 60 lines. They
  are listed in `licenses/mednafen_wswan-headerless-files.txt` with the command that
  produced the list. Two of them do carry a notice further down or in other words:
  - `libretro.c` is GPL-2.0-or-later (line 385);
  - `mednafen/wswan/v30mz.c` says "This NEC V30MZ emulator may be used for purposes both commercial
    and noncommercial if you give the author, Bryan McPhail, a small credit somewhere (such as in the
    documentation for an executable package)". That is a permissive grant with an attribution
    request, which a GPL-3.0-or-later work can honour (section 7(b)); this section is that credit,
    and the release notes repeat it when the core ships.

  The other 22 (`mednafen/wswan/interrupt.c`, `mednafen/mempatcher.c` and 20 headers) we treat as
  covered by `COPYING`. That is a judgement, not a quote.
- `libretro-common/` is the RetroArch team's MIT text. The objects linked from it by the pinned
  `Makefile` build are `compat/compat_strl` and `compat/compat_snprintf` only, both with that MIT
  header.
- Every one of those terms permits combining with a GPL-3.0-or-later program.
- The core is plain C (`SOURCES_CXX` is empty, the link driver is `$(CC)`). The device build needs
  only `libc.so.6` at GLIBC_2.17 or older, which `task core:device:mednafen_wswan` checks.
- No BIOS is shipped or needed. The core boots the cart's reset vector directly.

The build recipe facts (the core, `make platform=unix`, `-mcpu=cortex-a53`, the commit) come from
nelynes/slotPlus ([273ded9](https://github.com/nelynes/slotPlus/commit/273ded9), GPL-3.0) and are
credited in the commit that added the build.

## Beetle Lynx (Atari Lynx)

Checked at commit `fcdefcfb3c11d6d2e71be076a5d3df2e88ab73ed` of libretro/beetle-lynx-libretro, the
commit `SLOT_PIN` pins as `mednafen_lynx_commit` (tarball sha256 `mednafen_lynx_tarball_sha256`). It
is built by `cores/mednafen_lynx/build.sh` for Atari Lynx (ADR 0093) and ships through `dist:device`
and `zip-check.sh` since the Lynx platform patches (0071 on). Its licence texts are in `licenses/`,
which `dist-device.sh` copies whole into the release:

- `mednafen_lynx-GPL-2.0.txt`, the root `COPYING` of that source, verbatim and whole;
- `mednafen_lynx-Handy-zlib.txt`, `mednafen/lynx/license.txt` verbatim: the zlib licence of Handy
  (Copyright (c) 2004 K. Wilkins). nelynes/slotPlus ships only a GPL-2.0 text for this core, which
  leaves the zlib notice out; its condition 3 ("This notice may not be removed") needs it shipped.

The exact source ships with the core as `mednafen_lynx-src.tar.gz`, with `mednafen_lynx-src.meta`
recording its sha256.

**The combined core we ship is GPL-3.0-or-later.** Every licensed file permits it, as below.

- Scope of the counts: the 47 `.c`, `.h` and `.cpp` files under `mednafen/` plus `libretro.cpp`,
  `libretro_core_options.h`, `libretro_core_options_intl.h`, `scrc32.c` and `scrc32.h` at the root,
  52 files.
  - 9 say "any later version": 6 GPL-2.0-or-later (Mednafen's `endian.cpp`, `file.c`,
    `mempatcher.cpp`, `settings.cpp`, `state.cpp` and Shay Green's `sound/Stereo_Buffer.cpp`), 2
    GPL-3.0-or-later (`msvc_compat.h` and `include/boolean.h`, Hans-Kristian Arntzen) and 1
    LGPL-2.1-or-later (`sound/Blip_Buffer.cpp`).
  - 20 carry the zlib licence of Handy: every file under `mednafen/lynx/` except `c65c02.cpp`.
  - `include/retro_inline.h` is the RetroArch team's MIT text.
  - `md5.cpp` says "licensed under the GPL" and `include/blip/Stereo_Buffer.h` says "GNU GPL
    license", neither with a version.
  - No file says version 2 only.
  - Command, run in the unpacked source root: `{ find mednafen -type f \( -name '*.c' -o -name '*.h'
    -o -name '*.cpp' \); ls libretro.cpp libretro_core_options.h libretro_core_options_intl.h
    scrc32.c scrc32.h; } | xargs grep -l -i 'any later version' | wc -l` (9), and the same with
    `'Permission is granted to anyone to use this software'` (20).
- **Headerless files, a judgement.** 20 of the 52 have no licence text in their first 60 lines. They
  are listed in `licenses/mednafen_lynx-headerless-files.txt` with the command that
  produced the list. They include `libretro.cpp` (the glue), `mednafen/lynx/c65c02.cpp` (Handy's
  CPU, zlib by origin) and `scrc32.c` (a CRC-32 table). We treat them as covered by `COPYING`.
  That is a judgement, not a quote.
- `libretro-common/`: every object the pinned `Makefile` links carries the RetroArch team's MIT text:
  `streams/file_stream`, `vfs/vfs_implementation`, `file/file_path`, `time/rtime`,
  `string/stdstring`, `encodings/encoding_utf` and `compat/fopen_utf8`, `compat_posix_string`,
  `compat_snprintf`, `compat_strl` and `compat_strcasestr`.
- Every one of those terms permits combining with a GPL-3.0-or-later program.
- The emulator and glue are C++. The device build links the C++ runtime statically and needs only
  glibc at 2.17 or older, which `task core:device:mednafen_lynx` checks.
- **No BIOS is shipped, fetched or needed to build.** Running a cart needs the player's own
  `lynxboot.img` in `BIOS/` (ADR 0093, issue 104). The tests read one only from `SLOT_LYNX_BIOS`.

The build recipe facts (the core, `make platform=unix`, `-mcpu=cortex-a53`, the commit) come from
nelynes/slotPlus ([749523c](https://github.com/nelynes/slotPlus/commit/749523c), GPL-3.0) and are
credited in the commit that added the build.

## Beetle NeoPop (NeoGeo Pocket)

Checked at commit `a50d5ac288a81f2104ddf43195a4efdd15c72227` of libretro/beetle-ngp-libretro, the
commit `SLOT_PIN` pins as `mednafen_ngp_commit` (tarball sha256 `mednafen_ngp_tarball_sha256`). It is
built by `cores/mednafen_ngp/build.sh` for NeoGeo Pocket and Pocket Color (ADR 0090) and ships from
the NGP platform patch on (issue 72): `dist:device` copies it and `zip-check.sh` checks it. Its licence,
the root `COPYING` of that source copied verbatim and whole, is `licenses/mednafen_ngp-GPL-2.0.txt`.
The exact source ships with the core as `mednafen_ngp-src.tar.gz`, with `mednafen_ngp-src.meta`
recording its sha256.

**The combined core we ship is GPL-3.0-or-later.** Every licensed file permits it, as below.

- `COPYING` is the GNU GPL version 2 text. `readme.md` has no licence line. The NeoPop files say
  "Copyright (c) 2001-2002 by neopop_uk"; the Z80 is Philip Kendall's FUSE core; the sound buffers
  are Shay Green's Blip_Buffer.
- Scope of the counts: the 68 `.c`, `.h` and `.cpp` files under `mednafen/` plus `libretro.c` and
  `libretro_core_options.h` at the root, 70 files (the same scope as docs/research/fork-nelynes.md).
  - 49 say "any later version". 47 are GPL-2.0-or-later, `libretro.c` among them.
    `mednafen/sound/Blip_Buffer.cpp` and `mednafen/ngp/T6W28_Apu.cpp` are LGPL-2.1-or-later.
  - `mednafen/include/blip/Stereo_Buffer.h` says "GNU GPL license" with no version (Shay Green).
  - No file says version 2 only and none says version 3.
  - Command, run in the unpacked source root: `{ find mednafen -type f \( -name '*.c' -o -name
    '*.h' -o -name '*.cpp' \); ls libretro.c libretro_core_options.h; } | xargs grep -l -i 'any
    later version' | wc -l`.
- **Headerless files, a judgement.** 20 of the 70 have no licence text in their first 60 lines. They
  are listed in `licenses/mednafen_ngp-headerless-files.txt` with the command that
  produced the list, and they include `mednafen/ngp/system.c` (the flash file I/O) and
  `mednafen/ngp/sound.cpp`. We treat them as covered by `COPYING`. That is a judgement, not a quote.
- `libretro-common/` carries the RetroArch team's MIT text in 36 of its 38 `.c` and `.h` files. The
  other two, `include/compat/ifaddrs.h` and `include/compat/msvc/stdint.h`, are not compiled on
  unix or osx. The objects linked come from the pinned `Makefile` build:
  - `streams/file_stream`, `vfs/vfs_implementation`, `file/file_path` and `time/rtime`;
  - `string/stdstring` and `encodings/encoding_utf`;
  - `compat/fopen_utf8`, `compat_strl`, `compat_snprintf` and `compat_posix_string`.
- Every one of those terms permits combining with a GPL-3.0-or-later program.
- The core is C with five C++ files (Blip_Buffer, Stereo_Buffer, the T6W28 APU, sound and the
  memory patcher). The device build links the C++ runtime statically and needs only `libc.so.6` at
  GLIBC_2.17 or older, which `task core:device:mednafen_ngp` checks.
- No BIOS is shipped or needed. NeoPop installs its own HLE BIOS.

The build recipe facts (the core, `make platform=unix`, `-mcpu=cortex-a53`, the commit) come from
nelynes/slotPlus ([a8eae4c](https://github.com/nelynes/slotPlus/commit/a8eae4c), GPL-3.0) and are
credited in the commit that added the build.

## PicoDrive (Sega 32X)

Checked at commit `1890c2932234c9d30f4cd3851d02228baae8f09e` of libretro/picodrive, the commit `SLOT_PIN`
pins as `picodrive_commit`, with the three submodules its libretro build compiles, each pinned at the
commit the core records: digital-sound-antiques/emu2413 `a2dfc20ff507e4fd075cd325620bcea655e2c1f7`,
mackron/dr_libs `dd762b861ecadf5ddd5fb03e9ca1db6707b54fbb` and irixxxx/libpicofe
`9ed5822606dd7ff20a782a882e8fd611cb53ba88` (`picodrive_<name>_commit` and
`picodrive_<name>_tarball_sha256`). It is built by `cores/picodrive/build.sh` for the 32X (ADR 0096). Its
licence, the root `COPYING` of that source copied verbatim and whole, is `licenses/picodrive-LICENSE.txt`.
The exact sources ship with the core as `picodrive-src.tar.gz` and the three
`picodrive-<name>-src.tar.gz`, with `picodrive-src.meta` recording the commits and sha256s.
`scripts/dist-device.sh` copies them and every file in `licenses/` into `System/licenses/`, and
`scripts/zip-check.sh` requires them, checks each tarball against `SLOT_PIN` and compares each licence
file byte for byte.

**PicoDrive is not free software and is not GPL-compatible**, like snes9x and Genesis Plus GX. Its
`COPYING` is the same MAME-style text as Genesis Plus GX's, quoted:

- "Redistributions may not be sold, nor may they be used in a commercial product or activity."
- "Redistributions that are modified from the original source must include the complete source code,
  including the source code for all components used by a binary built from the modified sources." We
  build the pinned source unmodified, submodules included, and ship all four tarballs anyway.
- "Redistributions must reproduce the above copyright notice", which is why the whole file ships.

What is compiled into `picodrive_libretro.so` (the 103 sources of the device link line, at the pin):

- 42 carry the line "This work is licensed under the terms of MAME license" (notaz, irixxxx and
  others), the licence above. None says GPL: no source on the link line carries "General Public".
- 23 have no licence text in their first 60 lines, listed in `licenses/picodrive-headerless-files.txt`
  with the command that produced the list: the FAME 68000 and CZ80 Z80 cores, the SN76496 and YM2413
  glue, the Sega CD MegaSD, VGM and patch code, `mp3_sync.c`, `unzip.c` and Tremor. We treat the
  non-Tremor files as covered by the project `COPYING`; a judgement, not a quote.
- Tremor (`platform/common/tremor`, Xiph): BSD-style, its `COPYING` verbatim in
  `licenses/picodrive-tremor-BSD.txt`, which the binary must carry.
- emu2413 (Mitsutaka Okazaki): MIT, its `LICENSE` verbatim in `licenses/picodrive-emu2413-MIT.txt`.
- dr_mp3 (`dr_libs`): public domain or MIT-0, the choice stated in the file.
- zlib (Jean-loup Gailly and Mark Adler) and `libretro-common` (the RetroArch team's MIT text).
- libpicofe: only `plat.h` (a pixel-format macro) is included; libpicofe is GPL-2.0-or-later,
  LGPL-2.1-or-later or the MAME licence at the user's option (its README), and the MAME option is the
  one that matches the core.

The plugin boundary stance is the one for snes9x above: a separate program loaded by `dlopen` across
the libretro C ABI, the zip an aggregate of separate works. This is our reading, not legal advice. The
core is plain C and links only `libc` and `libm` on the device (`log` and `pow` bound to their GLIBC_2.17
versions, ADR 0096). The notice under snes9x names PicoDrive, and the release terms do not change: the
zip is never sold and never carries a donation or sponsor link.
## Stella 2014 (Atari 2600)

Checked at commit `7d1361e407e63f29e52892655069e5fb4096e691` of libretro/stella2014-libretro, the
commit `SLOT_PIN` pins as `stella2014_commit` (tarball sha256 `stella2014_tarball_sha256`). It is
built by `cores/stella2014/build.sh` for the Atari 2600 (ADR 0095). It joined `dist:device` and
`zip-check.sh` with the platform patch (`0100-platform-atari`, issue 156), and its licence texts moved
from `cores/stella2014/` to `licenses/`, which `dist-device.sh` copies whole into the release, beside
the pinned source tarball:

- `stella2014-GPL-2.0.txt`, the tree's `stella/license.txt` verbatim and whole (the GPL-2.0 text);
- `stella2014-Copyright-3.9.3.txt`, Stella's own `Copyright.txt` at tag `release-3.9.3`
  (stella-emu/stella, tag object `8ab9090`), verbatim: "either version 2 of the License, or any later
  version", with the BSD notice for Aaron Giles' MAME-derived portions. The libretro fork is Stella
  3.9.3 (`STELLA_VERSION` in `stella/src/common/Version.hxx`) and does not carry this file, so we ship
  it.

**The combined core we will ship is GPL-3.0-or-later**, as below. This rests on the upstream grant,
not on any file in the tree; if that reading were ever disputed, current libretro Stella (whose own
`Copyright.txt` makes the same grant) is the fallback (ADR 0095).

- Scope of the counts: the 195 `.c`, `.h`, `.cxx`, `.hxx` and `.ci` files under `stella/` plus
  `libretro.cxx`, `libretro_core_options.h` and `libretro_core_options_intl.h` at the root, 198 files.
  - 187 carry the Stella header ("Copyright (c) 1995-2014 by Bradford W. Mott, Stephen Anthony and
    the Stella Team. See the file "License.txt""). None says "any later version" and none says
    version 2 only.
  - Of those, `stella/src/common/Array.hxx` is "Based on code from ScummVM" (GPL-2.0-or-later
    upstream) and `stella/src/emucore/MD5.cxx` is "derived from the RSA Data Security, Inc. MD5
    Message-Digest Algorithm", whose notice permits derived works that say so (it does).
  - Command, run in the unpacked source root: `{ find stella -type f \( -name '*.c' -o -name '*.h' -o
    -name '*.cxx' -o -name '*.hxx' -o -name '*.ci' \); ls libretro.cxx libretro_core_options.h
    libretro_core_options_intl.h; } | xargs grep -l 'See the file "License.txt"' | wc -l` (187), and
    the same with `-i 'any later version'` (0).
- **Headerless files, a judgement.** 11 have no licence text in their first 60 lines, listed in
  `cores/stella2014/stella2014-headerless-files.txt` with the command. They are the libretro glue
  (`libretro.cxx` and the two options headers), `stella/stubs/Stubs.hxx`, the CDF and BUS cart types
  backported from Stella 7 (GPL-2.0-or-later by Stella's current `Copyright.txt`) and the C
  Thumbulator, a reshaping of the original that Stella 3.9.3 marks "Code is public domain and used
  with the author's consent" (David Welch, modified by Fred Quimby). We treat them as covered by the
  GPL text and the 3.9.3 grant. That is a judgement, not a quote.
- `libretro-common/`: the objects the pinned `Makefile.common` links (`compat/*`, `encodings`,
  `file/file_path` and `file_path_io`, `time/rtime`, `streams/file_stream` and `_transforms`,
  `string/stdstring`, `vfs/vfs_implementation`) carry the RetroArch team's MIT text. The zlib headers
  under `include/compat` are not compiled in.
- The test programs under `test/` are not built into the core.
- The core is C++. The device build links the C++ runtime statically and needs only `libc.so.6` at
  GLIBC_2.17, which `task core:device:stella2014` checks.
- No BIOS exists for the 2600; nothing is fetched.

## ProSystem (Atari 7800)

Checked at commit `8a88014287c7a01cd568067e5a557d0a2b2a051f` of libretro/prosystem-libretro, the
commit `SLOT_PIN` pins as `prosystem_commit` (tarball sha256 `prosystem_tarball_sha256`). It is built
by `cores/prosystem/build.sh` for the Atari 7800 (ADR 0095) and joined `dist:device` and
`zip-check.sh` with the platform patch (`0100-platform-atari`, issue 163); its licence texts are in
`licenses/` and ship with the core and its pinned source:

- `prosystem-GPL-2.0.txt`, the root `License.txt` verbatim and whole;
- `prosystem-CoreTone-zlib.txt`, `bupboop/License.txt` verbatim: the zlib licence of CoreTone
  (Copyright (C) 2015 - 2016 Osman Celimli). Its condition 3 ("This notice may not be removed") needs
  it shipped.

**The combined core we will ship is GPL-3.0-or-later.** Every licensed file permits it.

- Scope of the counts: the 44 `.c` and `.h` files under `core/` and `bupboop/` (every
  source the pinned `Makefile.common` compiles there, and their headers).
  - 31 say "any later version": Greg Stanton's GPL-2.0-or-later header (2005), on every emulator file.
  - 9 are CoreTone's (`bupboop/types.h` and `bupboop/coretone/*`, Osman Celimli): `coretone.c` holds
    the zlib text, 7 point to it ("see copyright notice in coretone.c") and `types.h` points to a
    `bupboop.h` the tree lacks; `bupboop/License.txt` is the same zlib text.
  - `core/boolean.h` is the RetroArch team's MIT text.
  - `core/Tia.*` and `core/Pokey.*` also carry Ron Fries' TiaSound and PokeySound notice (1997):
    version 2 of the GNU Library General Public License, whose section 3 lets a copy be put under the
    ordinary GPL version 2 or any later version, so it combines with GPL-3.0-or-later. Its legend
    ("Any permitted reproduction of these routines ... must bear this legend") stays in the shipped
    source tarball.
  - No file in either core carries a non-commercial term: `grep -ril 'commercial'` over both trees
    finds only the GPL texts themselves and the zlib text ("including commercial applications").
  - No file says version 2 only. `License.txt`'s "any later version" lines are the GPL's own
    how-to-apply appendix, not a grant; the grant is the file headers.
  - Command, run in the unpacked source root: `find core bupboop -type f \( -name '*.c' -o -name
    '*.h' \) | xargs grep -il 'any later version' | wc -l` (31), and the same with `-l 'Osman
    Celimli'` (9).
- **Headerless files, a judgement.** 3: `core/libretro.c` (the glue) and the two options headers,
  listed in `cores/prosystem/prosystem-headerless-files.txt`. We treat them as covered by
  `License.txt`.
- `libretro-common/`: the linked objects carry the RetroArch team's MIT text.
- The core is plain C. CoreTone calls `pow`, so the device build force-includes
  `cores/prosystem/glibc-2.17.h` (one `.symver` line, ours) to bind `pow@GLIBC_2.17`; the `.so` needs
  `libc.so.6` and `libm.so.6` at GLIBC_2.17, which `task core:device:prosystem` checks.
- **No BIOS is shipped, fetched or needed to build.** The core uses the player's own
  `7800 BIOS (U).rom` or `(E)` from `BIOS/` only when the BIOS row is On (issue 165). The tests read
  one only from `SLOT_7800_BIOS`.

## FinalBurn Neo (Neo Geo, CPS1 and CPS2)

Checked at commit `2dbbac7623fbae1c7894a6437769e8a3adb78610` of libretro/FBNeo (its master on 2026-10-19),
the commit `SLOT_PIN` pins as `fbneo_commit`, archive sha256 `fbneo_tarball_sha256`. It is built by
`cores/fbneo/build.sh` for the Neo Geo, CPS1 and CPS2 shelves (ADR 0097), with only the Neo Geo and CPS
drivers: `cores/fbneo/Makefile.arcade` includes FBNeo's own `Makefile.neogeo` and `Makefile.cps12` subset
makefiles together, and the build regenerates FBNeo's driver list for those sources with FBNeo's own
perl script. That makefile and `cores/fbneo/glibc-2.17.h` are the only build inputs that are not in the
archive; both are in this repository, so they ship inside `slot-nes-snes-src-<release>.tar.gz`. No
FBNeo source file is changed. The exact source ships with the core as `fbneo-src.tar.gz`, with
`fbneo-src.meta` recording its commit and sha256.

FBNeo's licence is `src/license.txt` of that source (the root `LICENSE.md` only points to it), copied
verbatim and whole to `licenses/fbneo-LICENSE.txt`. It names the MAME licence by URL at MAME commit
`5cef4e1f91010f0d573bbd662208979fa39e73ec` and says FB Neo is also subject to it; that file,
`docs/mamelicense.txt` at that commit, is `licenses/fbneo-MAME-license.txt`. Both ship in
`System/licenses/`, and `scripts/zip-check.sh` requires them.

**FinalBurn Neo is not free software and is not GPL-compatible**, like snes9x, Genesis Plus GX and
PicoDrive. Its terms, quoted from `src/license.txt`:

- "You may not sell, lease, rent or otherwise seek to gain monetary profit from FB Neo;"
- "You must make public any changes you make to the source code;" We change none, and the makefile
  that picks the drivers is public in this repository and in every release's source tarball.
- "You must include, verbatim, the full text of this license;" `licenses/fbneo-LICENSE.txt`.
- "You may not distribute FB Neo with ROM images unless you have the legal right to distribute them;"
  No ROM, BIOS or romset is shipped or fetched. Tests use zero-filled zips with the dat's member names.
- "You may not ask for donations to support your work on any project that uses the FB Neo source code."
  **This project asks for no donations, anywhere, ever**: no link asking for a donation or a sponsor for
  this project or its maintainer (donation, sponsor, Patreon, Ko-fi, PayPal) in the repository, the
  README, the release notes or the zip, and no `.github/FUNDING.yml`. This is a standing rule (ADR 0097),
  not only for releases that carry FBNeo. `tools/hacks.json` names where third-party ROM hacks are
  published, and one author publishes his on a Ko-fi shop: that is the download source of his patch, not
  a request for this project; the file is a tool input that reaches the zip only inside the source tarball.

The MAME licence adds: "Redistributions may not be sold, nor may they be used in a commercial product or
activity", the complete source for a modified build, and the copyright notice reproduced.

What is compiled into `fbneo_libretro.so` (the 152 sources of the device link line, at the pin):

- 81 have no licence or copyright text in their first 60 lines, listed in
  `licenses/fbneo-headerless-files.txt` with the command that produced the list. They are FB Neo's own
  files (the Neo Geo and CPS drivers, the burner and the libretro glue); we treat them as covered by
  `src/license.txt`, a judgement, not a quote.
- None says GPL. zstd (`dep/libs/zstd/zstddeclib.c`) is BSD or GPLv2 at the user's choice; we take BSD.
- The Musashi 68000 core (Karl Stenerud, version 3.32) "may be freely used for non-commercial purpooses
  as long as this copyright notice remains unaltered in the source code and any binary files containing
  this code in compiled form": the same non-commercial line as the rest, and the notice is a string the
  core keeps in the binary. The Z80, Yamaha FM, MSM5205 and MSM6295 cores carry their MAME notices; the
  licence above covers them.
- zlib (the zlib licence), the LZMA SDK and lib7z (public domain), libchdr (BSD-3-Clause, Aaron Giles),
  libretro-common (MIT). The notices whose terms ask to travel with a binary (libchdr, Musashi, zlib,
  libretro-common) are copied verbatim from the pinned source into `licenses/fbneo-notices.txt`.
- The µGUI module and its Source Han Sans font (FBNeo's on-screen messages): µGUI's own terms and the
  SIL Open Font License 1.1, both in `src/burner/libretro/deps/ugui/LICENSE.md`, copied verbatim to
  `licenses/fbneo-ugui-OFL.txt`, which the binary must carry under the OFL.

The plugin boundary stance is the one for snes9x above: a separate program loaded by `dlopen` across the
libretro C ABI, the zip an aggregate of separate works. This is our reading, not legal advice. On the
device the core links the C++ runtime statically (`-static-libstdc++ -static-libgcc`) and binds `log` and
`pow` to their GLIBC_2.17 versions (`cores/fbneo/glibc-2.17.h`), so it needs only `libc`, `libm` and
`libpthread`. The notice under snes9x names FinalBurn Neo, and the release terms do not change: the zip
is never sold and never carries a donation or sponsor link.

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

Patch `0034-platform-ps1` draws on three of them. The playlist rules (a `.cue` or `.m3u` hides the
discs it names, `(Disc N)` files become one game with a generated playlist) follow AaronC1990/tray
and oauramos/omega-zero, and its test fixture, a PS-X EXE and an ISO9660 disc generated in the test,
is ported from bently0602/slot's `crates/slot-retro/tests/pcsx.rs`. All three are GPL-3.0 and are
credited in the patch commit.

Patch `0035-ps1-options` answers pcsx_rearmed's declared option defaults, as oauramos/omega-zero
does, after AaronC1990/tray found that pcsx renders on the emu thread unless its threaded-rendering
key is answered. Both are credited in the patch commit.

Patch `0043-pal-pacing` paces a core at its own fps, as oauramos/omega-zero does (`Pace`, 726cc34).
The 2 fps window around 60 and the period-based `core_hz` follow cloudwithax/unslot
([4cf8468](https://github.com/cloudwithax/unslot/commit/4cf8468)), and the fractional frames-owed
carry follows nelynes/slotPlus ([0848fcb](https://github.com/nelynes/slotPlus/commit/0848fcb),
[b264635](https://github.com/nelynes/slotPlus/commit/b264635)). All three are GPL-3.0, the code is
reimplemented, and all three are credited in the patch commit.

Patch `0044-flush-sav-without-state` takes the generic half of suprsomething/slot.advance commit
dbbadae (writing the battery save when the core gives no state), patch `0045-shelf-face-restock`
reimplements the stale face check, the face-keeping restock and the selected-index lookups of
marghost/slot_modded commit 88af60a, and patch `0046-switcher-up-down` takes Up and Down in the save
state switcher from suprsomething/slot.advance commit 2fe9876. Both forks are GPL-3.0 and are
credited in the patch commits.

Patch `0048-logo-label` adds `crates/slot-ui/examples/logo_label.rs`, a port of cloudwithax/unslot's
`crates/slot-ui/src/scraped.rs` ([0b0f3a3](https://github.com/cloudwithax/unslot/commit/0b0f3a307da447d8d048425ab8e70a9fc4aeab43),
GPL-3.0), which is itself a Rust port of the Logo Only style of Brandon Kowalski's Cart Studio
(github.com/BrandonKowalski/slot-cart-studio, GPL-3.0-or-later). Both are credited in the file and the
patch commit. No logo ships: `tools/fetch-labels.py` downloads them at user time.

Patch `0049-battery-low` reimplements the Battery Low banners of marghost/slot_modded commit
[1706a16](https://github.com/marghost/slot_modded/commit/1706a16), which adapts
suprsomething/slot.advance commit [d495461](https://github.com/suprsomething/slot.advance/commit/d495461),
and ports marghost's tests for them. Patch `0050-doze-rest` reimplements the standby loop of
marghost/slot_modded commit [b1f9e24](https://github.com/marghost/slot_modded/commit/b1f9e24),
which adapts suprsomething/slot.advance commit
[bf810b6](https://github.com/suprsomething/slot.advance/commit/bf810b6). Patch `0051-silent-start-hud`
follows jgraving/slot commit [12f7b3a](https://github.com/jgraving/slot/commit/12f7b3a). All three forks are GPL-3.0 and are
credited in the patch commits.

Patch `0052-crash-guard` takes only the idea of oauramos/omega-zero commit be6eb11 (keep a game whose
start crashed on the shelf, with a notice); no code is copied. Credited in the patch commit and ADR 0084.

Patch `0053-cpu-governor` follows pvaibhav/slot commits
[ad7ce10](https://github.com/pvaibhav/slot/commit/ad7ce10) and
[320ac44](https://github.com/pvaibhav/slot/commit/320ac44) (schedutil written to every cpufreq policy),
as a user option rather than a launcher change; no code was copied. Patch `0054-fast-shelf-scroll`
reimplements the fast scroll of marghost/slot_modded commits
[efe32cd](https://github.com/marghost/slot_modded/commit/efe32cd) and
[0fce212](https://github.com/marghost/slot_modded/commit/0fce212), which adapt stevolarn/slot; the
leash and the non-blocking face loader are ours. All three forks are GPL-3.0 and are credited in the
patch commits.

Patch `0055-four-three` takes the idea of a 4:3 picture from cloudwithax/unslot
([4cf8468](https://github.com/cloudwithax/unslot/commit/4cf8468)), reimplemented as a source rect
on our fixed canvas. Patch `0056-headless-egl` follows the surfaceless Mesa EGL render surface of
cloudwithax/unslot ([42ef0f8](https://github.com/cloudwithax/unslot/commit/42ef0f8)) and
suprsomething/slot.advance ([e761baa](https://github.com/suprsomething/slot.advance/commit/e761baa)),
reimplemented. Both forks are GPL-3.0 and are credited in the patch commits.

Patch `0057-tg16-core-tests` builds its synthetic HuCard (one 8 KB bank, the reset vector at the last two
bytes pointing at $E000, and a `bra *` spin) after nelynes/slotPlus's `crates/slot/tests/pce_core.rs`
([92b7022](https://github.com/nelynes/slotPlus/commit/92b7022), GPL-3.0), the same recipe as
cloudwithax/unslot's `crates/slot-retro/tests/systems.rs`
([00296a5](https://github.com/cloudwithax/unslot/commit/00296a5), GPL-3.0). The palette code is new. Both forks
are credited in the patch commit. The TG16 Screen page (patch `0058-platform-tg16`), the pad layout
(`0061-tg16-input`) and the HuCard drawing (`0062-tg16-carts`, after `assets/src/carts.py`) follow
nelynes/slotPlus [92b7022](https://github.com/nelynes/slotPlus/commit/92b7022) (GPL-3.0); each is
reimplemented and credited in its patch commit.
Patch `0064-wswan-core-tests` builds its synthetic WonderSwan Color cart with the reset jump in the
last 16 bytes landing at F000:0000 after cloudwithax/unslot's `crates/slot-retro/tests/systems.rs`
([00296a5](https://github.com/cloudwithax/unslot/commit/00296a5), GPL-3.0). The footer, paint and
save RAM code is new. The fork is credited in the patch commit.

Patch `0070-lynx-core-tests` boots its synthetic Atari Lynx cart through the public cc65 encrypted
boot loader (`libsrc/lynx/bootldr.s`, Karri Kaksonen, 2011, cc65's zlib licence): 52 bytes of data in
a test, never shipped. The test approach follows nelynes/slotPlus's Lynx work
([749523c](https://github.com/nelynes/slotPlus/commit/749523c), GPL-3.0); the carts, the homebrew
image and the checks are new. The fork is credited in the patch commit.

The Lynx platform patches reimplement ideas from nelynes/slotPlus (GPL-3.0), credited in each patch
commit: the shelf shape ([749523c](https://github.com/nelynes/slotPlus/commit/749523c), patch
`0071-platform-lynx`), measuring the rate from the sound
([0848fcb](https://github.com/nelynes/slotPlus/commit/0848fcb),
[b264635](https://github.com/nelynes/slotPlus/commit/b264635), patch `0075-lynx-pacing`), the
by-title rotation list, the override file and the turned play
([d7d0e74](https://github.com/nelynes/slotPlus/commit/d7d0e74),
[185257a](https://github.com/nelynes/slotPlus/commit/185257a), patch `0077-lynx-rotation`) and the
flat card ([98419f4](https://github.com/nelynes/slotPlus/commit/98419f4), patch `0078-lynx-carts`,
drawn by our own generator, no asset copied).

Patch `0080-ngp-core-tests` builds its synthetic NeoGeo Pocket Color cart (the SNK header, the start
address at 0x1c, the colour byte at 0x23 and a `jr t,-2` spin) after nelynes/slotPlus's
`crates/slot/tests/ngp_core.rs` ([a8eae4c](https://github.com/nelynes/slotPlus/commit/a8eae4c),
GPL-3.0). The paint and flash-command code is new. The fork is credited in the patch commit.
Patch `0099-atari-core-tests` builds its Atari 2600 test cart in the shape of the ROM in
stella2014-libretro's own `test/determinism_harness.c` (a VSYNC kernel writing COLUBK), and its 7800
cart from the register map in ProSystem's `core/Equates.h`. Both are generated bytes in a test, never
shipped; the code and the checks are new.
