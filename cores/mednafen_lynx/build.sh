#!/bin/sh
# libretro/beetle-lynx-libretro (Beetle Lynx, Atari Lynx): the shared steps are in cores/lib.sh.
# GPL-2.0-or-later Mednafen glue with zlib Handy files, see LICENSING.md. The makefile is the repo
# root Makefile and names the output mednafen_lynx_libretro.<ext>, so that is the core name here
# (SLOT_PIN keys mednafen_lynx_*). The recipe (make platform=unix, -mcpu=cortex-a53) follows
# nelynes/slotPlus 749523c (ADR 0093).
core=mednafen_lynx repo=beetle-lynx-libretro makefile= subdir=
# The emulator and glue are C++ (only file.c, scrc32.c and libretro-common are C): link the C++ runtime in, the stock OS is not known to have
# libstdc++.so.6 (same as snes9x, nestopia and mednafen_ngp).
device_ldflags="-static-libstdc++ -static-libgcc"
. "$(dirname "$0")/../lib.sh"
core_main "$@"
