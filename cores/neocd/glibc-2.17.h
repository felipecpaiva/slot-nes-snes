/* Force-included into every device compile of NeoCD (device_include in build.sh).
 * The YM2610 tables and the libretro-common audio readers call exp, logf and pow, which glibc 2.27 and
 * 2.29 gave new default versions (the same maths without the old SVID error handling). The build image
 * has glibc 2.31, so the core would need GLIBC_2.29, newer than the 2.17 that scripts/lib.sh
 * needs_old_glibc_only allows. aarch64 glibc still exports all three at GLIBC_2.17; bind those, as Beetle
 * PCE Fast does powf. */
__asm__(".symver exp,exp@GLIBC_2.17");
__asm__(".symver logf,logf@GLIBC_2.17");
__asm__(".symver pow,pow@GLIBC_2.17");
