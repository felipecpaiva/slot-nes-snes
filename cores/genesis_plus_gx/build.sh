#!/bin/sh
# libretro/Genesis-Plus-GX (Mega Drive, Master System, Game Gear): the shared steps are in
# cores/lib.sh. Non-commercial licence (Charles MacDonald, Eke-Eke, MAME portions), see LICENSING.md.
# The makefile is Makefile.libretro at the repo root and names the output genesis_plus_gx_libretro.<ext>.
core=genesis_plus_gx repo=Genesis-Plus-GX makefile=Makefile.libretro subdir=
. "$(dirname "$0")/../lib.sh"
core_main "$@"
