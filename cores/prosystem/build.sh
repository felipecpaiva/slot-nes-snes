#!/bin/sh
# libretro/prosystem-libretro (ProSystem, Atari 7800): the shared steps are in cores/lib.sh.
# GPL-2.0-or-later with the zlib CoreTone files, see LICENSING.md. The makefile is the repo root
# Makefile and names the output prosystem_libretro.<ext>, so that is the core name here (SLOT_PIN keys
# prosystem_*). Recipe: make platform=unix, -mcpu=cortex-a53 (ADR 0095). Plain C, so no C++ runtime.
core=prosystem repo=prosystem-libretro makefile= subdir=
# CoreTone calls pow, which glibc 2.29 re-versioned: bind the GLIBC_2.17 one (the header says why).
device_include=cores/prosystem/glibc-2.17.h
. "$(dirname "$0")/../lib.sh"
core_main "$@"
