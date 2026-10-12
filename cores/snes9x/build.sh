#!/bin/sh
# libretro/snes9x: the shared fetch, verify, stamp and build steps are in cores/lib.sh.
# Non-commercial licence, see LICENSING.md.
core=snes9x repo=snes9x makefile= subdir=libretro
# C++ core: link the runtime in, the stock OS is not known to have libstdc++.so.6 (the upstream
# classic_armv7_a7 and classic_armv8_a35 targets do the same).
device_ldflags="-static-libstdc++ -static-libgcc"
. "$(dirname "$0")/../lib.sh"
core_main "$@"
