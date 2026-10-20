/* Force-included into every device compile of ProSystem (device_include in build.sh).
 * CoreTone (bupboop/coretone/music.c) calls pow for its note table, and glibc 2.29 gave pow a new
 * default version (pow@GLIBC_2.29, the same maths without the old SVID error handling). The build
 * image has glibc 2.31, so the core would need GLIBC_2.29, newer than the 2.17 that scripts/lib.sh
 * needs_old_glibc_only allows. aarch64 glibc still exports pow@GLIBC_2.17; bind that one. */
__asm__(".symver pow,pow@GLIBC_2.17");
