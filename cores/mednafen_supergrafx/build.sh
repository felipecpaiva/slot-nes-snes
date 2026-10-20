#!/bin/sh
# libretro/beetle-supergrafx-libretro (Beetle SuperGrafx, PC Engine SuperGrafx HuCards): the shared steps
# are in cores/lib.sh. GPL-2.0-or-later with BSD, MIT and public-domain parts, see LICENSING.md. The makefile
# is the repo root Makefile and names the output mednafen_supergrafx_libretro.<ext>, so that is the core
# name here (SLOT_PIN keys mednafen_supergrafx_*); its option keys start sgx_. The recipe (make
# platform=unix, -mcpu=cortex-a53) is the Beetle PCE Fast one (ADR 0091, ADR 0101).
core=mednafen_supergrafx repo=beetle-supergrafx-libretro makefile= subdir=
# HAVE_CDROM=0: the unix platform turns on physical CD drive access on Linux (the pcsx_rearmed
# HAVE_PHYSICAL_CDROM=0 precedent). HAVE_CHD=0: the makefile's default is 1, and CD images are out of
# scope (ADR 0101), so the rchd reader and its codecs stay out of the binary; they are still in the source
# tarball that ships beside it.
make_args="HAVE_CDROM=0 HAVE_CHD=0"
# The core is C++ and the makefile adds -lrt: link the C++ runtime in, and let --as-needed drop librt,
# so NEEDED stays inside the glibc set the stock OS has.
device_ldflags="-static-libstdc++ -static-libgcc -Wl,--as-needed"
# psg.cpp calls powf, which glibc 2.27 re-versioned: bind the GLIBC_2.17 symbol (see the header).
device_include=cores/mednafen_supergrafx/glibc-2.17.h
. "$(dirname "$0")/../lib.sh"
core_main "$@"
