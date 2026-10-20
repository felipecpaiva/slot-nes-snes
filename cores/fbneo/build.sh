#!/bin/sh
# libretro/FBNeo (FinalBurn Neo, Neo Geo, CPS1 and CPS2 arcade sets): the shared steps are in cores/lib.sh.
# Non-commercial licence that also forbids asking for donations, see LICENSING.md (ADR 0099).
core=fbneo repo=FBNeo makefile=Makefile subdir=src/burner/libretro
# Only the Neo Geo and CPS drivers are built: cores/fbneo/Makefile.arcade includes FBNeo's own neogeo and
# cps12 subset makefiles together, and REGEN_HEADERS=1 has FBNeo's perl scripts write the driver list for
# exactly those sources. TARGET_NAME keeps the output named fbneo_libretro.<ext>. The path is relative to
# the makefile's directory, build/fbneo-<host|device>/FBNeo-<commit>/src/burner/libretro, so the recipe
# stamp is the same inside and outside the device container.
make_args="SUBSET=arcade TARGET_NAME=fbneo REGEN_HEADERS=1 INCLUDED_MAKEFILE=../../../../../../cores/fbneo/Makefile.arcade"
# The burner is C++: link the C++ runtime in, the stock OS is not known to have libstdc++.so.6.
device_ldflags="-static-libstdc++ -static-libgcc"
# The sound code calls log and pow, which glibc 2.29 re-versioned: bind the GLIBC_2.17 symbols (see the
# header).
device_include=cores/fbneo/glibc-2.17.h
. "$(dirname "$0")/../lib.sh"
core_main "$@"
