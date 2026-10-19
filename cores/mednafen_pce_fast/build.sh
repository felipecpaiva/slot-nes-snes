#!/bin/sh
# libretro/beetle-pce-fast-libretro (Beetle PCE Fast, TurboGrafx-16 and PC Engine HuCards): the shared steps
# are in cores/lib.sh. GPL-2.0-or-later with BSD, zlib and public-domain parts, see LICENSING.md. The
# makefile is the repo root Makefile and names the output mednafen_pce_fast_libretro.<ext>, so that is the
# core name here (SLOT_PIN keys mednafen_pce_fast_*). The recipe (make platform=unix, -mcpu=cortex-a53)
# follows nelynes/slotPlus 92b7022 (ADR 0091).
core=mednafen_pce_fast repo=beetle-pce-fast-libretro makefile= subdir=
# HAVE_CDROM=0: the unix platform turns on physical CD drive access on Linux (the pcsx_rearmed
# HAVE_PHYSICAL_CDROM=0 precedent). HAVE_CHD=0: CD images are out of scope (ADR 0091), so libchdr, lzma,
# zstd and zlib stay out of the binary; they are still in the source tarball that ships beside it.
make_args="HAVE_CDROM=0 HAVE_CHD=0"
# All C, but the makefile links with $(CXX) and adds -lrt: link the C++ runtime in, and let --as-needed
# drop librt and libstdc++ so NEEDED stays inside the glibc set the stock OS has.
device_ldflags="-static-libstdc++ -static-libgcc -Wl,--as-needed"
# psg.c calls powf, which glibc 2.27 re-versioned: bind the GLIBC_2.17 symbol (see the header).
device_include=cores/mednafen_pce_fast/glibc-2.17.h
. "$(dirname "$0")/../lib.sh"
core_main "$@"
