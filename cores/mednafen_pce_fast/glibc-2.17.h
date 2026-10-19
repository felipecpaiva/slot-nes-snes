/* Force-included into every device compile of Beetle PCE Fast (device_include in build.sh).
 * The PSG volume table calls powf, and glibc 2.27 gave powf a new default version (powf@GLIBC_2.27,
 * the same maths without the old SVID error handling). The build image has glibc 2.31, so the core would
 * need GLIBC_2.27, newer than the 2.17 that scripts/lib.sh needs_old_glibc_only allows. aarch64 glibc
 * still exports powf@GLIBC_2.17; bind that one. */
__asm__(".symver powf,powf@GLIBC_2.17");
