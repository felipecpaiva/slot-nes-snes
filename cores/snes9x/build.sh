#!/bin/sh
# libretro/snes9x: the shared fetch, verify, stamp and build steps are in cores/lib.sh.
# Non-commercial licence, see LICENSING.md.
core=snes9x repo=snes9x makefile= subdir=libretro
. "$(dirname "$0")/../lib.sh"
core_main "$@"
