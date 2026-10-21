#!/bin/sh
# libretro/neocd_libretro (NeoCD, Neo Geo CD discs): the shared steps are in cores/lib.sh. LGPL-3.0 with
# BSD, MIT, zlib and public-domain parts vendored under deps/ and src/3rdparty/, see LICENSING.md (ADR 0105).
# The makefile is the repo root Makefile and names the output neocd_libretro.<ext>.
core=neocd repo=neocd_libretro makefile= subdir=
# HAVE_CDROM=0: the unix platform turns on physical CD drive access on Linux (the pcsx_rearmed
# HAVE_PHYSICAL_CDROM=0 precedent); a command-line value overrides the makefile's := assignment.
# USE_LTO=0: the unix platform turns on link-time optimisation, which drops the .symver bindings of the
# device header below, so the core would need GLIBC_2.29.
make_args="HAVE_CDROM=0 USE_LTO=0"
# The core is C++: link the C++ runtime in, the stock OS is not known to have libstdc++.so.6.
device_ldflags="-static-libstdc++ -static-libgcc"
# exp, logf and pow were re-versioned by glibc 2.27 and 2.29: bind the GLIBC_2.17 symbols (see the header).
device_include=cores/neocd/glibc-2.17.h
. "$(dirname "$0")/../lib.sh"
core_main "$@"
