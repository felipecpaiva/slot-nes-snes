/* Force-included into every device compile of Beetle VB (device_include in build.sh).
 * The VIP colour tables call pow (mednafen/vb/vip.c MakeColorLUT), and glibc 2.29 gave pow a new default
 * version (pow@GLIBC_2.29, the same maths without the old SVID error handling). The build image has glibc
 * 2.31, so the core would need GLIBC_2.29, newer than the 2.17 that scripts/lib.sh needs_old_glibc_only
 * allows. aarch64 glibc still exports pow@GLIBC_2.17; bind that one, as Beetle PCE Fast does powf. */
__asm__(".symver pow,pow@GLIBC_2.17");
