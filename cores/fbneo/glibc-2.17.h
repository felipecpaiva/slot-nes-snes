/* Force-included into every device compile of FBNeo (device_include in build.sh).
 * The sound code calls log and pow, and glibc 2.29 gave both a new default version (log@GLIBC_2.29 and
 * pow@GLIBC_2.29, the same maths without the old SVID error handling). The build image has glibc 2.31,
 * so the core would need GLIBC_2.29, newer than the 2.17 that scripts/lib.sh needs_old_glibc_only
 * allows. aarch64 glibc still exports both at GLIBC_2.17; bind those, as Beetle PCE Fast does powf. */
__asm__(".symver log,log@GLIBC_2.17");
__asm__(".symver pow,pow@GLIBC_2.17");
