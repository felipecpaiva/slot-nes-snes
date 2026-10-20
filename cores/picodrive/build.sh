#!/bin/sh
# libretro/picodrive (PicoDrive, Sega 32X): the shared steps are in cores/lib.sh. Non-commercial
# licence, see LICENSING.md (ADR 0096). Makefile.libretro names the output picodrive_libretro.<ext>.
core=picodrive repo=picodrive makefile=Makefile.libretro subdir=
# The GitHub archive has no submodules. The libretro build compiles emu2413 (pico/sound/ym2413.c) and
# dr_mp3 (platform/common/mp3_drmp3.c), and libretro.c includes platform/libpicofe/plat.h, so those
# three ship as their own pinned tarballs. cyclone (ARM32 only) and libchdr (Sega CD, out of scope) are
# not built and not shipped.
modules="emu2413:pico/sound/emu2413:digital-sound-antiques/emu2413 dr_libs:platform/common/dr_libs:mackron/dr_libs libpicofe:platform/libpicofe:irixxxx/libpicofe"
# use_libchdr=0: CD images are out of scope (the TG16 HAVE_CHD=0 precedent). PLATFORM_TREMOR=1 and
# PLATFORM_ZLIB=1 pin what the makefile would otherwise pick from the builder's installed headers.
# GIT_REVISION: the makefile asks git, which inside build/ would find this repo's HEAD.
. "$(dirname "$0")/../../SLOT_PIN"
make_args="use_libchdr=0 PLATFORM_TREMOR=1 PLATFORM_ZLIB=1 GIT_REVISION=-$(printf %s "${picodrive_commit:-}" | cut -c1-7)"
# The sound code calls log and pow, which glibc 2.29 re-versioned: bind the GLIBC_2.17 symbols (see the
# header).
device_include=cores/picodrive/glibc-2.17.h
# The makefile builds with -flto, which would put the .symver lines and the calls in different link-time
# partitions; one partition keeps them together.
device_ldflags="-flto-partition=one"
. "$(dirname "$0")/../lib.sh"
core_main "$@"
