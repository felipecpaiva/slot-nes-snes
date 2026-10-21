#!/bin/sh
# libretro/beetle-pce-fast-libretro (Beetle PCE Fast, TurboGrafx-16 and PC Engine HuCards and CDs): the shared steps
# are in cores/lib.sh. GPL-2.0-or-later with BSD, zlib and public-domain parts, see LICENSING.md. The
# makefile is the repo root Makefile and names the output mednafen_pce_fast_libretro.<ext>, so that is the
# core name here (SLOT_PIN keys mednafen_pce_fast_*). The recipe (make platform=unix, -mcpu=cortex-a53)
# follows nelynes/slotPlus 92b7022 (ADR 0091).
core=mednafen_pce_fast repo=beetle-pce-fast-libretro makefile= subdir=
# HAVE_CDROM=0: the unix platform turns on physical CD drive access on Linux (the pcsx_rearmed
# HAVE_PHYSICAL_CDROM=0 precedent). HAVE_CHD=1: PC Engine CD discs are CHD (ADR 0104), so libchdr, lzma,
# zstd, zlib and dr_flac are compiled in; their notices are in licenses/mednafen_pce_fast-chd-notices.txt.
make_args="HAVE_CDROM=0 HAVE_CHD=1"
# All C, but the makefile links with $(CXX) and adds -lrt: link the C++ runtime in, and let --as-needed
# drop librt and libstdc++ so NEEDED stays inside the glibc set the stock OS has.
device_ldflags="-static-libstdc++ -static-libgcc -Wl,--as-needed"
# psg.c calls powf, which glibc 2.27 re-versioned: bind the GLIBC_2.17 symbol (see the header).
device_include=cores/mednafen_pce_fast/glibc-2.17.h
# The CHD build compiles deps/zlib-1.2.11, whose zutil.h reads the macOS SDK's TARGET_OS_MAC as classic Mac
# OS and defines fdopen to NULL, which breaks stdio.h. Defining fdopen as itself skips that block.
host_cflags="-Dfdopen=fdopen"
. "$(dirname "$0")/../lib.sh"
core_main "$@"
