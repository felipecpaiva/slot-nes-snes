---
title: "Build Beetle SuperGrafx from a pinned commit for host and device without CD images and record its licence"
phase: 20
area: cores
type: feature
size: S
depends_on: [209-sgx-tracking]
---

## Why
Beetle PCE Fast has no SuperGrafx code. Beetle SuperGrafx is the same Mednafen pce_fast tree with the second VDC, the VPC and 32 KB of work RAM.

## Scope
- [x] `cores/mednafen_supergrafx/build.sh` (`HAVE_CDROM=0 HAVE_CHD=0`, the makefile defaults CHD on), `glibc-2.17.h` for `powf`, `SLOT_PIN` `mednafen_supergrafx_commit` 9c11dcd and the archive sha256.
- [x] `task core:mednafen_supergrafx:src`, `:host` and `core:device:mednafen_supergrafx` (only GLIBC_2.17 symbols).
- [x] LICENSING.md section, `licenses/mednafen_supergrafx-GPL-2.0.txt`, `-tremor-BSD.txt` and `-headerless-files.txt`; dist-device.sh, zip-check.sh, run-tests.sh and bench-device.sh list the core.

## Tests
| ID | File | Asserts |
|---|---|---|
| C1 | `sgx_core.rs` | the generated HuCard boots with no BIOS at 59.82 fps and 44.1 kHz, 256x240 on the 360x240 canvas, states, 2 KB HUBM backup RAM |
| C2 | `sgx_core.rs` | `.sgx` gives 32 KB of work RAM; a `.pce` card gives 8 KB with `sgx_forcesgx` disabled and 32 KB with it enabled |

## Edge cases
| Case | Expected handling |
|---|---|
| The makefile default for HAVE_CHD stays 1 | `make_args` says HAVE_CHD=0 |
| A pin bump re-versions a libm symbol | `task core:device:mednafen_supergrafx` fails |

## Acceptance
- [x] C1 and C2 pass with SLOT_REQUIRE_CORES=1; the device core needs only GLIBC_2.17 symbols.

## Device check (RG34XXSP)
Issue 214.

## References
- ADR 0103; docs/cart-art/SGX.md
