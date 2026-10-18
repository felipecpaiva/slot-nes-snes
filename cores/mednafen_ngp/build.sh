#!/bin/sh
# libretro/beetle-ngp-libretro (Beetle NeoPop, NeoGeo Pocket and Pocket Color): the shared steps are in
# cores/lib.sh. GPL-2.0-or-later with LGPL-2.1-or-later parts, see LICENSING.md. The makefile is the
# repo root Makefile and names the output mednafen_ngp_libretro.<ext>, so that is the core name here
# (SLOT_PIN keys mednafen_ngp_*). The recipe (make platform=unix, -mcpu=cortex-a53) follows
# nelynes/slotPlus a8eae4c (ADR 0090).
core=mednafen_ngp repo=beetle-ngp-libretro makefile= subdir=
# Five .cpp files (Blip_Buffer, the T6W28 APU, sound): link the C++ runtime in, the stock OS is not
# known to have libstdc++.so.6 (same as snes9x and nestopia).
device_ldflags="-static-libstdc++ -static-libgcc"
. "$(dirname "$0")/../lib.sh"
core_main "$@"
