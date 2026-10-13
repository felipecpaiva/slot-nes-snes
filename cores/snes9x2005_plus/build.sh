#!/bin/sh
# libretro/snes9x2005 built with USE_BLARGG_APU=1: the shared steps are in cores/lib.sh.
# Non-commercial licence (the snes9x terms), see LICENSING.md. The makefile is at the repo root.
# With USE_BLARGG_APU=1 the makefile itself names the output snes9x2005_plus_libretro.<ext>, which is
# the name lib.sh copies, so no rename is needed (the build fails loudly if a pin ever changes that).
core=snes9x2005_plus repo=snes9x2005 makefile= subdir= make_args=USE_BLARGG_APU=1
. "$(dirname "$0")/../lib.sh"
core_main "$@"
