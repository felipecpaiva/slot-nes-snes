---
title: "Build Beetle VB from a pinned commit for host and device with the VR view off and record its licence"
phase: 16
area: cores
type: feature
size: S
depends_on: [153-vb-tracking]
---

## Why
No libretro core but Beetle VB runs the Virtual Boy. Its recent VR view needs OpenGL, which the device build must not link.

## Scope
- [x] `cores/mednafen_vb/build.sh` (`HAVE_VR=0`), `SLOT_PIN` `mednafen_vb_commit` d5ae54c and the archive sha256.
- [x] `task core:mednafen_vb:src`, `:host` and `core:device:mednafen_vb` (NEEDED libc and libm at GLIBC_2.17 or older).
- [x] LICENSING.md section, `licenses/mednafen_vb-GPL-2.0.txt` and `mednafen_vb-headerless-files.txt`; dist-device.sh, zip-check.sh, run-tests.sh and bench-device.sh list the core.

## Tests
| ID | File | Asserts |
|---|---|---|
| C1 | `vb_core.rs` | the generated cart boots with no BIOS at 50.27 fps, 384x224, sound, states, 64 KB cart RAM, declared options |

## Edge cases
| Case | Expected handling |
|---|---|
| The makefile default for HAVE_VR changes | `make_args` says HAVE_VR=0 |
| A pin bump re-versions a libm symbol | `task core:device:mednafen_vb` fails |

## Acceptance
- [x] C1 passes with SLOT_REQUIRE_CORES=1; the device core needs only libc and libm.

## Device check (RG34XXSP)
Issue 162.

## References
- ADR 0097; docs/cart-art/VB.md
