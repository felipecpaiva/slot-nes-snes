#!/bin/sh
# jtothebell/fake-08 (FAKE-08, PICO-8 carts): the shared steps are in cores/lib.sh. MIT, with z8lua (MIT
# and WTFPL) as a submodule the GitHub archive leaves out, see LICENSING.md (ADR 0101). PICO-8 itself is
# Lexaloffle's and is never shipped. The makefile is platform/libretro/Makefile and names the output
# fake08_libretro.<ext>, so that is the core name here (SLOT_PIN keys fake08_*); its option keys start
# fake08_.
core=fake08 owner=jtothebell repo=fake-08 makefile= subdir=platform/libretro
modules="z8lua:libs/z8lua:jtothebell/z8lua"
# cores/fake08/slot.patch: cartdata files are opened with fopen, not freopen on stderr (which closed
# slot's stderr), written through a synced temp file, flushed once a second when they changed, and the
# pause menu loses the two entries that leave the game for fake-08's own cart browser.
source_patch=cores/fake08/slot.patch
# fake-08 is C++: link the C++ runtime in, and let --as-needed drop what is not used, so NEEDED stays
# inside the glibc set the stock OS has.
device_ldflags="-static-libstdc++ -static-libgcc -Wl,--as-needed"
# The synth and z8lua call powf, exp2f and pow, which glibc 2.27 and 2.29 re-versioned: bind the
# GLIBC_2.17 symbols (see the header).
device_include=cores/fake08/glibc-2.17.h
. "$(dirname "$0")/../lib.sh"
core_main "$@"
