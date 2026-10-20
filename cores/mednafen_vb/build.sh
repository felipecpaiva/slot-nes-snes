#!/bin/sh
# libretro/beetle-vb-libretro (Beetle VB, Nintendo Virtual Boy): the shared steps are in cores/lib.sh.
# GPL-2.0-or-later with MIT libretro-common parts, see LICENSING.md. The makefile is the repo root
# Makefile and names the output mednafen_vb_libretro.<ext>, so that is the core name here (SLOT_PIN keys
# mednafen_vb_*); its option keys start vb_. The recipe (make platform=unix, -mcpu=cortex-a53) is the
# Beetle PCE Fast one (ADR 0091, ADR 0097).
core=mednafen_vb repo=beetle-vb-libretro makefile= subdir=
# HAVE_VR=0: the VR view (libretro_vr.cpp) needs OpenGL; it is the makefile's default, stated so a
# changed default cannot pull GL into the core.
make_args="HAVE_VR=0"
# The V810 is C++: link the C++ runtime in, and let --as-needed drop what is not used, so NEEDED stays
# inside the glibc set the stock OS has.
device_ldflags="-static-libstdc++ -static-libgcc -Wl,--as-needed"
# vip.c calls pow, which glibc 2.29 re-versioned: bind the GLIBC_2.17 symbol (see the header).
device_include=cores/mednafen_vb/glibc-2.17.h
. "$(dirname "$0")/../lib.sh"
core_main "$@"
