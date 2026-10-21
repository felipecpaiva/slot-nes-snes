/* Force-included into every device compile of FAKE-08 (device_include in build.sh).
 * The synth and z8lua's maths call powf, exp2f and pow, which glibc 2.27 and 2.29 gave new default
 * versions (the same maths without the old SVID error handling). The build image has glibc 2.31, so the
 * core would need GLIBC_2.29, newer than the 2.17 that scripts/lib.sh needs_old_glibc_only allows.
 * aarch64 glibc still exports all three at GLIBC_2.17; bind those, as Beetle PCE Fast does powf. */
__asm__(".symver powf,powf@GLIBC_2.17");
__asm__(".symver exp2f,exp2f@GLIBC_2.17");
__asm__(".symver pow,pow@GLIBC_2.17");
