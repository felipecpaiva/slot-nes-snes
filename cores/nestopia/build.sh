#!/bin/sh
# libretro/nestopia: the shared fetch, verify, stamp and build steps are in cores/lib.sh.
# GPL-2.0-or-later, see LICENSING.md. The makefile is in libretro/, device platform=unix, host platform=osx.
core=nestopia repo=nestopia makefile= subdir=libretro
# C++ core: link the runtime in, the stock OS is not known to have libstdc++.so.6 (same as snes9x).
device_ldflags="-static-libstdc++ -static-libgcc"
. "$(dirname "$0")/../lib.sh"
core_main "$@"
