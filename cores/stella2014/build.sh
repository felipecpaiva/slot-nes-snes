#!/bin/sh
# libretro/stella2014-libretro (Stella 3.9.3 for libretro, Atari 2600): the shared steps are in
# cores/lib.sh. GPL-2.0-or-later by Stella's own grant, see LICENSING.md. The makefile is the repo root
# Makefile and names the output stella2014_libretro.<ext>, so that is the core name here (SLOT_PIN keys
# stella2014_*). Recipe: make platform=unix, -mcpu=cortex-a53 (ADR 0095).
core=stella2014 repo=stella2014-libretro makefile= subdir=
# Stella is C++: link the C++ runtime in, the stock OS is not known to have libstdc++.so.6 (same as
# snes9x, nestopia and the Beetle cores).
device_ldflags="-static-libstdc++ -static-libgcc"
. "$(dirname "$0")/../lib.sh"
core_main "$@"
