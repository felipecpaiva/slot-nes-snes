#!/bin/sh
# libretro-fceumm: the shared fetch, verify, stamp and build steps are in cores/lib.sh.
core=fceumm repo=libretro-fceumm makefile=Makefile.libretro subdir=
. "$(dirname "$0")/../lib.sh"
core_main "$@"
