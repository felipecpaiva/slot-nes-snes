#!/bin/sh
# libretro/pcsx_rearmed (PlayStation): the shared steps are in cores/lib.sh. GPL-2.0-or-later, see
# LICENSING.md. HAVE_PHYSICAL_CDROM=0 turns off the unix default of 1 (osx already sets 0), and
# BUILTIN_GPU=neon and HAVE_CHD=1 pin what the makefile picks for arm64 today. DYNAREC is left to the
# makefile: ari64 on aarch64 unix, 0 (the interpreter) on osx, which a command line value would override.
core=pcsx_rearmed repo=pcsx_rearmed makefile=Makefile.libretro subdir=
make_args="HAVE_PHYSICAL_CDROM=0 BUILTIN_GPU=neon HAVE_CHD=1"
. "$(dirname "$0")/../lib.sh"
core_main "$@"
