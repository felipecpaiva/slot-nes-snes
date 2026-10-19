#!/bin/sh
# libretro/beetle-wswan-libretro (Beetle Cygne, WonderSwan and WonderSwan Color): the shared steps are in
# cores/lib.sh. GPL-2.0-or-later with MIT libretro-common parts, see LICENSING.md. The makefile is the
# repo root Makefile and names the output mednafen_wswan_libretro.<ext>, so that is the core name here
# (SLOT_PIN keys mednafen_wswan_*); its option keys start wswan_. The recipe (make platform=unix,
# -mcpu=cortex-a53) follows nelynes/slotPlus 273ded9 (ADR 0092).
core=mednafen_wswan repo=beetle-wswan-libretro makefile= subdir=
. "$(dirname "$0")/../lib.sh"
core_main "$@"
